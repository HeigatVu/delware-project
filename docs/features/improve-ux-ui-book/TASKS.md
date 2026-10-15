---
type: TASKS
category: features
slug: improve-ux-ui-book
title: "Tasks: book UX/UI and code tours"
description: "Two tasks in one milestone pair: the book navigation pass, then the code tours with their validation test."
status: draft
created: 2026-10-15
updated: 2026-10-15
---

# Tasks: book UX/UI and code tours

Task list for this slug. Status lives in each heading, using: queued, in_progress, blocked, done, canceled.

<abstract>

Two tasks, delivered in order. T1 makes the four book pages navigable and render well; T2 authors the code tours and the test that validates them. T1 is first because T2's index section edits the README T1 rewrites.

</abstract>

<tasks>

## Tasks

Group tasks into milestones, each a result a person can check. One task is one pull request in one repository, sized for review: aim under about 300 changed lines and 10 files, and split a task that would grow past that before its pull request opens. The workspace's `spec.sizeBudget` in `ua-checks.yaml`, when declared, refuses larger commits and pull requests.

### T1: Book navigation and rendering pass  [done]

**Milestone:** M1, the book reads as a guided site. **Repository:** delware-project. **Size:** 4 files, ~220 changed lines.

**Depends on:** none

**Acceptance criteria:**

- [x] `book/README.md` states the reading order with one-line descriptions, a Mermaid reading-map, and a tours section pointing at `.tours/`
- [x] overview, architecture, and quickstart each open with a breadcrumb to the index and a "what you'll learn" line, and end with prev/next links matching the README order
- [x] `book/architecture.md` carries a Mermaid flowchart with both inputs, both readers, process_dataset, both frames, the three analysis consumers, and the figure outputs; the ASCII art is gone
- [x] At most two GitHub alerts per page and at least one genuine `[!WARNING]`/`[!NOTE]` across the book
- [x] No file outside `book/` changes in this task

**Verification:** open each page; grep for `mermaid`, `[!WARNING]`, `« Prev` / `Next »`; `git diff --stat -- book/` shows exactly four files.

### T2: Code tours and their validation test  [done]

**Milestone:** M2, the code is annotated for later reading. **Repository:** delware-project. **Size:** 10 files, ~500 changed lines.

**Depends on:** T1 (README tours section must land on the rewritten index)

**Acceptance criteria:**

- [x] Eight tour files exist under `.tours/` covering `main.py` and all eight `src/delware_speech/` modules, chained by `nextTour` with `00-start-here` marked `isPrimary`
- [x] Every step has `title`, `file`, `line`, and a `description` naming the symbol it explains; every `file` is a tracked repo file and every `line` is within that file's current line count
- [x] `tests/test_tours.py` validates schema and anchors for every tour and passes
- [x] Full suite and lint stay green; no file under `src/` or `main.py` is modified

**Verification:** `/home/ducvu/.conda/envs/alzheimer-speech/bin/pytest -v tests/test_tours.py tests/` then `/home/ducvu/.conda/envs/alzheimer-speech/bin/flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503`.

</tasks>

<revisions>

## Revisions

Appended by `ultragentic docs revise <this file> "<what changed>"`. Do not edit dates by hand.

| Date | Change |
|------|--------|
| 2026-10-15 | Created. |
| 2026-10-15 | T2 sized for eight tour files (10 files, ~500 lines) after authoring; wording matches PLAN. |

</revisions>
