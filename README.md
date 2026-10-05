# Delaware Speech NLP Analysis

Python re-implementation of the analysis pipeline in Nyongesa et al. (2025),
*"Artificial intelligence-driven natural language processing for identifying linguistic
patterns in Alzheimer's disease and mild cognitive impairment: A study of lexical,
syntactic, and cohesive features of speech through picture description tasks"*, run on
the DementiaBank **Delaware** corpus.

The pipeline parses CHAT picture-description transcripts, harmonizes demographics,
extracts the paper's 53-feature set (emitted as 63 columns: counts plus rates), and reproduces the paper's statistical comparisons,
feature clustering, Random Forest diagnosis model, and publication figures.

## Repository map

| Directory / file | Purpose |
|------------------|---------|
| `src/delware_speech/` | The analysis package. Start with [its README](src/delware_speech/README.md) — a per-file map explaining each module's functions and why it was created |
| `book/` | Narrative documentation: [overview](book/overview.md), [architecture](book/architecture.md), [quickstart](book/quickstart.md) |
| `docs/` | Repo-level reference and working documents: per-module function reference in [docs/reference/](docs/reference/index.md), the replicated paper in `docs/paper/`, and dated run documents (`docs/<date>/<slug>/`) |
| `main.py` | CLI entrypoint: `python main.py --all` runs process → stats → cluster → importance → visualize |
| `tests/` | Unit tests: six files covering every module except `visualization` (`pytest tests/`) |
| `data/` | Pipeline output: processed feature datasets (all task records and unique participants) |
| `results/` | Pipeline output: statistical tables, cluster assignments, importance rankings, model benchmarks |
| `figures/` | Pipeline output: the paper's Figures 3–6 and the importance chart as PNGs |
| `reference_repo/speech/` | The original authors' scripts (numbered Python scripts + `Cluster_Analysis.R`, `Importance_Features.R`, `t-SNE_PLOTS_.R`), kept for comparison |
| `tasks.json` | Implementation task ledger (T1–T6) mapping work to modules |
| `vibe-checks.yaml` | Check plan: tests, lint, and delivery verification |

## Where to read first

| Question | Go to |
|----------|-------|
| What does this project do? | [book/overview.md](book/overview.md) |
| What does file X in `src/` do, and why does it exist? | [src/delware_speech/README.md](src/delware_speech/README.md) |
| How do I run it? | [book/quickstart.md](book/quickstart.md) |
| How do the pieces fit together? | [book/architecture.md](book/architecture.md) |
| What exactly does function `f()` do? | [docs/reference/index.md](docs/reference/index.md) |

## Quick start

```sh
PYTHONPATH=src python main.py --all --corpus-root /path/to/Delaware \
  --demo-excel /path/to/Delaware/demo-test-fixed.xlsx
pytest tests/ -v
```

See [book/quickstart.md](book/quickstart.md) for dependencies, one-stage runs, and
troubleshooting.

## Documentation layout note

Documentation is split by audience, following the pattern of an mdBook-style `book/`
for narrative docs plus a `docs/` tree for reference material: `book/` explains the
study, the architecture, and how to run things; `docs/reference/` documents every
module function; `src/delware_speech/README.md` maps each source file to its purpose
and its counterpart in the original paper scripts.
