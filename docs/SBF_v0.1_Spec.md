<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SBF v0.1 — Normative Specification

**Status:** Stable (v0.1).

This document is the **normative**, version-pinned definition of SBF v0.1. It defines required fields, allowed values, precedence, and conformance rules.

## 1. Conformance

### 1.1 Roles
- **Producer** emits SBF JSON.
- **Consumer** reads SBF and applies precedence.
- **Validator** verifies schema + rules.

### 1.2 Requirements keywords
**MUST**, **MUST NOT**, **SHOULD**, **MAY** as per RFC 2119.

### 1.3 Version pinning
SBF document **MUST** include `spec: "SBF v0.1"`, `l: "L1"|"L2"|"L3"|"L4"|"L5"`, and `t: <string>`. Consumers **MUST** ignore unknown fields.

## 2. Identifiers & common structures

### 2.1 IDs
- `BeatId` unique; **SHOULD** match `^b[0-9]{4,}$`.
- `CharId`/`EntId` unique; stable slugs.

### 2.2 Pools
`dict.s[]`, `dict.q[]` optional. Any `*_si` indexes those pools. Pool entries **SHOULD** be referenced ≥2×.

### 2.3 Beats (record)
```json
{ "id": "BeatId", "act": 1, "evt": "string", "evt_si": 0, "actn": { "p": "CharId", "a": "verb", "u": "CharId|EntId", "i": "string", "loc": "EntId", "when": "string" } }
```
If both `evt` and `evt_si` appear, `evt_si` is authoritative.

### 2.4 Beats (table)
`beats_tbl.cols` **MUST** equal:
`["id","act","evt_si","p","a","u","i","loc","when"]` in that order. When present, Producers **MUST** omit `beats`.

### 2.5 Chars & ents
```json
{ "id": "CharId|EntId", "r": "role", "n": "string|{}", "n_si": 0, "pro": "profile" }
```

## 3. Precedence
1) Tables over records. 2) `*_si` over inline strings. 3) Consumers prefer authoritative sources.

## 4. Levels

### L1 — Authoring/Debug
- Human-readable; no `evt` cap.

### L2 — Main (lossy)
- **MUST** cap/omit `evt` to ≤12 words.
- **MUST** use canonical verb for `actn.a`.
- **MUST NOT** include long prose.

### L3 — Main-Table (lossy)
- **MUST** provide `beats_tbl`; **omit** `beats`.
- Apply all L2 constraints.

### L4 — Less‑Lossy
- Optional `style`, `themes` (≤8), `quotes` (≤40, each ≤12 words via `dict.q[]`), `motifs`.

### L5 — Lossless‑ish
- `text_map` with `coverage`, `loss_tolerance`, `chunks`, `spans`.
- **MUST** satisfy `coverage ≥ 1 - loss_tolerance`.

## 5. Validation rules
- `act` ≥1; monotonic by act is **SHOULD**.
- L2/L3: `evt` ≤12 words if present; `actn.a` in canonical set.
- Pooling: discourage one-offs.
- L4 caps; L5 coverage check.
- `beats_tbl.cols` exact order as above.

## Appendix A — Canonical verbs (excerpt)
`confront, discover, reveal, pursue, evade, travel, hide, meet, separate, attack, defend, rescue, capture, escape, deceive, confess, investigate, observe, communicate, decide, plan, betray, negotiate, search, follow, lead, wait, warn, ambush, recover, lose, win, request, refuse, accept, deliver, acquire, release, threaten, promise, persuade, doubt, believe, fear, hope, need, attempt, fail, succeed, remember, forget, realize, explain, agree, disagree, accuse, prove, disprove`

## 2.x Optional fields added in v0.1.2
- Root:
  - `lang` — BCP47-lite language tag, e.g., `"en"` or `"en-US"`.
  - `a_schema` — versioned verb schema tag, e.g., `"verbs.en.v1"`.
  - `links` — optional typed edges between beats: `{rel, src, tgt}` with `src/tgt` as beat IDs.
- Actions:
  - `actn.time` — optional normalized time:
    - Ordinal: `{"kind":"ordinal","episode":N,"scene":N,"beat":N}`
    - ISO-like: `{"kind":"iso","start":"1897-05-03","end":null}`

### Identifiers
- `char.id` must match `^char:[a-z0-9_]+$`. `ent.id` must match `^ent:[a-z0-9_]+$`. `beat.id` must match `^b[0-9]{4,}$`.
- `lang` must match `^[a-z]{2}(-[A-Z]{2})?$`.

### L5 Coverage
- `text_map.coverage` is the **union** of span lengths per chunk divided by total chunk length. Overlaps do not stack.
- Must satisfy `coverage ≥ 1 − loss_tolerance` (with a tolerance of 1e-9 for floating rounding).
