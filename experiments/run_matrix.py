
# SPDX-License-Identifier: Apache-2.0
import sys, re, os, json, pathlib, itertools, math, hashlib, gzip
from collections import Counter

def sentences(text):
    # naive sentence splitter
    # split on .!? followed by space and capital or newline
    parts = re.split(r"(?<=[\.!?])\s+(?=[A-Z\"'])", text)
    return [s.strip() for s in parts if s.strip()]

def build_pool(items, k):
    c = Counter(items)
    pool = [s for s,n in c.items() if n >= k]
    return pool, c

def idx_or_none(pool, s):
    try: return pool.index(s)
    except ValueError: return None

def make_l2(doc_id, title, sents, k, gloss_policy):
    pool, counts = build_pool(sents, k)
    beats = []
    for i, s in enumerate(sents, start=1):
        b = {"id": f"b{i:05d}", "act": 1}
        if gloss_policy == "evt_si_only":
            j = idx_or_none(pool, s)
            if j is not None:
                b["evt_si"] = j
        elif gloss_policy == "evt_when_leq_10":
            wc = len(s.split())
            if wc <= 10: b["evt"] = s
            else:
                j = idx_or_none(pool, s)
                if j is not None: b["evt_si"] = j
        else: # leq_12
            wc = len(s.split())
            if wc <= 12: b["evt"] = s
            else:
                j = idx_or_none(pool, s)
                if j is not None: b["evt_si"] = j
        beats.append(b)
    d = {"spec":"SBF v0.1","spec_version":"0.1.2","l":"L2","t":title, "dict":{"s": pool}, "beats": beats}
    return d

def make_l3(title, l2):
    # convert to beats_tbl
    cols = ["id","act","evt_si","p","a","u","i","loc","when"]
    rows = []
    for b in l2.get("beats", []):
        rows.append([b["id"], b.get("act",1), b.get("evt_si"), None, None, None, None, None, None])
    d = {"spec":"SBF v0.1","spec_version":"0.1.2","l":"L3","t":title, "dict": l2.get("dict", {}),
         "beats_tbl": {"cols": cols, "rows": rows}}
    return d

def make_l5(title, text, l5_chunk):
    # chunk raw text and map first N beats to spans
    chunks = []
    spans = []
    # chunk by fixed size
    i = 0; cid = 1
    while i < len(text):
        part = text[i:i+l5_chunk]
        cid_str = f"c{cid:03d}"
        chunks.append({"id": cid_str, "hash": f"sha256:{hashlib.sha256(part.encode('utf-8')).hexdigest()}", "len": len(part)})
        i += l5_chunk; cid += 1
    # simple coverage: map first M spans to the start of each chunk
    covered = 0
    for c in chunks:
        spans.append({"beat": "b00001", "chunk": c["id"], "start": 0, "end": min(48, c["len"])})
        covered += min(48, c["len"])
    total = sum(c["len"] for c in chunks) or 1
    cov = round(covered/total, 3)
    d = {"spec":"SBF v0.1","spec_version":"0.1.2","l":"L5","t":title,
         "text_map":{"chunks":chunks,"spans":spans,"coverage":cov,"loss_tolerance": max(0.0, round(1.0-cov+0.002,3))}}
    return d

def size_metrics(obj):
    raw = json.dumps(obj, ensure_ascii=False, separators=(",",":")).encode("utf-8")
    pretty = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    gz = gzip.compress(raw)
    return {"bytes_raw": len(raw), "bytes_pretty": len(pretty), "bytes_gzip": len(gz)}

def main():
    import argparse, yaml
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", required=True)
    ap.add_argument("--index", default="corpus/index.json")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()
    params = yaml.safe_load(open(args.params, "r", encoding="utf-8"))
    index = json.load(open(args.index, "r", encoding="utf-8"))
    os.makedirs(args.out, exist_ok=True)
    results_path = os.path.join("experiments","results.jsonl")
    outf = open(results_path, "w", encoding="utf-8")
    for it in index:
        title = it["id"].replace("_"," ")
        text = open(it["file_txt"],"r",encoding="utf-8").read()
        sents = sentences(text)
        for k in params["k_gloss"]:
            for gp in params["gloss_policy"]:
                # L2
                l2 = make_l2(it["id"], title, sents, k, gp)
                m = size_metrics(l2)
                m.update({"work": it["id"], "level":"L2","k_gloss":k,"gloss_policy":gp})
                outf.write(json.dumps(m)+"\n")
                # L3
                l3 = make_l3(title, l2)
                m = size_metrics(l3)
                m.update({"work": it["id"], "level":"L3","k_gloss":k,"gloss_policy":gp})
                outf.write(json.dumps(m)+"\n")
                # write files
                base = f"{it['id']}.k{k}.{gp}"
                json.dump(l2, open(os.path.join(args.out, f"L2.{base}.json"),"w",encoding="utf-8"), indent=2, ensure_ascii=False)
                json.dump(l3, open(os.path.join(args.out, f"L3.{base}.json"),"w",encoding="utf-8"), indent=2, ensure_ascii=False)
        for ch in params["l5_chunk"]:
            l5 = make_l5(title, text, ch)
            m = size_metrics(l5); m.update({"work": it["id"], "level":"L5","l5_chunk":ch})
            outf.write(json.dumps(m)+"\n")
            json.dump(l5, open(os.path.join(args.out, f"L5.{it['id']}.chunk{ch}.json"),"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    outf.close()
    print(f"[run_matrix] wrote {results_path} and JSON outputs in {args.out}")
if __name__ == "__main__":
    main()
