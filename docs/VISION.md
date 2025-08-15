<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Vision

SBF is a **stand‑alone, plain‑text, lossy‑first** format that compresses stories into compact, self‑explanatory JSON that AIs can ingest and reason over with minimal prompting. We prioritize **semantic retention** (characters, entities, places, actions, motives, arcs) over surface prose, and keep token budgets tiny by using **IDs, indices, and tables**.

**Principles**
- Lossy-first core (L2/L3) for scalable ingestion; style/text are optional layers (L4/L5).
- Self-describing, zero external deps; the file is the contract.
- Stable IDs, pooled strings, and columnar tables for compression.
- Deterministic tools; small, auditable validators.
