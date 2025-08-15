# SPDX-License-Identifier: Apache-2.0
import sys, json, argparse
from copy import deepcopy

CANON_BEATS_COLS = ["id","act","evt_si","p","a","u","i","loc","when"]
CANON_CHARS_COLS = ["id","r","n_si","pro"]

def build_pool(doc):
    pool = []
    def add(s):
        if isinstance(s, str) and s not in pool:
            pool.append(s)
    for b in doc.get("beats", []):
        add(b.get("evt"))
    for arr in (doc.get("chars", []), doc.get("ents", [])):
        for o in arr or []:
            n = o.get("n")
            if isinstance(n, str): add(n)
            if isinstance(n, dict):
                for v in n.values(): add(v)
    for m in doc.get("mysteries", []):
        q = m.get("q")
        if isinstance(q, str): add(q)
    return pool

def to_l2(doc, evt_cap=12, remove_evt=True, pool_threshold=2):
    d = deepcopy(doc)
    d.setdefault("dict", {}).setdefault("s", [])
    pool = d["dict"]["s"]
    if not pool:
        pool.extend(build_pool(d))
    def idx(s):
        if not isinstance(s, str): return None
        try:
            return s_pool._index.get(s)
        except ValueError:
            pool.append(s)
            return len(pool)-1
    for b in d.get("beats", []):
        if "evt" in b and isinstance(b["evt"], str):
            words = [w for w in b["evt"].split()]
            gloss = " ".join(words[:evt_cap])
            b["evt_si"] = idx(gloss)
            if remove_evt:
                b.pop("evt", None)
    for arr in (d.get("chars", []), d.get("ents", [])):
        for o in arr or []:
            n = o.get("n")
            if isinstance(n, str):
                o["n_si"] = idx(n)
            elif isinstance(n, dict):
                v = n.get("en") if "en" in n else (next(iter(n.values())) if n else None)
                if isinstance(v, str):
                    o["n_si"] = idx(v)
    for m in d.get("mysteries", []):
        if isinstance(m.get("q"), str):
            m["q_si"] = idx(m["q"])
    d["l"] = "L2" if d.get("l") in (None,"L0","L1","L2") else d.get("l")
    return d

def to_l3(doc, evt_cap=12, remove_evt=True, pool_threshold=2):
    d = to_l2(doc, evt_cap=evt_cap, remove_evt=remove_evt, pool_threshold=pool_threshold)
    rows = []
    for b in d.get("beats", []):
        a = b.get("actn") or {}
        rows.append([
            b.get("id"),
            b.get("act") if isinstance(b.get("act"), int) else 1,
            b.get("evt_si") if isinstance(b.get("evt_si"), int) else None,
            a.get("p"), a.get("a"), a.get("u"), a.get("i"), a.get("loc"), a.get("when")
        ])
    d["beats_tbl"] = {"cols": CANON_BEATS_COLS, "rows": rows}
    if d.get("chars"):
        crows = []
        for c in d["chars"]:
            crows.append([c.get("id"), c.get("r"), c.get("n_si"), c.get("pro")])
        d["chars_tbl"] = {"cols": CANON_CHARS_COLS, "rows": crows}
    d.pop("beats", None)
    d["l"] = "L3"
    return d

def compact_pool(doc, threshold=2):
    d = doc.get("dict") or {}
    pool = d.get("s") or []
    if not pool or threshold <= 1:
        return doc
    ref_counts = [0]*len(pool)
    def bump(i):
        if isinstance(i, int) and 0 <= i < len(pool):
            ref_counts[i] += 1
    for b in doc.get("beats", []):
        bump(b.get("evt_si"))
    for arr in (doc.get("chars", []), doc.get("ents", [])):
        for o in arr or []:
            bump(o.get("n_si"))
    keep = {}
    new_pool = []
    for i,s in enumerate(pool):
        if ref_counts[i] >= threshold:
            keep[i] = len(new_pool)
            new_pool.append(s)
    if len(new_pool) == len(pool):
        return doc
    def remap(i):
        if isinstance(i, int) and i in keep:
            return keep[i]
        return None
    for b in doc.get("beats", []):
        if "evt_si" in b:
            ni = remap(b.get("evt_si"))
            if ni is None:
                b.pop("evt_si", None)
            else:
                b["evt_si"] = ni
    for arr in (doc.get("chars", []), doc.get("ents", [])):
        for o in arr or []:
            if "n_si" in o:
                ni = remap(o.get("n_si"))
                if ni is None:
                    o.pop("n_si", None)
                else:
                    o["n_si"] = ni
    d["s"] = new_pool
    doc["dict"] = d
    return doc

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["to-l1","to-l2","to-l3","auto"])
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--evt-cap", type=int, default=12)
    ap.add_argument("--keep-evt", action="store_true")
    ap.add_argument("--minify", action="store_true")
    ap.add_argument("--pool-threshold", type=int, default=3)
    ap.add_argument("--profile", choices=["l1","l2","l3","l4","l5"], help="Alias for mode")
    ap.add_argument("--loss-tolerance", type=float, default=0.04)
    args = ap.parse_args()
    doc = json.load(open(args.input, "r", encoding="utf-8"))
    if args.profile:
        if args.profile == "l1": args.mode = "to-l1"
        elif args.profile == "l2": args.mode = "to-l2"
        elif args.profile == "l3": args.mode = "to-l3"
        else: args.mode = "auto"
    if args.mode == "to-l2":
        out = to_l2(doc, evt_cap=args.evt_cap, remove_evt=not args.keep_evt, pool_threshold=args.pool_threshold)
        out = compact_pool(out, threshold=args.pool_threshold)
    elif args.mode == "to-l3":
        out = to_l3(doc, evt_cap=args.evt_cap, remove_evt=not args.keep_evt, pool_threshold=args.pool_threshold)
        out = compact_pool(out, threshold=args.pool_threshold)
    elif args.mode == "to-l1":
        out = deepcopy(doc); out["l"]="L1"
    else:
        out = to_l2(doc)
    json.dump(out, open(args.output, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[packed] {args.input} -> {args.output} ({args.mode})")

if __name__ == "__main__":
    main()
