# SPDX-License-Identifier: Apache-2.0
import sys, json, itertools

CANON_COLS = ["id","act","evt_si","p","a","u","i","loc","when"]
def main(path):
    pool = []
    def idx(s):
        if s is None: return None
        try: return pool.index(s)
        except ValueError: pool.append(s); return len(pool)-1
    rows = []
    for line in open(path,"r",encoding="utf-8"):
        line = line.strip()
        if not line: continue
        o = json.loads(line)
        evt = o.get("evt")
        evt_si = idx(evt) if isinstance(evt, str) else o.get("evt_si")
        rows.append([o.get("id"), o.get("act",1), evt_si, o.get("p"), o.get("a"), o.get("u"), o.get("i"), o.get("loc"), o.get("when")])
    doc = {"spec":"SBF v0.1","spec_version":"0.1.2","l":"L3","t":"events",
           "a_schema":"verbs.en.v1","lang":"en",
           "dict":{"s": pool},
           "beats_tbl":{"cols": CANON_COLS, "rows": rows}}
    json.dump(doc, sys.stdout, ensure_ascii=False, indent=2)
if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Usage: events_to_sbf.py events.ndjson"); sys.exit(2)
    main(sys.argv[1])
