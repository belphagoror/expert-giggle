# SPDX-License-Identifier: Apache-2.0
import sys, json, re, os

import itertools

import unicodedata

def is_nfc(s: str) -> bool:
    return s == unicodedata.normalize("NFC", s)

def rule_unique_ids(findings, doc):
    # beats
    seen = set()
    def check_dup(seq, label):
        dups = []
        for x in seq:
            if x in seen: dups.append(x)
            else: seen.add(x)
        if dups:
            log(findings, SEV_ERROR, f"duplicate {label} ids", {"ids": sorted(set(dups))})
    beat_ids = []
    for b in doc.get("beats") or []:
        if isinstance(b.get("id"), str): beat_ids.append(b["id"])
    bt = doc.get("beats_tbl") or {}
    cols = bt.get("cols") or []
    rows = bt.get("rows") or []
    if cols and rows and "id" in cols:
        idx = cols.index("id")
        for r in rows:
            if isinstance(r[idx], str): beat_ids.append(r[idx])
    check_dup(beat_ids, "beat")
    # chars and ents
    check_dup([c.get("id") for c in doc.get("chars") or [] if isinstance(c.get("id"), str)], "char")
    check_dup([e.get("id") for e in doc.get("ents") or [] if isinstance(e.get("id"), str)], "ent")

def rule_nfc_normalization(findings, doc):
    # IDs and pooled strings should be NFC
    for arr in (doc.get("chars") or []):
        _id = arr.get("id")
        if isinstance(_id, str) and not is_nfc(_id):
            log(findings, SEV_WARN, "char id not NFC-normalized", {"id": _id})
    for arr in (doc.get("ents") or []):
        _id = arr.get("id")
        if isinstance(_id, str) and not is_nfc(_id):
            log(findings, SEV_WARN, "ent id not NFC-normalized", {"id": _id})
    pool = ((doc.get("dict") or {}).get("s") or [])
    for i,s in enumerate(pool):
        if isinstance(s, str) and not is_nfc(s):
            log(findings, SEV_WARN, "pooled string not NFC-normalized", {"index": i})

ALLOWED_LINK_RELS = {"reveals_of","causes","consequence_of","foreshadows","contradicts","parallels"}

ID_CHAR_RE = re.compile(r"^char:[a-z0-9_]+$")
ID_ENT_RE  = re.compile(r"^ent:[a-z0-9_]+$")
ID_BEAT_RE = re.compile(r"^b[0-9]{4,}$")
LANG_RE    = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")

def rule_id_patterns(findings, doc):
    # chars/ents objects
    for arr, regex, label in [(doc.get("chars") or [], ID_CHAR_RE, "char"), (doc.get("ents") or [], ID_ENT_RE, "ent")]:
        for o in arr:
            oid = o.get("id")
            if isinstance(oid, str) and not regex.match(oid):
                log(findings, SEV_ERROR, f"{label} id violates pattern", {"id": oid})
    # beats list objects
    for b in doc.get("beats") or []:
        bid = b.get("id")
        if isinstance(bid, str) and not ID_BEAT_RE.match(bid):
            log(findings, SEV_ERROR, "beat id violates pattern", {"id": bid})
    # lang
    lang = doc.get("lang")
    if lang and not LANG_RE.match(lang):
        log(findings, SEV_ERROR, "lang violates BCP47-lite pattern", {"lang": lang})

def rule_links(findings, doc):
    links = doc.get("links") or []
    if not links: return
    # collect known beat ids
    beat_ids = set()
    for b in doc.get("beats") or []:
        if isinstance(b.get("id"), str): beat_ids.add(b["id"])
    # beats_tbl
    bt = doc.get("beats_tbl") or {}
    cols = bt.get("cols") or []
    rows = bt.get("rows") or []
    if cols and rows:
        try:
            idx = cols.index("id")
            for r in rows:
                v = r[idx]
                if isinstance(v, str): beat_ids.add(v)
        except ValueError:
            pass
    for lk in links:
        if lk.get("src") not in beat_ids or lk.get("tgt") not in beat_ids:
            log(findings, SEV_ERROR, "link references unknown beat id", lk)
        rel = lk.get("rel")
        if isinstance(rel, str) and rel not in ALLOWED_LINK_RELS:
            log(findings, SEV_WARN, "link rel not in allowed set", {"rel": rel})

def rule_l5_coverage_union(findings, doc):
    if doc.get("l") != "L5": return
    tm = doc.get("text_map") or {}
    chunks = {c.get("id"): c.get("len") for c in tm.get("chunks") or [] if c.get("id") and isinstance(c.get("len"), int)}
    spans = tm.get("spans") or []
    # compute union by chunk
    by_chunk = {}
    for s in spans:
        ch = s.get("chunk"); a = s.get("start"); b = s.get("end")
        if ch not in chunks or not isinstance(a, int) or not isinstance(b, int): 
            continue
        L = chunks[ch]
        a = max(0, min(a, L)); b = max(0, min(b, L))
        if b <= a: continue
        by_chunk.setdefault(ch, []).append((a,b))
    covered = 0
    for ch, intervals in by_chunk.items():
        # merge intervals
        intervals.sort()
        cur_a, cur_b = intervals[0]
        for a,b in intervals[1:]:
            if a <= cur_b:
                cur_b = max(cur_b, b)
            else:
                covered += (cur_b - cur_a)
                cur_a, cur_b = a, b
        covered += (cur_b - cur_a)
    total = sum(chunks.values()) or 1
    cov = covered/total
    tol = (tm.get("loss_tolerance") if isinstance(tm.get("loss_tolerance"), (int,float)) else None)
    if tol is None:
        log(findings, SEV_ERROR, "L5 requires text_map.loss_tolerance", {})
        return
    if cov + tol + 1e-9 < 1.0:
        log(findings, SEV_ERROR, f"coverage {cov:.3f} < 1 - loss_tolerance {tol:.3f}", {})
    # encourage storing the computed coverage
    if abs((tm.get("coverage") or 0) - cov) > 0.01:
        log(findings, SEV_WARN, f"text_map.coverage out of sync with computed union {cov:.3f}", {})

