# Architecture — how the pipeline fits together

## The module graph

```
                 .cha transcripts            demo-test-fixed.xlsx
                        │                            │
                        ▼                            ▼
               chat_reader.parse_cha_file   demographics.load_delaware_demographics
                        │                            │
                        └──────────┬─────────────────┘
                                   ▼
                     pipeline.process_dataset          (per file: features.
                               │                        extract_linguistic_features)
                               ▼
              ┌── data/processed_features_all.csv ──┐
              │            │                        │
              │  pipeline.select_unique_participants │
              │            │                        │
              ▼            ▼                        ▼
   data/processed_features_unique.csv      plot_task_radar (uses ALL task rows)
              │
      ┌───────┼──────────────────────┐
      ▼       ▼                      ▼
statistical_  clustering         importance
analysis      │                  │
  │           │                  │
  │   corr_matrix ──► plot_cluster_correlation_matrix, plot_tsne_clusters
  │           │
  │      importance_df ──► plot_feature_importance
  ▼           ▼
results/*.csv  figures/*.png
```

## Stage by stage

### 1. Ingest (`chat_reader`, `demographics`)

Two independent readers, one per raw input format. `chat_reader.parse_cha_file` is the
only code that understands CHAT; `demographics.load_delaware_demographics` is the only
code that understands the workbook. Everything downstream speaks pandas and canonical
names (`Cookie`/`Cat`/`Rockwell`, education years, one MoCA column).

### 2. Assemble (`pipeline`)

`process_dataset` walks the corpus and builds the **all-tasks** frame; one transcript
contributing zero or more rows (one per canonical picture task present).
`select_unique_participants` reduces it to the **unique-participants** frame using the
paper's priority (Cookie > Cat > Rockwell) and earliest visit. Demographics are joined
inside `process_single_cha` by exact `ID` match, with transcript-header fields as
fallback.

Why two frames: the inferential statistics need one speech sample per person (else one
person's three tasks inflate n), while the task-comparison radar explicitly needs
every task row.

### 3. Quantify (`features`)

`extract_linguistic_features` is a pure function from text to a flat numeric dict —
no corpus knowledge, no file I/O. All NLP models (SpaCy, NLTK, TextStat, TextBlob)
are lazy-loaded module globals, so importing the package is cheap and model loading
happens once. Every returned dict has the same 63 keys, even for empty input.

### 4. Analyze (`statistical_analysis`, `clustering`, `importance`)

Three independent consumers of the feature frames:

- **statistical_analysis** — per-feature hypothesis tests across `Diagnosis` groups
  and correlations against `MoCA`, always with effect sizes and multiple-testing
  correction. No randomness.
- **clustering** — operates on the *feature × feature* correlation matrix (rows are
  features, not participants). Both a hierarchical and a K-Means view are produced so
  the paper's four-domain claim can be checked against two algorithms; the
  elbow/silhouette table is the evidence for k = 4.
- **importance** — supervised learning on the unique-participants frame: stratified
  10-fold CV with per-fold scaling (no leakage), Random Forest Gini ranking, and the
  three-model benchmark.

### 5. Render (`visualization`)

Six figure functions, each taking already-computed frames — plotting never recomputes
analysis (the one exception: if clustering was skipped, the correlation matrix is
recomputed on the fly so Figure 3 can still render; the importance chart is drawn only if `--importance` ran in
the same invocation). The `Agg` backend is forced at
import time: figures are files, never windows.

## The wiring: `main.py`

`main.py` is a thin CLI over the five stages, each togglable (`--process`, `--stats`,
`--cluster`, `--importance`, `--visualize`, or `--all`). Conveniences worth knowing:

- **Caching**: `--all` (or no flag) always re-processes the corpus. With specific stage
  flags and no `--process`, the datasets are loaded from `data/processed_features_all.csv`
  and `data/processed_features_unique.csv` when they exist (processing runs if they do not).
- **Stage hand-off**: stages pass DataFrames in memory; CSVs are written for the
  record. The visualization stage receives the in-memory frames from earlier stages in
  the same run.
- **Paths**: corpus root, workbook, and the three output directories are all CLI
  arguments with defaults (see `book/quickstart.md`).

## Design decisions a reviewer should know

| Decision | Where | Rationale |
|----------|-------|-----------|
| Disfluencies are preserved, not cleaned away | `chat_reader.clean_chat_utterance` | Disfluency rate is a study feature |
| Per-file error containment in batch processing | `pipeline.process_dataset` | One malformed transcript must not kill a corpus run |
| Zeroed, schema-complete dict for empty text | `features._empty_feature_dict` | Downstream frames always share columns |
| Per-metric try/except in feature extraction | `features.extract_linguistic_features` | A failing readability metric yields 0.0, not a crash |
| `StandardScaler` fit inside each CV fold | `importance.evaluate_classifier_cv` | Prevents scale leakage between train and test folds |
| Medians imputed before CV (not per fold) | `importance.prepare_classification_data` | Documented trade-off; see `docs/reference/importance.md` |
| `random_state=42` everywhere stochastic | clustering, importance, t-SNE | Deterministic re-runs |
| Correlation features, not participants, are clustered | `clustering` | The paper's question is which features group together |
| Radar plots use the all-tasks frame | `main.py` | Task comparison needs every task, not one per person |

## Where the tests sit

Six test files cover every module except `visualization` (`clustering` and `importance`
share one file; figures are checked by regenerating them and inspecting the PNGs). Run everything with
`pytest tests/` (see `book/quickstart.md`).
