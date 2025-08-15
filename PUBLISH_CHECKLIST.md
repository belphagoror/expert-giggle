<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Publish Checklist (run after community feedback)

## Versioning
- [ ] Decide next version (e.g., 0.1.3)
- [ ] Update versions in `pyproject.toml` and `types/package.json`
- [ ] Update `CHANGELOG.md`

## Build verify (local)
```bash
python -m pip install build twine
python -m build                 # dist/*.whl, *.tar.gz
npm pack types                  # creates @sbf-types-<ver>.tgz
make release-check
```

## Dry-run install
```bash
python -m venv .venv && source .venv/bin/activate
pip install dist/*.whl
npm i -D ./types
```

## Tag and GitHub release
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
# Draft release using RELEASE_NOTES_vX.Y.Z.md
```

## Publish (when ready)
- PyPI: `python -m twine upload dist/*`
- npm:  `cd types && npm publish --access public`
