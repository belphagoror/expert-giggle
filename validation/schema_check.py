# SPDX-License-Identifier: Apache-2.0
import sys, json
from jsonschema import Draft202012Validator

def is_sbf(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj.get("spec") == "SBF v0.1"
    except Exception:
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: schema_check.py <schema.json> <file1.json> [file2.json ...]")
        sys.exit(2)
    schema_path = sys.argv[1]
    files = [p for p in sys.argv[2:] if is_sbf(p)]
    if not files:
        print("[schema] No SBF files to validate.")
        return
    schema = json.load(open(schema_path, "r", encoding="utf-8"))
    validator = Draft202012Validator(schema)
    ok = True
    for p in files:
        try:
            obj = json.load(open(p, "r", encoding="utf-8"))
            validator.validate(obj)
            print(f"[schema] OK: {p}")
        except Exception as e:
            ok = False
            print(f"[schema] FAIL: {p} :: {e}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
