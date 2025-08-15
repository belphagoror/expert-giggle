# SPDX-License-Identifier: Apache-2.0
import re, json, argparse, subprocess, os, sys
from pathlib import Path

CANON = set("confront discover reveal pursue evade travel hide meet separate attack defend rescue capture escape deceive confess investigate observe communicate decide plan betray negotiate search follow lead wait warn ambush recover lose win request refuse accept deliver acquire release threaten promise persuade doubt believe fear hope need attempt fail succeed remember forget realize explain agree disagree accuse prove disprove".split())

def slug(s):
    s = re.sub(r"[^a-z0-9]+","_", s.lower()).strip("_")
    return s[:48] or "x"

def strip_md(md):
    md = re.sub(r"(?s)```.*?```"," ", md)
    md = re.sub(r"(?is)<script.*?>.*?</script>"," ", md)
    md = re.sub(r"(?is)<style.*?>.*?</style>"," ", md)
    md = re.sub(r"(?is)<[^>]+>"," ", md)
    md = re.sub(r"!\\[[^\\]]*\\]\\([^\\)]*\\)"," ", md)
    md = re.sub(r"\\[([^\\]]+)\\]\\([^\\)]*\\)", r"\\1", md)
    md = re.sub(r"[ \\t]+"," ", md)
    return md

def split_sections(text):
    lines = text.splitlines()
    sections = []
    buf = []; headers = []
    for ln in lines:
        if re.match(r"^\\s*#{1,6}\\s+\\S", ln):
            if buf:
                sections.append("\\n".join(buf).strip())
                buf = []
            headers.append(ln.strip("# ").strip())
        else:
            buf.append(ln)
    if buf: sections.append("\\n".join(buf).strip())
    if not sections: sections = [text]
    return headers, sections

def paras(section):
    parts = re.split(r"\\n\\s*\\n", section)
    parts = [re.sub(r"\\s+"," ",p).strip() for p in parts if len(p.split())>=8]
    return parts

def find_names(s):
    cands = re.findall(r"\\b([A-Z][a-z]+(?: [A-Z][a-z]+){0,2})\\b", s)
    bad = set("The A An And But Or Nor Then When While Once For Of In On At By With From To Into Onto Over Under As If Not No Yes I He She They We You It His Her Their Our Your Its".split())
    cands = [x for x in cands if x.split()[0] not in bad]
    return cands[:4]

def find_loc(s):
    m = re.search(r"\\b(?:at|in|on|near|inside|outside|over|under)\\s+([A-Z][A-Za-z0-9 '\\-]+)", s)
    return m.group(1).strip() if m else None

def find_verb(s):
    words = [w.lower().strip(".,!?;:") for w in s.split()]
    for w in words:
        base = re.sub(r"(ing|ed|es|s)$","", w)
        if w in CANON: return w
        if base in CANON: return base
    return "observe"

def build_doc(title, sections):
    chars = {}; ents = {}
    beats = []
    total = sum(len(paras(sec)) for sec in sections)
    seen = 0
    for sec_i, sec in enumerate(sections):
        ps = paras(sec)
        for p_i, p in enumerate(ps):
            seen += 1
            act = 1 + (seen-1) * 3 // max(1,total)
            names = find_names(p)
            loc = find_loc(p)
            verb = find_verb(p)
            p_id = None; u_id = None; loc_id = None
            if names:
                p_name = names[0]; pid = "ch_"+slug(p_name)
                chars.setdefault(pid, {"id":pid,"n":p_name})
                p_id = pid
            if len(names)>1:
                u_name = names[1]; uid = "ch_"+slug(u_name)
                chars.setdefault(uid, {"id":uid,"n":u_name})
                u_id = uid
            if loc:
                lid = "loc_"+slug(loc)
                ents.setdefault(lid, {"id":lid,"type":"loc","n":loc})
                loc_id = lid
            gloss = " ".join(p.split()[:12])
            beats.append({"id": f"b{seen:05d}", "act": act, "evt": gloss, "actn": {"p": p_id, "a": verb, "u": u_id, "loc": loc_id}})
    doc = {"spec":"SBF v0.1","spec_version":"0.1.0","l":"L1","t":title,
           "k":{"legend":"SRL-lite ingestion; evt is short gloss; actn populated; acts by section/position"},
           "chars": list(chars.values()), "ents": list(ents.values()), "beats": beats}
    return doc

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--title")
    ap.add_argument("--profile", choices=["l1","l2","l3"], default="l2")
    ap.add_argument("--evt-cap", type=int, default=12)
    ap.add_argument("--pool-threshold", type=int, default=2)
    args = ap.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8", errors="ignore")
    text = strip_md(raw)
    headers, sections = split_sections(text)
    title = args.title or Path(args.input).stem.replace("_"," ").replace("-"," ").title()

    l1 = build_doc(title, sections)
    Path(args.output).write_text(json.dumps(l1, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.profile in ("l2","l3"):
        mode = "to-l2" if args.profile=="l2" else "to-l3"
        out2 = str(Path(args.output).with_name(Path(args.output).stem + ("_L2.json" if args.profile=="l2" else "_L3.json")))
        subprocess.check_call([sys.executable, str(Path(__file__).parent.parent / "tools" / "sbf_pack.py"), mode, args.output, out2, "--evt-cap", str(args.evt_cap), "--pool-threshold", str(args.pool_threshold)])
        print("[ingest] L1 written and packed to", out2)

if __name__ == "__main__":
    main()