def rule_a_schema_version(findings, doc):
    a_schema = doc.get("a_schema")
    try:
        canon = json.load(open(os.path.join(os.path.dirname(__file__), "canonical_verbs.json"), "r", encoding="utf-8"))
        cv_schema = canon.get("schema")
        if a_schema and cv_schema and a_schema != cv_schema:
            log(findings, SEV_WARN, "a_schema does not match validator verbs schema", {"doc": a_schema, "validator": cv_schema})
    except Exception:
        pass


SEV_INFO, SEV_WARN, SEV_ERROR = "INFO","WARN","ERROR"

def log(findings, sev, msg, ctx):
    findings.append({"sev":sev, "msg":msg, "ctx":ctx})

def word_count(s):
    return len([w for w in re.split(r"\s+", s.strip()) if w])

def load_canonical_verbs():
    path = os.path.join(os.path.dirname(__file__), "canonical_verbs.json")
    try:
        return set(json.load(open(path,"r",encoding="utf-8"))["verbs"])
    except Exception:
        return set()

def rule_main_profile(findings, doc):
    level = doc.get("l")
    if level not in ("L2","L3"):
        return
    verbs = load_canonical_verbs()
    if "beats_tbl" in doc and doc.get("beats"):
        log(findings, SEV_WARN, "beats present alongside beats_tbl; omit beats in L3", {})
    for b in doc.get("beats", []):
        s = b.get("evt")
        if isinstance(s, str) and word_count(s) > 12:
            log(findings, SEV_ERROR, f"evt exceeds 12-word cap at level {level}", {"beat":b.get("id")})
        a = (b.get("actn") or {}).get("a")
        if a and verbs and a not in verbs:
            log(findings, SEV_ERROR, f"actn.a not in canonical verb set: {a}", {"beat": b.get("id")})

def rule_l4_caps(findings, doc):
    if doc.get("l") != "L4":
        return
    themes = doc.get("themes") or []
    if len(themes) > 8:
        log(findings, SEV_ERROR, f"L4 themes exceed cap (8): {len(themes)}", {})
    quotes = doc.get("quotes") or []
    if len(quotes) > 40:
        log(findings, SEV_ERROR, f"L4 quotes exceed cap (40): {len(quotes)}", {})
    pool_q = (doc.get("dict") or {}).get("q") or []
    for q in quotes:
        qsi = q.get("q_si")
        if isinstance(qsi, int) and 0 <= qsi < len(pool_q):
            s = pool_q[qsi]
            if isinstance(s, str) and word_count(s) > 12:
                log(findings, SEV_ERROR, "L4 quote exceeds 12-word cap", q)

def rule_l5_coverage(findings, doc):
    if doc.get("l") != "L5":
        return
    tm = doc.get("text_map") or {}
    cov = tm.get("coverage"); tol = tm.get("loss_tolerance")
    if cov is None or tol is None:
        log(findings, SEV_ERROR, "L5 requires text_map.coverage and text_map.loss_tolerance", {}); return
    if not (0 <= cov <= 1 and 0 <= tol <= 1):
        log(findings, SEV_ERROR, "coverage/loss_tolerance must be in [0,1]", {})
    if cov < (1 - tol):
        log(findings, SEV_ERROR, f"coverage {cov} < 1 - loss_tolerance {1-tol}", {})

def rule_pool_threshold(findings, doc):
    pool = (doc.get("dict") or {}).get("s") or []
    if not pool: return
    refs = [0]*len(pool)
    def bump(i):
        if isinstance(i, int) and 0 <= i < len(pool):
            refs[i]+=1
    for b in doc.get("beats", []):
        bump(b.get("evt_si"))
    for arr_name in ("chars","ents","mysteries"):
        for o in doc.get(arr_name, []) or []:
            bump(o.get("n_si") if arr_name!="mysteries" else o.get("q_si"))
    few = [i for i,c in enumerate(refs) if c==1]
    if few:
        log(findings, SEV_WARN, f"{len(few)} pooled strings referenced only once (consider not pooling one-offs)", {})

def rule_beats_tbl_columns(findings, doc):
    tbl = doc.get("beats_tbl")
    if not isinstance(tbl, dict): return
    cols = tbl.get("cols")
    want = ["id","act","evt_si","p","a","u","i","loc","when"]
    if cols != want:
        log(findings, SEV_ERROR, f"beats_tbl.cols must exactly equal {want}, got {cols}", {})

def analyze(findings, doc):
    pass

def validate(paths):
    ok = True
    for path in paths:
        findings = []
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        rule_main_profile(findings, doc)
        rule_l4_caps(findings, doc)
        rule_l5_coverage(findings, doc)
        rule_l5_coverage_union(findings, doc)
        rule_pool_threshold(findings, doc)
        rule_beats_tbl_columns(findings, doc)
        errs = [x for x in findings if x["sev"]=="ERROR"]
        print(f"# {path}")
        for x in findings:
            print(f"- {x['sev']}: {x['msg']} :: {x['ctx']}")
        if errs: ok = False
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sbf_validate.py <file1.json> [file2.json ...]"); sys.exit(2)
    sys.exit(validate(sys.argv[1:]))
