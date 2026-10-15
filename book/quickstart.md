[Book index](README.md)

# Quickstart

Install the dependencies, provide the Delaware inputs, and run the stages you need.

## Requirements and install

Use Python 3.10 or newer. From the repository root:

```sh
pip install pandas numpy scipy scikit-learn statsmodels spacy nltk
pip install textstat textblob tqdm openpyxl matplotlib seaborn
```

There is no `pyproject.toml`; run commands with `PYTHONPATH=src`.

Download the language resources before the first full run:

```sh
python -m spacy download en_core_web_sm
python -c 'import nltk; [nltk.download(x) for x in ("stopwords", "punkt", "words", "wordnet")]'
```

## Run everything

```sh
PYTHONPATH=src python main.py --all \
  --corpus-root /path/to/Delaware \
  --demo-excel /path/to/Delaware/demo-test-fixed.xlsx
```

Without input flags, `main.py` uses the study data mount defaults. Outputs go to `output/`: transcript analyses under `output/speech-features/`, and MoCA analyses under `output/cognitive-scores/`. Use `--data-dir`, `--results-dir`, or `--figures-dir` to override output roots.

> **Check the workbook path.** If `--demo-excel` is missing, the pipeline silently uses transcript metadata. If diagnosis is absent there too, it defaults to `Control`.

## Run selected stages

```sh
PYTHONPATH=src python main.py --process     # parse transcripts and extract features
PYTHONPATH=src python main.py --stats       # group tests, ANCOVA, and MoCA correlations
PYTHONPATH=src python main.py --cluster     # cluster features and validate k
PYTHONPATH=src python main.py --importance  # rank features and compare classifiers
PYTHONPATH=src python main.py --visualize   # write figures
```

Stage flags can be combined. `--all` or no stage flag reparses the corpus; a stage-only run reuses cached data under `output/speech-features/processed-data/` when available. Add `--process` to force a fresh parse. The importance figure requires `--importance` in the same run.

See [`output/README.md`](../output/README.md) for links to generated files. Run `pytest tests/ -v` to check the code.

## Common fixes

| Problem | Check |
|---------|-------|
| No `.cha` files found | Check `--corpus-root`; transcripts may be in a `transcript/` subfolder. |
| SpaCy model or NLTK data missing | Run the downloads above. |
| Empty regression panels | The feature may have fewer than five complete pairs or no variance. |

[Previous: Architecture](architecture.md) · [Book index](README.md)
