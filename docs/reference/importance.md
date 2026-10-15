# `importance` — feature importance and diagnostic classification

Source: `src/delware_speech/importance.py` (143 lines).
Replicates `reference_repo/speech/Importance_Features.R` and the paper's modeling.
Unit tests: `tests/test_clustering_importance.py`.

## What it does

Builds a diagnosis-classification problem from the feature table, ranks features by
Random Forest Gini importance (the paper's top-20 list), and benchmarks three
classifiers under identical cross-validation.

## Functions

### `prepare_classification_data(df, target_col="Diagnosis", feature_cols=None) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]`

1. Drops rows with a missing target; strips label whitespace.
2. Removes rows whose label is `other`/`unknown`/`nan` (case-insensitive) — only
   meaningful diagnostic classes remain.
3. Uses `get_numeric_feature_columns` when `feature_cols` is `None`.
4. Median-imputes missing feature values (`SimpleImputer(strategy="median")`).

Returns `(X, y, feature_cols, valid_classes)`.

### `evaluate_classifier_cv(clf, X, y, n_splits=10, random_state=42) -> Dict[str, float]`

Stratified, shuffled `n_splits`-fold CV. **Inside each fold** the features are
standardized (`StandardScaler` fit on the training fold only — no leakage into the test
fold), the classifier is fit and predicts, and the fold contributes:

- raw accuracy,
- Cohen's kappa (0.0 on degenerate folds),
- balanced accuracy (mean per-class recall over the classes present in the fold).

Returns means and SDs: `Accuracy_Mean`, `Accuracy_Std`, `Kappa_Mean`, `Kappa_Std`,
`Balanced_Acc_Mean`.

### `compute_feature_importance_rf(X, y, feature_names, n_estimators=100, random_state=42) -> pd.DataFrame`

Scales all rows, fits `RandomForestClassifier(n_estimators=100, max_features="sqrt")`,
and returns a ranked frame: `Feature`, `Importance_Gini` (raw), `Importance_Score`
(raw × 100), `Rank` (1 = most predictive). The top 20 rows of this frame are the
paper's headline feature list, and the input to
`visualization.plot_feature_importance`.

### `benchmark_all_models(X, y, random_state=42) -> pd.DataFrame`

Runs `evaluate_classifier_cv` with `n_splits=10` for the paper's three models:

| Model | Estimator |
|-------|-----------|
| Random Forest | `RandomForestClassifier(n_estimators=100)` |
| SVM (RBF) | `SVC(kernel="rbf")` |
| Gradient Boosting | `GradientBoostingClassifier()` |

Returns one row per model with the five CV metrics.

## Notes for reviewers

- Imputation happens **once, before** CV (on the full X), while scaling happens per
  fold. Medians therefore see the whole dataset — acceptable for medians, but worth
  knowing when judging the paper's leakage posture.
- `compute_feature_importance_rf` fits on all rows (in-sample); the ranking is not cross-validated.
- All stochastic steps are seeded (`random_state=42`); re-runs are deterministic.
- This module trains on the **unique-participant** dataset in `main.py` — one row per
  person, so CV folds never split one person's tasks across train and test.
