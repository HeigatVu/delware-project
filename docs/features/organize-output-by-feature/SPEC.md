---
type: SPEC
category: features
slug: organize-output-by-feature
title: "Group generated outputs by analysis feature"
description: "Put pipeline products beside related data and document where to check each result."
status: draft
created: 2026-10-16
updated: 2026-10-16
---

# Group generated outputs by analysis feature

Specification: what changes and how a person will know it works.

<abstract>

The pipeline currently scatters generated files across `data/`, `results/`, and `figures/`. Put them under one `output/` root and group them by the analysis or data they describe, while preserving every existing file. Add a short linked index and update the run instructions so a reader can find an output without knowing which pipeline stage wrote it.

</abstract>

<context>

## Objective

Make the products of the pipeline easy to browse by putting related tables and plots together.

## Stack and commands

- Python CLI: `main.py`; pipeline and analysis modules under `src/delware_speech/`.
- Output index and run guidance: Markdown in `output/`, `README.md`, and `book/`.
- Verification: pytest, flake8, and `ultragentic docs check`.

</context>

<scope>

## In scope

- `output/processed-data/`, `group-comparisons/`, `cognitive-scores/`, `clustering/`, `classification/`, and `task-profiles/`.
- Update `main.py` defaults and CLI help to use the grouped paths. Keep `--data-dir`, `--results-dir`, and `--figures-dir` as optional overrides.
- Move the existing tracked output files without changing their contents or names.
- Add `output/README.md` with links to every current output, and update the repository README and book pages that describe output paths.
- Test that the pipeline writes processed data under the new default root.

## Out of scope

- Changing feature extraction, statistics, model results, plot contents, or output filenames.
- Reprocessing source data or adding new pipeline outputs.

</scope>

<requirements>

| ID | Requirement | Priority |
|---|---|---|
| R1 | Default runs write all outputs under `output/`. | must |
| R2 | Outputs are grouped into the six feature folders listed above. | must |
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
| SC1 | Existing generated files are all present under the correct feature folder. | Compare the source and destination filenames and hashes. |
| SC2 | A processing run writes its CSVs beneath the configured output root. | `pytest -q tests/test_main_outputs.py` |
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

</revisions>
