
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
  "schema/sbf_schema_v0_1.json",
  "examples/example_L2.json",
  "examples/example_L3.json",
  "examples/example_L4.json",
  "examples/example_L5.json",
]
def main():
  missing = [p for p in REQUIRED if not (ROOT/p).exists()]
  if missing:
    print("Missing:", *missing, sep="\n - ")
    raise SystemExit(1)
  print("Integrity OK")
if __name__ == "__main__":
  main()
