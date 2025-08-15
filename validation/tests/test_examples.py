
import json, subprocess, sys, pathlib

def test_examples_schema_and_rules():
    repo = pathlib.Path(__file__).resolve().parents[2]
    examples = sorted((repo/"examples").glob("*.json"))
    assert examples, "no examples found"

    # Schema check must pass
    schema = repo / "schema/sbf_schema_v0_1.json"
    cmd = [sys.executable, str(repo/"validation/schema_check.py"), str(schema)] + [str(p) for p in examples]
    rc = subprocess.run(cmd, capture_output=True, text=True)
    assert rc.returncode == 0, f"schema_check failed:\n{rc.stdout}\n{rc.stderr}"

    # Rule validate must report 0 ERROR
    cmd = [sys.executable, str(repo/"validation/sbf_validate.py")] + [str(p) for p in examples]
    rc = subprocess.run(cmd, capture_output=True, text=True)
    assert rc.returncode == 0, f"sbf_validate failed rc={rc.returncode}:\n{rc.stdout}\n{rc.stderr}"
    assert "ERROR" not in rc.stdout, f"validation errors present:\n{rc.stdout}"
