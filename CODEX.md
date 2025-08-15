<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Using SBF with Code Assistants

## Standing instructions
- Read `docs/VISION.md` and `docs/SBF_v0.1_Spec.md` first.
- Respect level rules (L2/L3 lossy defaults).
- Run `make validate` after changes.

## Kickoff prompt
> Read the vision/spec, run `make validate`, propose the smallest improvement to SRL-lite without increasing size, update/add an example under `examples`, re-run validation, and show only the diff.

## Guardrails
- Keep dependencies small; prefer pure Python.

# For Code Assistants

## Mission
Keep SBF lossy core small and deterministic. Do not modify schema unless tests pass.

## Setup
```bash
make setup
python scripts/mk_corpus.py
python experiments/run_matrix.py --params experiments/params.yaml
python experiments/metrics.py
make validate
make roundtrip
```

## Defaults
- Pool threshold: 3
- L2/L3 gloss policy: `evt_si_only`
- L5 chunk: 1024

## Tools
- Validate: `python validation/sbf_validate.py examples/*.json`
- Schema: `python validation/schema_check.py schema/sbf_schema_v0_1.json <files>`
- Export NDJSON: `python -m sbf.cli export <sbf.json> --ndjson > beats.ndjson`
- Minified pack: `python tools/sbf_pack.py to-l3 in.json out.json --pool-threshold 3 --minify`

## Constraints
- IDs must match patterns: `^char:[a-z0-9_]+$`, `^ent:[a-z0-9_]+$`, `^b\d{4,}$`.
- Use `a_schema: "verbs.en.v1"` unless bumping with governance approval.
- L5 coverage is the union of spans; must satisfy `coverage ≥ 1 - loss_tolerance`.

## PR checklist
- [ ] `make release-check` passes on Linux.
- [ ] No schema change unless spec, types, validator, and examples updated.
- [ ] Update CHANGELOG with user-visible changes.
```
