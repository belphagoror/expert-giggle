# SPDX-License-Identifier: Apache-2.0
import sys, json

def main(path):
    obj = json.load(open(path, "r", encoding="utf-8"))
    if "beats_tbl" in obj:
        cols = obj["beats_tbl"]["cols"]
        for r in obj["beats_tbl"]["rows"]:
            rec = {c: r[i] for i,c in enumerate(cols)}
            print(json.dumps(rec, ensure_ascii=False))
    elif "beats" in obj:
        for b in obj["beats"]:
            rec = {"id": b.get("id"), "act": b.get("act"), "evt_si": b.get("evt_si")}
            for k in ["p","a","u","i","loc","when","time"]:
                rec[k] = (b.get("actn") or {}).get(k)
            print(json.dumps(rec, ensure_ascii=False))
    else:
        print("[]")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: export_ndjson.py <sbf.json>"); sys.exit(2)
    main(sys.argv[1])
