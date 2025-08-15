
# SPDX-License-Identifier: Apache-2.0
import sys, json, pathlib

CANON_COLS = ["id","act","evt_si","p","a","u","i","loc","when","time"]

def load(path):
    return json.load(open(path,"r",encoding="utf-8"))

def beats_iter(doc, pool):
    # yield dict rows with canon columns
    if "beats_tbl" in doc:
        cols = doc["beats_tbl"]["cols"]
        idx = {c:i for i,c in enumerate(cols)}
        for r in doc["beats_tbl"]["rows"]:
            yield {
                "id": r[idx["id"]],
                "act": r[idx["act"]],
                "evt_si": r[idx.get("evt_si", None)] if "evt_si" in idx else None,
                "p": r[idx.get("p", None)] if "p" in idx else None,
                "a": r[idx.get("a", None)] if "a" in idx else None,
                "u": r[idx.get("u", None)] if "u" in idx else None,
                "i": r[idx.get("i", None)] if "i" in idx else None,
                "loc": r[idx.get("loc", None)] if "loc" in idx else None,
                "when": r[idx.get("when", None)] if "when" in idx else None,
                "time": None,  # time lives in actn for object form; absent here
            }
    else:
        for b in doc.get("beats", []):
            evt_si = b.get("evt_si")
            if evt_si is None and isinstance(b.get("evt"), str):
                # normalize: push literal evt into pool if present
                try:
                    evt_si = pool.index(b["evt"])
                except ValueError:
                    pool.append(b["evt"]); evt_si = len(pool)-1
            actn = b.get("actn") or {}
            yield {
                "id": b.get("id"),
                "act": b.get("act"),
                "evt_si": evt_si,
                "p": actn.get("p"),
                "a": actn.get("a"),
                "u": actn.get("u"),
                "i": actn.get("i"),
                "loc": actn.get("loc"),
                "when": actn.get("when"),
                "time": actn.get("time")
            }

def norm(doc):
    # build a normalized structure to compare
    pool = list(((doc.get("dict") or {}).get("s") or []))
    rows = list(beats_iter(doc, pool))
    rows.sort(key=lambda r: r["id"] or "")
    chars = sorted([(c.get("id"), c.get("r"), c.get("n_si"), c.get("pro")) for c in (doc.get("chars") or [])])
    ents  = sorted([(e.get("id"), e.get("r"), e.get("n_si"), e.get("pro")) for e in (doc.get("ents") or [])])
    links = sorted([(l.get("rel"), l.get("src"), l.get("tgt")) for l in (doc.get("links") or [])])
    pool  = tuple(pool)
    out = {
        "l": doc.get("l"),
        "t": doc.get("t"),
        "lang": doc.get("lang"),
        "a_schema": doc.get("a_schema"),
        "rows": rows,
        "chars": chars,
        "ents": ents,
        "links": links,
        "pool": pool
    }
    return out

def main(paths):
    fail = False
    for p in paths:
        doc = load(p)
        # repack: from normalized rows go back to L3 form
        n = norm(doc)
        # repack as beats[] to preserve time
        beats = []
        for r in n["rows"]:
            beats.append({
                "id": r["id"],
                "act": r["act"],
                **({"evt_si": r["evt_si"]} if r.get("evt_si") is not None else {}),
                "actn": {"p": r.get("p"), "a": r.get("a"), "u": r.get("u"), "i": r.get("i"), "loc": r.get("loc"), "when": r.get("when"), "time": r.get("time")}
            })
        repacked = {
            "spec":"SBF v0.1",
            "spec_version": doc.get("spec_version","0.1.2"),
            "l": doc.get("l"),
            "t": n["t"],
            "lang": n["lang"],
            "a_schema": n["a_schema"],
            "dict": {"s": list(n["pool"])},
            "beats": beats,
            "links": [{"rel":a,"src":b,"tgt":c} for (a,b,c) in n["links"]],
            "chars": [{"id":a,"r":b,"n_si":c,"pro":d} for (a,b,c,d) in n["chars"]],
            "ents":  [{"id":a,"r":b,"n_si":c,"pro":d} for (a,b,c,d) in n["ents"]],
        }
        if norm(doc) != norm(repacked):
            print(f"[FAIL] {p}: normalized mismatch after repack")
            fail = True
        else:
            print(f"[OK]   {p}")
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: rt_idempotence.py <files...>"); sys.exit(2)
    main(sys.argv[1:])
