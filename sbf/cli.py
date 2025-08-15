from __future__ import annotations
import argparse, sys, json, os, subprocess
from pathlib import Path
from typing import List, Optional

def _find_repo_schema(start: Path) -> Path | None:
    for c in (start / "schema" / "sbf_schema_v0_1.json",):
        if c.exists(): return c
    return None

def _validate_json(file_path: Path, schema_path: Path) -> int:
    try:
        import jsonschema
    except Exception as e:
        print("ERROR: jsonschema not installed.", file=sys.stderr); return 2
    with open(schema_path, "r", encoding="utf-8") as f: schema = json.load(f)
    with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
    try:
        jsonschema.validate(instance=data, schema=schema)
    except Exception as e:
        print(f"FAIL: {file_path} invalid: {e}", file=sys.stderr); return 1
    print(f"OK: {file_path}"); return 0

def _doctor() -> int:
    print("Python:", sys.version.split()[0])
    for mod in ("json","jsonschema"):
        try: __import__(mod); print("Module:", mod, "✓")
        except Exception as e: print("Module:", mod, "✗", e)
    try: node = subprocess.check_output(["node","--version"], text=True).strip()
    except Exception: node = "not found"
    print("Node:", node)
    return 0

def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    p = argparse.ArgumentParser(prog="sbf", description="SBF CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    pe = sub.add_parser("export"); pe.add_argument("file"); pe.add_argument("--ndjson", action="store_true")
    pv = sub.add_parser("validate"); pv.add_argument("files", nargs="+"); pv.add_argument("--schema")
    pp = sub.add_parser("pack"); pp.add_argument("profile", choices=["to-l2","to-l3"]); pp.add_argument("inp"); pp.add_argument("out")
    pd = sub.add_parser("diff"); pd.add_argument("a"); pd.add_argument("b")
    sub.add_parser("doctor")
    args = p.parse_args(argv)
    if args.cmd == "export":
        import json, sys
        obj = json.load(open(args.file, "r", encoding="utf-8"))
        if args.ndjson:
            # beats_tbl path
            if "beats_tbl" in obj:
                cols = obj["beats_tbl"]["cols"]
                for r in obj["beats_tbl"]["rows"]:
                    rec = {c: r[i] for i,c in enumerate(cols)}
                    print(json.dumps(rec, ensure_ascii=False))
            # beats object path
            elif "beats" in obj:
                for b in obj["beats"]:
                    rec = {
                        "id": b.get("id"),
                        "act": b.get("act"),
                        "evt_si": b.get("evt_si"),
                    }
                    for k in ["p","a","u","i","loc","when","time"]:
                        rec[k] = (b.get("actn") or {}).get(k)
                    print(json.dumps(rec, ensure_ascii=False))
            else:
                print("[]")
        else:
            print(json.dumps(obj, ensure_ascii=False))
        return 0


    if args.cmd == "validate":
        here = Path(os.getcwd())
        schema = Path(args.schema) if args.schema else _find_repo_schema(here)
        if not schema or not schema.exists():
            print("ERROR: schema not found (try --schema or schema/sbf_schema_v0_1.json)", file=sys.stderr); return 2
        rc = 0
        for f in args.files: rc |= _validate_json(Path(f), schema)
        return rc

    if args.cmd == "pack":
        tool = Path("tools") / "sbf_pack.py"
        if tool.exists():
            return subprocess.call([sys.executable, str(tool), args.profile, args.inp, args.out])
        else:
            with open(args.inp,"r",encoding="utf-8") as f: data=json.load(f)
            data["__packed_with_stub__"]=True; data["__target_profile__"]=args.profile
            with open(args.out,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
            print(f"Stub-packed {args.inp} -> {args.out} ({args.profile})"); return 0

    if args.cmd == "diff":
        with open(args.a,"r",encoding="utf-8") as fa, open(args.b,"r",encoding="utf-8") as fb:
            A,B=json.load(fa),json.load(fb)
        def ids(x):
            out=set()
            for r in x.get("beats", []):
                if "id" in r: out.add(r["id"])
            return out
        print("Only in A:", sorted(ids(A)-ids(B)))
        print("Only in B:", sorted(ids(B)-ids(A)))
        return 0

    if args.cmd == "doctor":
        return _doctor()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
