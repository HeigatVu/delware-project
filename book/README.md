# The Delaware Speech NLP book

Narrative documentation for this repository, in the spirit of an mdBook: read the
pages in order for a guided tour, or jump to what you need. Per-function reference
material lives separately in `docs/reference/`; the source map lives in
`src/delware_speech/README.md`.

## Pages

1. **[Overview](overview.md)** — the study being replicated, the corpus, and what the
   pipeline produces. Start here.
2. **[Architecture](architecture.md)** — how the modules fit together, the data flow
   from `.cha` transcripts to figures, and the design decisions worth knowing before
   changing code.
3. **[Quickstart](quickstart.md)** — install, point the pipeline at the Delaware
   dataset, run all or part of it, and find the outputs.

## What this repository is, in one paragraph

A faithful Python re-implementation of the analysis in Nyongesa et al. (2025), which
extracted 53 linguistic features from picture-description speech on the DementiaBank
Delaware corpus and used them to characterize and classify Alzheimer's disease and
MCI. The original study shipped numbered Python scripts and three R scripts; this
repository reorganizes the same analysis into one importable package
(`src/delware_speech/`), driven by a single CLI (`main.py`), with unit tests and
deterministic seeds. The original scripts are kept for comparison in
`reference_repo/speech/`.

## Reading paths

| If you want to… | Read |
|---|---|
| Understand the study and its claims | `book/overview.md` |
| Review or modify the code | `src/delware_speech/README.md`, then `book/architecture.md` |
| Look up one function's behavior | `docs/reference/<module>.md` |
| Run the pipeline on data | `book/quickstart.md` |
| Compare against the original R/Python scripts | `reference_repo/speech/` |
