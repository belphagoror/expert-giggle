# SBF v0.1.2 — Release Notes

## Highlights
- Optional fields: `lang`, `a_schema`, `links`, `actn.time`.
- Deterministic coverage: L5 union-of-spans check.
- Round-trip harnesses in `scripts/` and CI gates.
- Packer defaults tuned from corpus (pool=3, evt_si_only, L5 chunk=1024).
- CLI: `export --ndjson`, `--minify` for packing.

## Breaking changes
- None. All additions are optional. Existing v0.1 files remain valid.

## Upgrade notes
- Add `a_schema: "verbs.en.v1"` to new documents for clarity.
- Optionally set `lang: "en"` when using English canonical verbs.

## Contributors
- Maintainers
