#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
echo "[preflight] Python: $(python --version)"
echo "[preflight] Node: $(node --version || echo 'missing')"
python - <<'PY'
import importlib
print('jsonschema OK' if importlib.util.find_spec('jsonschema') else 'jsonschema MISSING')
PY
