<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Story Blueprint Format — Guide

This is the friendly guide to SBF. For the normative spec, see `docs/SBF_v0.1_Spec.md`.

## Levels (Profiles)

### New Levels (v0.1 update)

- **L4 — Less‑Lossy (style & theme):** Same semantics as L2/L3, plus compact stylistic signals and themes that compress well (no large prose). Optional sections: `style`, `themes`, limited `quotes`, `motifs`. Tight caps apply.
- **L5 — Lossless‑ish (archival):** Optional text attachment via pooled shards and spans. Declares `coverage` (e.g., ≥ 0.96) and `loss_tolerance`. Not intended for day-to-day inference.

### Main (lossy) profile rules

- **Default:** Use **L2** for ingestion (L3 for very large datasets).  
- **`evt` cap:** At L2/L3, `evt` MUST be absent or ≤ **12 words** (short gloss only).  
- **Canonical verbs:** `actn.a` MUST come from the canonical verb set (Appendix A).  
- **Pooling:** Only pool strings used **≥ 2×** (names, places, stock glosses).  
- **Tables authority:** If a `*_tbl` is present, it overrides its record array. For `beats`, prefer `beats_tbl` and omit `beats` in L3.

### L4 (Less‑Lossy) caps

- `themes`: ≤ **8** items (controlled vocabulary labels), `beats` lists may be ranges.  
- `style`: compact integers/enums only (tone curve 0–9 × up to 5 points; pacing counts; diction fingerprint).  
- `quotes`: ≤ **40** per document; each quote ≤ **12 words**; stored via pooled indices.  
- `motifs`: IDs + beat refs only (labels pooled).

### L5 (Lossless‑ish) requirements

- `text_map.coverage ≥ 1 - loss_tolerance`.  
- Each `chunk` includes stable `hash` and `len`.  
- `spans` anchor chunks to `beat`/`chapter` scopes via IDs.
