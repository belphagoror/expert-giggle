# SPDX-License-Identifier: Apache-2.0
import sys, json, re
REQ = {"id":str,"act":int,"a":(str,type(None))}
ID_BEAT_RE = re.compile(r"^b\d{4,}$")
def main(path):
    n=0; bad=0
    for i,line in enumerate(open(path,"r",encoding="utf-8"), start=1):
        s = line.strip()
        if not s: continue
        n+=1
        try:
            o = json.loads(s)
        except json.JSONDecodeError as e:
            print(f"[BAD] line {i}: invalid JSON: {e}"); bad+=1; continue
        for k,t in REQ.items():
            if k not in o or not isinstance(o[k], t):
                print(f"[BAD] line {i}: missing/typed {k}"); bad+=1; break
        else:
            if not ID_BEAT_RE.match(o["id"]):
                print(f"[BAD] line {i}: id must match ^b\\d{{4,}}$"); bad+=1
    if bad:
        print(f"[FAIL] {bad}/{n} bad lines"); sys.exit(1)
    print(f"[OK] {n} lines"); sys.exit(0)
if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Usage: check_events_ndjson.py events.ndjson"); sys.exit(2)
    main(sys.argv[1])
