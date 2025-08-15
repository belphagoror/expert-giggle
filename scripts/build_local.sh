#!/usr/bin/env bash
set -euo pipefail
python -m pip install build >/dev/null 2>&1 || echo "Install 'build' locally to create Python artifacts"
if command -v python >/dev/null; then
  echo "[python] building dist/ ..."
  python -m build
fi
if command -v npm >/dev/null; then
  echo "[npm] packing types/ ..."
  (cd types && npm pack)
fi
echo "Done. Artifacts in dist/ and types/"
