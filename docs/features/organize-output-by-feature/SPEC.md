---
type: SPEC
category: features
slug: organize-output-by-feature
title: "Group generated outputs by source data"
description: "Organize outputs by their source data domain so results are easier to check."
status: draft
created: 2026-10-16
updated: 2026-10-16
---

# Group generated outputs by source data

Specification: what changes and how a person will know it works.

<abstract>

The current six top-level folders make related outputs hard to find. Keep the existing subfolders, but place transcript-derived feature data and analyses under `output/speech-features/`; keep MoCA results under `output/cognitive-scores/`. Preserve every existing file and update the index and run instructions to show this two-domain layout.

</abstract>

<context>

## Objective

Make pipeline products easy to browse by grouping them under the source data domain they describe.

## Stack and commands

- Python CLI: `main.py`; pipeline and analysis modules under `src/delware_speech/`.
- Output index and run guidance: Markdown in `output/`, `README.md`, and `book/`.
- Verification: pytest, flake8, and `ultragentic docs check`.

</context>

<scope>

## In scope

- `output/speech-features/{processed-data,group-comparisons,clustering,classification,task-profiles}/` and `output/cognitive-scores/`.
- Update `main.py` defaults and CLI help to use the grouped paths. Keep `--data-dir`, `--results-dir`, and `--figures-dir` as optional overrides.
- Move the existing tracked output files without changing their contents or names.
- Update `output/README.md` with links to every current output, and update the repository README, book pages, and CLI tour that describe output paths.
- Test that the pipeline writes processed data under the new default root.

## Out of scope

- Changing feature extraction, statistics, model results, plot contents, or output filenames.
- Reprocessing source data or adding new pipeline outputs.

</scope>

<requirements>

| ID | Requirement | Priority |
|---|---|---|
| R1 | Default runs write all outputs under `output/`. | must |
| R2 | Transcript-derived outputs live under `output/speech-features/`, and MoCA outputs live under `output/cognitive-scores/`. | must |
| R3 | Existing output files keep their names and bytes after being moved. | must |
| R4 | `output/README.md` links to every existing output and explains the folders. | must |
| R5 | The CLI retains the three directory override flags and adds a single `--output-dir` root. | must |
| R6 | The quickstart, overview, architecture, and repository README describe the new paths. | must |
| R7 | A focused test checks the processed-data output location. | must |

</requirements>

<verification>

## Success criteria

| ID | Criterion | How it is checked |
|---|---|---|
| SC1 | Existing generated files are all present in the correct data-domain folder with unchanged bytes. | Compare the source and destination filenames and hashes. |
| SC2 | A processing run writes its CSVs under `output/speech-features/processed-data/`. | `pytest -q tests/test_main_outputs.py` |
| SC3 | Tour anchors remain valid after the `main.py` edit. | `pytest -q tests/test_tours.py` |
| SC4 | Code style and full suite pass. | project flake8 command and `pytest -v tests/` |
| SC5 | Documentation has no stale `data/`, `results/`, or `figures/` output paths. | Search README and book pages. |

</verification>

<open_questions>

- None.

</open_questions>

<revisions>

## Revisions

| Date | Change |
|---|---|
| 2026-10-16 | Created. |
| 2026-10-16 | Group outputs by source data domain following user feedback. |
| 2026-10-16 | Require repo-root output paths under both source-data folders. |

</revisions>
