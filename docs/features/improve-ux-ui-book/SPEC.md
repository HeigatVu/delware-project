---
type: SPEC
category: features
slug: improve-ux-ui-book
title: "Improve book/ UX/UI and add .tours/ code tours"
description: "Specification for making the narrative documentation easier to navigate and annotating the codebase with VS Code Code Tour walkthroughs."
status: draft
created: 2026-10-15
updated: 2026-10-15
---

# Improve book/ UX/UI and add .tours/ code tours

Specification: what is being built or changed, and how a person will know it works.

<abstract>

The `book/` narrative documentation (4 Markdown pages) works but reads flat: no per-page navigation, an ASCII-only architecture diagram, and no on-ramp for someone opening the Python package for the first time. This change (a) gives every book page consistent navigation (breadcrumbs, prev/next footers, a described reading order on the index), (b) renders the module graph as a Mermaid flowchart with information parity to the ASCII art, and (c) adds a `.tours/` directory of VS Code Code Tour files that walk the CLI entry point and all eight pipeline modules with per-symbol notes. Done means: every book page links onward and back, the Mermaid diagram renders on GitHub, and every tour step points at a file/line that exists and matches what its note describes — machine-checked by a new pytest file.

</abstract>

<context>

## Objective

Ducvu reads this repository to understand and extend the Delaware speech-NLP replication. The book gives him the narrative; the `.tour` files give him guided, line-anchored notes inside the editor so re-reading the code later does not mean re-deriving it. Both are documentation-surface improvements with zero product-code impact.

## Assumptions

- A1. "UX/UI of book/" means the reading experience of the Markdown pages (navigation, structure, diagrams, callouts), not a change of format away from Markdown.
- A2. ".tour/" means the VS Code Code Tour extension convention: `.tours/*.tour` JSON files (`title`, `description`, `steps[].file`, `steps[].line`, `steps[].title`). No other tour format is introduced.
- A3. The existing content of the four book pages is accurate (it was authored and checked in the `write-map-each-feature` run); this change improves presentation and navigation, it does not re-research facts.
- A4. Python 3.10+ with the `alzheimer-speech` conda environment runs the tests; pytest finds `src/` through `pytest.ini`.

## Stack and commands

- Markdown only for `book/`; JSON for `.tours/`; one new pytest file under `tests/`.
- Tests: `/home/ducvu/.conda/envs/alzheimer-speech/bin/pytest -v tests/`
- Lint: `/home/ducvu/.conda/envs/alzheimer-speech/bin/flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503`
- Docs checks: `ultragentic docs check docs/features/improve-ux-ui-book`

</context>

<scope>

## In scope

- `book/README.md`, `book/overview.md`, `book/architecture.md`, `book/quickstart.md`: navigation blocks, Mermaid diagram, callout/alert formatting, a documented reading order.
- New `.tours/` directory with Code Tour JSON files covering: repository orientation, `main.py`, and the modules `chat_reader`, `demographics`, `pipeline`, `features`, `statistical_analysis`, `clustering`, `importance`, `visualization`.
- New `tests/test_tours.py` that machine-validates every tour file (parses as JSON, required fields present, every step's file exists, line within the file's line count, line content sanity).
- Cross-links: `book/README.md` mentions the tours and the per-function reference pages; tour descriptions point onward to the matching book page or reference page by name, not by hard-coded path (the docs tree is being reorganized into date folders by a concurrent run, so exact reference paths are intentionally avoided in prose and tour anchors).

## Out of scope

- Any behavior change under `src/delware_speech/` or `main.py` (docs/tours are annotative only).
- HTML/CSS site generation (no mdBook build, no static site), new runtime dependencies, CI changes.
- Rewriting the factual content of the book pages or `docs/reference/` (beyond links).
- Touring `tests/` file-by-file or `reference_repo/` (the original scripts).

## Boundaries

- Always: keep the four book pages as plain Markdown renderable on GitHub; keep `.tour` JSON valid per the Code Tour schema.
- Ask first: adding any new top-level directory other than `.tours/`.
- Never: edit `src/` or `main.py`; commit binary/image assets; add credentials or secrets to any file.

</scope>

<requirements>

## Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| R1 | Every book content page (overview, architecture, quickstart) begins with a breadcrumb back to the book index and ends with prev/next links matching the README's page order; the index lists all pages with one-line descriptions. | must |
| R2 | `book/architecture.md` contains a Mermaid flowchart of the module/data graph with at least the nodes and edges of the current ASCII diagram (both raw inputs, both readers, process_dataset, the two frames, the three analysis consumers, the figure outputs). | must |
| R3 | Each book page opens with a short "what you'll learn" line or mini-TOC, and warnings/notable caveats use GitHub alerts (`> [!WARNING]` / `> [!NOTE]`) instead of bare prose. | must |
| R4 | A `.tours/` directory exists with at least six `.tour` files that together cover `main.py` and all eight `src/delware_speech/` modules; every step has `file`, `line`, and a `description` naming the symbol being explained. | must |
| R5 | Every tour step's `file` resolves to a tracked repo file and its `line` falls within that file's line count; this is enforced by `tests/test_tours.py`. | must |
| R6 | `book/README.md` documents how to view the tours (Code Tour extension) and links the tour files by name. | must |
| R7 | The change touches no file under `src/` and does not modify `main.py`. | must |

</requirements>

<verification>

## Success criteria

| ID | Criterion | How it is checked |
|----|-----------|-------------------|
| SC1 | All tour files valid: JSON parses, required fields present, every step's file exists, line within bounds, and each tour covers the module its filename claims. | `/home/ducvu/.conda/envs/alzheimer-speech/bin/pytest -v tests/test_tours.py` |
| SC2 | Existing suite still green (nothing regressed by the docs change). | `/home/ducvu/.conda/envs/alzheimer-speech/bin/pytest -v tests/` |
| SC3 | Lint clean on the new test file. | `/home/ducvu/.conda/envs/alzheimer-speech/bin/flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503` |
| SC4 | R1–R3, R6 hold by inspection: breadcrumbs/footers on all three content pages, a ```mermaid fence in architecture.md, an alert callout present, tours documented on the index. | Open `book/*.md`; grep for `mermaid`, `[!WARNING]`, `« Prev`/`Next »` links. |
| SC5 | R7 holds. | `git diff --stat main...HEAD -- src/ main.py` is empty for this change's commits. |
| SC6 | Docs pass their own checks. | `ultragentic docs check docs/features/improve-ux-ui-book` |

</verification>

<open_questions>

- None.

</open_questions>

<revisions>

## Revisions

Appended by `ultragentic docs revise <this file> "<what changed>"`. Do not edit dates by hand.

| Date | Change |
|------|--------|
| 2026-10-15 | Created. |
| 2026-10-15 | A concurrent run (reorganize-docs-into-date) moved docs/reference/ into docs/2026-10-06/reference/; SPEC cross-links and tour anchors were reworded to avoid the moving path. |

</revisions>
