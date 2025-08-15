<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Story Blueprint Format (SBF)

- Vision: `docs/VISION.md`
- Spec (GFM): `docs/Story_Blueprint_Format_GFM.md`
- Normative spec: `docs/SBF_v0.1_Spec.md`

## Quick start
```bash
python validation/list_sbf_files.py examples/*.json > sbf_files.txt
python validation/schema_check.py schema/sbf_schema_v0_1.json $(cat sbf_files.txt)
python validation/sbf_validate.py $(cat sbf_files.txt)
```
bash
# List candidate files
python validation/list_sbf_files.py examples/*.json > sbf_files.txt

# Schema check
python validation/schema_check.py schema/sbf_schema_v0_1.json $(cat sbf_files.txt)

# Rule validation
python validation/sbf_validate.py $(cat sbf_files.txt)
```
```bash
python validation/list_sbf_files.py examples/*.json > sbf_files.txt
python validation/schema_check.py schema/sbf_schema_v0_1.json $(cat sbf_files.txt)
python validation/sbf_validate.py $(cat sbf_files.txt)

cd types && npm install --no-audit --no-fund && npx tsc --noEmit
```

## Defaults
- Pool threshold: 3
- L2/L3 gloss policy: `evt_si_only` (omit literal `evt` by default)
- L5 chunk size: 1024

## New fields (optional)
- Root: `lang`, `a_schema`, `links`
- Actions: `actn.time`

## Round-trip tests
```bash
python scripts/rt_idempotence.py examples/*.json
python scripts/rt_l5_text.py corpus/clean/*.txt out/L5.*.json
```

## Streaming export
```bash
python scripts/export_ndjson.py path/to/file.json > beats.ndjson
```
