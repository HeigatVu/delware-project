---
type: RESEARCH
category: features
slug: organize-output-by-feature
title: "Verify moved outputs with Git object identity"
description: "Explains how Git object identity verifies that moved outputs kept their contents."
status: draft
created: 2026-10-16
updated: 2026-10-16
---

# Verify moved outputs with Git object identity

Research digest: a question answered from cited sources, with what they mean for this work.

<abstract>

Can Git verify that output files kept their contents when moved into feature folders? Yes: compare the old and new blob identities. The Git documentation describes blobs as content objects, and the repository diff reports every moved output as an exact rename. This confirms preservation of tracked contents, not the scientific quality of those outputs.

</abstract>

<question>

## Question

Can the project's frozen file-preservation criterion be checked without rerunning the analysis pipeline? This digest covers the 17 tracked files moved in commit `233d5d8`, the local Git diff, and the official Git book; no domain or date comparison is needed.

</question>

<findings>

## Findings

The Git book describes Git as a content-addressable object store and explains that blob objects hold file content; the object key is computed from the stored content and its header ([Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)). In this repository, `git diff --name-status -M HEAD^ HEAD -- data results figures output` reports 17 `R100` moves. The inference is that these tracked artifacts retained their Git object contents while their paths changed.

## Applicability

| Source | Reuse, reject, or gap | Why |
|--------|-----------------------|-----|
| [Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) | Reuse | Git's content-addressed blobs provide a direct way to check that moved tracked files retained their contents. |

## Refine

Keep the planned file-preservation check: compare the source and destination paths and confirm their blob identities match. No analysis rerun is needed to check a directory-only move.

### Methodological gap

Git object identity checks tracked contents only. It does not establish that an output is scientifically valid or that the source data were processed correctly; those checks remain in the pipeline tests and review.

### Cross-domain mechanisms

Content-addressed storage is a version-control mechanism that transfers well to artifact migration: compare file identities before and after a path change to detect accidental edits without opening or regenerating each file.

## Map

```mermaid
flowchart LR
  Q[Did moved files keep their contents?] --> G[Git blob identity]
  G --> D[17 exact rename records]
  D --> R[Preservation criterion supported]
```

</findings>

<open_questions>

## Open questions

- None.

</open_questions>

<references>

## References

https://git-scm.com/book/en/v2/Git-Internals-Git-Objects

</references>

<revisions>

## Revisions

Appended by `ultragentic docs revise <this file> "<what changed>"`. Do not edit dates by hand.

| Date | Change |
|------|--------|
| 2026-10-16 | Created. |

</revisions>
