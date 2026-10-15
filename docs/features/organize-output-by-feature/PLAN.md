---
type: PLAN
category: features
slug: organize-output-by-feature
title: "Plan: group outputs by source data"
description: "Keep speech-feature outputs together, separate MoCA outputs, and update writers and navigation."
status: draft
created: 2026-10-16
updated: 2026-10-16
---

# Plan: group outputs by source data

<abstract>

Move existing files into source-data folders, update default writer paths, then update navigation and verify the move.

</abstract>

<approach>

## Steps

1. Move transcript-derived tables and analyses under `output/speech-features/`; keep MoCA results in `output/cognitive-scores/`.
2. Update `main.py` defaults to write into those folders while preserving all directory override flags.
3. Update the output index, README, book, reference docs, and tour descriptions to match the new paths.
4. Update the output path test and verify the move by comparing old and new Git blob IDs.
5. Run focused tests, the full suite, lint, and docs checks.

</approach>

<risks>

## Risk

The `main.py` tour uses source line anchors. Run `tests/test_tours.py` after changing the function and update only affected anchors.

</risks>

<verification>

## Verification

- Focused: `pytest -q tests/test_main_outputs.py tests/test_tours.py`
- Full suite: `pytest -v tests/`
- Lint: the repository flake8 command
- Docs: `ultragentic docs check` for this feature folder

</verification>

<revisions>

## Revisions

| Date | Change |
|---|---|
| 2026-10-16 | Created. |
| 2026-10-16 | Align the implementation sequence with source-domain output folders and preserve existing overrides. |

</revisions>
