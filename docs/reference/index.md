# Module reference

Repo-level reference for `src/delware_speech/`. One page per module: every public
function with its signature, inputs, outputs, and the paper artifact it replicates.
The per-file narrative map lives in `src/delware_speech/README.md`; the guided tour
lives in `book/`.

| Module | Reference page | Replicates |
|--------|----------------|------------|
| CHAT transcript parser | [chat-reader.md](chat-reader.md) | `01_convert_cha_to_txt.py` |
| Demographics harmonizer | [demographics.md](demographics.md) | `02_demographics_summary_processing.py` |
| Linguistic feature extraction | [features.md](features.md) | `04_nlp_linguistic_feature_extraction.py` |
| Dataset processing & orchestration | [pipeline.md](pipeline.md) | `03_process_text_files.py` |
| Statistical analysis | [statistical-analysis.md](statistical-analysis.md) | `05_linguistic_statistical_analysis.py` |
| Feature clustering | [clustering.md](clustering.md) | `Cluster_Analysis.R` |
| Feature importance & classification | [importance.md](importance.md) | `Importance_Features.R` |
| Figures | [visualization.md](visualization.md) | `t-SNE_PLOTS_.R` + R plot code |

Reference scripts live in `reference_repo/speech/` (the authors' original code).

Conventions across all modules:

- Determinism: every stochastic algorithm is seeded with `random_state=42`.
- Failure containment: per-feature/per-file errors are caught and logged, never fatal to
  a batch run; empty inputs return zeroed, schema-complete values.
- Data flow: pandas DataFrames in and out; one row = one task record
  (until `select_unique_participants` reduces to one row per participant).
