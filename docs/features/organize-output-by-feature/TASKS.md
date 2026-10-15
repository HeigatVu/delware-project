---
type: TASKS
category: features
slug: organize-output-by-feature
title: "Tasks: group outputs by source data"
description: "Implementation task and acceptance criteria for grouping generated outputs by source data."
status: draft
created: 2026-10-16
updated: 2026-10-16
---

# Tasks: group outputs by source data

<abstract>

One task covers the source-domain move, default writer paths, navigation updates, and verification.

</abstract>

<tasks>

### T1: Group generated outputs by source data [done]

**Description:** Put transcript-derived feature data and analyses under `output/speech-features/`, keep MoCA results under `output/cognitive-scores/`, and update writers and reader paths.

**Acceptance criteria:**
- [x] All 15 transcript-derived output files live under `output/speech-features/` with unchanged Git blob IDs.
- [x] MoCA correlations and regressions remain under `output/cognitive-scores/`.
- [x] Default pipeline paths use the new layout, and explicit data, results, and figures overrides retain their behavior.
- [x] The output index, README, book, reference pages, and code tour describe the new layout.
- [x] No tracked reader points to the old top-level analysis folders.

**Verification:**
- [x] Focused tests: `pytest -q tests/test_main_outputs.py tests/test_tours.py`
- [x] Full suite: `pytest -v tests/` (29 passed)
- [x] Lint: project flake8 command
- [x] Output index links resolve and moved files compare as `R100`.

**Dependencies:** None

**Files likely touched:**
- `main.py`, `tests/test_main_outputs.py`
- `output/README.md` and generated output paths
- `README.md`, `book/`, `docs/`, and `.tours/01-entry-point.tour`

**Estimated scope:** Large: one output layout spans pipeline writers, 15 tracked artifacts, and reader documentation.

**Delivery branch:** `task/organize-output-by-source-data`

</tasks>

<revisions>

## Revisions

| Date | Change |
|---|---|
| 2026-10-16 | Created. |
| 2026-10-16 | Record the single completed T1 with explicit acceptance criteria and verification. |

</revisions>
