.PHONY: setup validate test lint format precommit types
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -e .[dev]
validate:
	sbf validate examples/*.json
test:
	pytest -q
lint:
	ruff check .
format:
	black .
precommit:
	pre-commit run --all-files
types:
	@if [ -f types/package.json ]; then \
	npm ci --prefix types && npx --prefix types tsc --noEmit; \
	else echo "No types/ package"; fi

roundtrip:
	python scripts/rt_idempotence.py examples/*.json
	python scripts/rt_l5_text.py corpus/clean/*.txt out/L5.*.json

release-check: validate roundtrip types
	@echo "All gates passed."

ingest-lmstudio:
	python scripts/ingest_lmstudio.py --model "$(MODEL)" --text "$(FILE)" --out events.ndjson
	python scripts/check_events_ndjson.py events.ndjson
	python scripts/events_to_sbf.py events.ndjson > out/$(notdir $(FILE:.txt=.L3.json))
