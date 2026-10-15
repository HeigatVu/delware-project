---
type: SPEC
category: features
slug: write-map-each-feature
title: "Documentation maps for every module in src/delware_speech, organized docs + book style"
description: "Documentation maps for every module in src/delware_speech, organized docs + book style"
status: active
created: 2026-10-05
updated: 2026-10-05
format: legacy
---


# Documentation maps for every module in src/delware_speech, organized docs + book style

## Class
document

## Deliverable
Markdown documentation explaining every file in `src/delware_speech/` — each file's functions
and the goal for which the file was created — organized like the `docs/` (repo-level reference)
and `book/` (narrative user/developer/architecture docs) split of
github.com/FranklinChen/talkbank-tools, so a reader checking the code understands it clearly:

1. `src/delware_speech/README.md` — the per-file map for the package: for each of the 9 `.py`
   files, its purpose, its public functions with one-line explanations, and the goal that
   motivated creating the file (which paper section or R reference script it implements).
2. `docs/reference/` — one reference page per module (8 pages, all modules except
   `__init__.py`): every public function with signature, inputs/outputs, and the paper or
   reference-repo artifact it replicates.
3. `book/` — narrative documentation: `book/README.md` (navigation), `book/overview.md`
   (what the study and this implementation are), `book/architecture.md` (pipeline stages and
   data flow from .cha transcripts to figures), `book/quickstart.md` (install and run).
4. `README.md` at the repository root — a repository map table linking each major directory
   (src, docs, book, data, results, figures, tests, reference_repo) to its purpose.

## Done line
A reader can open the root README, `src/delware_speech/README.md`, the `book/` pages, and
`docs/reference/` and find every module and every public function of `src/delware_speech`
explained with its purpose and creation goal, with each documented function name verified by
script to exist in the source.

## Sources
- `src/delware_speech/__init__.py`, `chat_reader.py`, `demographics.py`, `features.py`,
  `pipeline.py`, `statistical_analysis.py`, `clustering.py`, `importance.py`,
  `visualization.py`
- `main.py` (CLI entrypoint showing how modules compose)
- `tests/` (six test files showing expected behavior)
- `docs/paper/nyongesa-et-al-2025-*.pdf` and `docs/paper/paper_text.txt` (the replicated study)
- `reference_repo/speech/` (original paper scripts: 01-05 numbered scripts, Cluster_Analysis.R,
  Importance_Features.R, t-SNE_PLOTS_.R)
- `data/`, `results/`, `figures/` (pipeline outputs referenced by the docs)
- Repository structure of github.com/FranklinChen/talkbank-tools (docs/book organization model)

## Acceptance rows
| AC id | What must be true | How it is checked |
|-------|-------------------|-------------------|
| AC1 | `src/delware_speech/README.md` exists and has a section for each of the 9 `.py` files in the package, each stating the file's purpose, its public functions, and the goal for which the file was created | `grep -c` for each module filename in the README returns at least 1 per module |
| AC2 | `docs/reference/` contains one page per module (8 pages) and every public function of each module is listed on its page | list the directory; for each module, grep its page for each `def` name found by AST parse |
| AC3 | `book/` contains `README.md`, `overview.md`, `architecture.md`, and `quickstart.md`, and `book/README.md` links to the other three | list the directory; grep `book/README.md` for the three links |
| AC4 | Root `README.md` exists with a repository map table whose rows cover src, docs, book, data, results, figures, tests, reference_repo | open the file and grep the table for each directory name |
| AC5 | Every function name documented in `src/delware_speech/README.md` and `docs/reference/` exists in the actual source (no invented functions) | run a Python AST script that extracts public `def` names per module and cross-checks the docs |
| AC6 | All new documentation uses paths relative to the repository root; no machine-absolute paths (`/home/`, `/shared-data/` in links or code fences presenting repo layout) | `grep -rnE "/home/|/shared-data/" docs/reference book src/delware_speech/README.md README.md` returns no matches outside quoted CLI examples of dataset locations already in main.py defaults |

## Outward actions
| ID | Action | Tool or channel | Recipient or target | Exact content or amount |
|----|--------|-----------------|---------------------|-------------------------|
| none | | | | |

## Budget
Time: 90 minutes. Sources: the 15 files listed above plus one fetched web page
(github.com/FranklinChen/talkbank-tools structure). Cost: none.

## Open questions
none
