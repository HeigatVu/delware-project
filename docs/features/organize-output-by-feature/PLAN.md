---
type: PLAN
category: features
slug: organize-output-by-feature
title: "Plan: grouped pipeline outputs"
description: "Move current products, route future runs to the same feature folders, and update navigation."
status: draft
created: 2026-10-16
updated: 2026-10-16
---

# Plan: grouped pipeline outputs

<abstract>

Move existing files first, then route future runs into the same feature groups, and finally update navigation and verify all paths.

</abstract>

<approach>

## Steps

1. Map current CSV and figure outputs to the feature folders in the SPEC, then move the tracked files without changing their contents.
2. Update `main.py` to use `output/` by default and preserve the existing directory override flags.
3. Add an output index, revise the repository and book references, and add a focused pipeline path test.
4. Run the focused test, tour anchor test, full test suite, lint, and docs checks.

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

</revisions>
