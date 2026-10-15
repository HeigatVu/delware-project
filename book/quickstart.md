[Book index](README.md) › **3 · Quickstart**

# Quickstart — install and run

*Install, choose input data, run stages, and find outputs.*

## Requirements

- Python 3.10+ (the development environment is a conda env named `alzheimer-speech`)
- The Delaware DementiaBank corpus: a directory of `.cha` transcripts (optionally under
  a `transcript/` subdirectory) plus the demographics workbook `demo-test-fixed.xlsx`
- SpaCy model and NLTK data, downloaded on first use (see step 2)

## 1. Install dependencies

From the repository root:

```sh
pip install pandas numpy scipy scikit-learn statsmodels spacy nltk
pip install textstat textblob tqdm openpyxl matplotlib seaborn
pip install flake8 pytest          # only if you want to lint/test
```

(There is no packaged `pyproject.toml`: run from the repository root with `PYTHONPATH=src`,
as in the commands below. `pytest` finds `src/` through `pytest.ini`.)

## 2. One-time model downloads

The feature extractor auto-downloads on first use, but you can pre-fetch to avoid
surprises mid-run:

```sh
python -m spacy download en_core_web_sm
python - <<'PY'
import nltk
for pkg in ("stopwords", "punkt", "words", "wordnet"):
    nltk.download(pkg)
PY
```

## 3. Run the whole pipeline

```sh
PYTHONPATH=src python main.py --all \
  --corpus-root /path/to/Delaware \
  --demo-excel  /path/to/Delaware/demo-test-fixed.xlsx
```

With no `--corpus-root`/`--demo-excel`, the built-in defaults point at the study's
shared-data mount (see `DEFAULT_CORPUS_ROOT` / `DEFAULT_DEMO_EXCEL` at the top of
`main.py` and override as needed). Outputs default to `output/`, grouped by
analysis feature. `--data-dir`, `--results-dir`, and `--figures-dir` remain
available when you need to override an individual output root.

> [!WARNING]
> If `--demo-excel` points at a missing workbook, `process_dataset` skips it
> silently and falls back to transcript-header metadata (`Diagnosis` defaults to
> `Control` when the header has none). A wrong path looks like a successful run
> with everything classified `Control` — check the merge happened (see
> Troubleshooting below).

Processing the full corpus is the slow part (feature extraction runs SpaCy per
transcript); expect a tqdm progress bar. `--all` (or no flag) always re-processes. Stage-only runs
(e.g. `--stats`) reuse `output/processed-data/processed_features_all.csv` when it exists; add `--process`
to force a re-parse.

## 4. Or run one stage at a time

```sh
PYTHONPATH=src python main.py --process     # transcripts + demographics -> output/processed-data/
PYTHONPATH=src python main.py --stats       # group comparisons, ANCOVA, MoCA correlations
PYTHONPATH=src python main.py --cluster     # correlation clustering + validation
PYTHONPATH=src python main.py --importance  # RF importance + model benchmark
PYTHONPATH=src python main.py --visualize   # figures (the importance chart also needs --importance in the same run)
```

Stage flags combine (`--stats --visualize`), and later stages load the cached
datasets from `output/processed-data/` automatically. `--visualize` alone still works even if
clustering was skipped: the correlation matrix is recomputed on the fly.

## 5. Run the tests

```sh
pytest tests/ -v
```

Six test files cover `chat_reader`, `demographics`, `features`, `pipeline`,
`statistical_analysis`, and `clustering`+`importance` (visualization is verified by
its output figures).

## 6. Check the outputs

| Folder | What it is |
|--------|------------|
| `output/processed-data/` | All task records and one row per participant |
| `output/group-comparisons/` | Diagnosis comparisons, ANCOVA, and feature distributions |
| `output/cognitive-scores/` | Feature correlations and plots against MoCA |
| `output/clustering/` | Cluster assignments, validation, correlation heatmap, and t-SNE |
| `output/classification/` | Model benchmarks and feature importance |
| `output/task-profiles/` | Feature profiles across picture-description tasks |

For links to each result file, see [`output/README.md`](../output/README.md).

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `No .cha files found under …` | Wrong `--corpus-root`; transcripts may live in a `transcript/` subdirectory (auto-detected) |
| Demographics not merged, no error shown | `--demo-excel` path wrong or missing: `process_dataset` skips a missing workbook silently and falls back to transcript-header metadata (`Diagnosis` defaults to `Control` when the header has none) |
| `OSError: model en_core_web_sm not found` mid-run | Run the SpaCy download in step 2 |
| `LookupError` for an NLTK corpus | Run the NLTK downloads in step 2 |
| Excel export warnings | `openpyxl` missing — CSVs are still written |
| Figures look empty for a feature | That feature had <5 complete pairs (regressions) or zero variance — see the relevant plot function's reference page |

---

« Previous: [2 · Architecture](architecture.md) · Back to the [book index](README.md) »
