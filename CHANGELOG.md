# Changelog

## v0.1.2
- Added optional `lang`, `a_schema`, `links`, and `actn.time`.
- Enforced ID regexes and L5 union coverage in validator.
- Added round-trip harnesses and CI gates.
- Packer defaults: pool threshold=3, omit literal `evt`, L5 chunk=1024.
- CLI: `sbf export --ndjson` and `--minify` for packing outputs.
