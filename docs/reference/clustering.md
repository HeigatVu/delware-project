# `clustering` — feature-domain discovery

Source: `src/delware_speech/clustering.py` (124 lines).
Replicates `reference_repo/speech/Cluster_Analysis.R`.
Unit tests: `tests/test_clustering_importance.py`.

## What it does

Takes the participant-level feature table, correlates the linguistic features with each
other, clusters the correlation profiles, validates the number of clusters, and labels
each cluster with an interpretive clinical domain — the analysis behind the paper's
claim that the many features collapse into a handful of meaningful domains.

## Constants

### `EXCLUDE_NON_FEATURE_COLS`

Columns that must never enter a correlation: identifiers and demographics
(`ID`, `Record_ID`, `Visit_Number`, `Task`, `Task_Raw`, `Age`, `Sex`,
`Education_Code`, `Education_Years`, `Diagnosis`, `MoCA`, `Participant_Text`) and the
raw counts (`total_counts`, `word_count`, `sentence_count`) whose scale would dominate.

## Functions

### `get_numeric_feature_columns(df: pd.DataFrame) -> List[str]`

Numeric columns minus the excluded set, minus zero-variance columns. This function is
the single definition of "which columns are features" and is reused by `importance.py`.

### `compute_correlation_and_distance(df, feature_cols) -> Tuple[pd.DataFrame, np.ndarray]`

Pearson correlation matrix between features (NaN rows dropped, missing correlations
filled with 0) and the distance matrix `D = 1 − R` clipped to `[0, 2]` with a zeroed
diagonal. Returns `(corr_matrix, dist_matrix)`.

### `cluster_features_hierarchical(corr_matrix, dist_matrix, n_clusters=4, method="complete") -> pd.DataFrame`

Converts the square distance matrix to condensed form, builds the linkage
(`method="complete"` matches the R script), cuts the tree at `n_clusters`
(`maxclust`), and returns a `Feature`/`Cluster` frame sorted by cluster then feature
name.

### `cluster_features_kmeans(corr_matrix, n_clusters=4, random_state=42) -> Tuple[pd.DataFrame, float]`

K-Means (`n_init=10`) on the raw correlation rows; returns the `Feature`/`Cluster`
frame (1-indexed to match the R output) and the silhouette score (`0.0` when only one
cluster is found).

### `evaluate_cluster_elbow_and_silhouette(corr_matrix, k_range=range(2, 7), random_state=42) -> pd.DataFrame`

For each k in `k_range`: K-Means inertia (the elbow curve) and silhouette score. This
is the evidence table behind choosing four clusters — inspect it before trusting any
fixed `n_clusters`.

### `assign_cluster_domain_names(cluster_df: pd.DataFrame) -> pd.DataFrame`

Labels each cluster by keyword-matching its member feature names:

| Member features contain | Domain label |
|---|---|
| `flesch`, `ttr`, `diversity`, `density`, `honore`, `brunet` | Readability & Lexical Diversity |
| `complexity`, `sentence_length`, `dale_chall`, `clauses`, `fog` | Complexity, Fluency & Structural Metrics |
| `polarity`, `subjectivity`, `deixis`, `tense`, `pronoun` | Sentiment, Temporal & Discourse Markers |
| anything else | Advanced Syntactic & Lexical Sophistication |

Adds the `Domain` column. The labels are interpretive (a reading aid), not derived by
the clustering itself — check a cluster's member list before quoting a domain name. On the
committed outputs the rules collapse: hierarchical gives all four clusters "Readability &
Lexical Diversity", and K-Means gives two distinct names (keyword order is first-match-wins).

## Notes for reviewers

- Both clustering views (hierarchical and K-Means) run on **features**, not
  participants: rows of the input matrix are features profiled by their correlations
  across participants.
- `random_state=42` is fixed everywhere so re-runs produce identical assignments.
