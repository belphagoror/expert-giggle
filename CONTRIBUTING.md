<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Contributing

- Open an issue before large changes.
- Follow GOVERNANCE for verbs and links.
- Keep the lossy core small and deterministic.
- Run locally:
  ```bash
  make setup
  make validate
  make roundtrip
  ```
- Do not commit heavy data. See `.gitignore`.

## PR checklist
- [ ] CHANGELOG updated
- [ ] `make release-check` passes
- [ ] No large artifacts added
