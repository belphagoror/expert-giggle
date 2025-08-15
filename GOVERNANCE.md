# Governance

## Canonical verbs
- Current schema: `verbs.en.v1`. Changes bump minor (`verbs.en.v2`).
- Rules for changes:
  - Additions: MUST map to existing concepts or be widely used.
  - Removals: only at major spec versions.
  - Aliases: maintain a mapping table; do not change canonical labels mid-version.

## Links
- Allowed `links.rel` starter set: `reveals_of`, `causes`, `consequence_of`, `foreshadows`, `contradicts`, `parallels`.
- Additions require examples and reasoning benefit.

## Process
- Open an issue with proposal and examples.
- Two approvals from maintainers; one-week comment period.
- Version tag updated in `validation/canonical_verbs.json` and docs.
