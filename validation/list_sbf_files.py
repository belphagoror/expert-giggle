# SPDX-License-Identifier: Apache-2.0
import sys, json
def is_sbf(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj.get("spec") == "SBF v0.1"
    except Exception:
        return False
def main():
    paths = sys.argv[1:]
    for p in paths:
        if is_sbf(p):
            print(p)
if __name__ == "__main__":
    main()
