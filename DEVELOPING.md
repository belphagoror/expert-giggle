<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Developing with SBF

## Layout
- docs/ — human-facing docs
- schema/, validation/, tools/, ingest/, types/, examples/
- .github/workflows/ — CI

## Python env
```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip -r requirements.txt
```

## Make targets
```bash
make validate
make types
make ingest-demo
make pack-demo
make integrity
```

## Conventions
- L2/L3 are lossy; cap/omit `evt`.
- Use canonical verbs for `actn.a`.
- Tables are authoritative in L3.
