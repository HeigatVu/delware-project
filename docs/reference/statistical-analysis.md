# `statistical_analysis` — group comparisons, ANCOVA, cognition correlations

Source: `src/delware_speech/statistical_analysis.py` (233 lines).
Replicates `reference_repo/speech/05_linguistic_statistical_analysis.py`.
Unit tests: `tests/test_statistical_analysis.py`.

## What it does

The paper's inferential layer over the feature table: whether linguistic features
separate diagnostic groups (with effect sizes and multiple-testing correction), whether
differences survive adjustment for age and education, and whether features track the
MoCA cognitive score.

## Functions

### `compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float`

Cohen's d using the pooled standard deviation; `0.0` when either group has fewer than
two values or the pooled SD is zero.

### `perform_group_comparisons(df, features, group_col="Diagnosis") -> pd.DataFrame`

Per feature (one row per feature):

- Per-group `Mean_<g>` and `SD_<g>` columns.
- **ANOVA** — `stats.f_oneway`: `ANOVA_F`, `ANOVA_p`, plus partial eta-squared
  (`SS_between / SS_total`).
- **Kruskal–Wallis** — `stats.kruskal`: `Kruskal_H`, `Kruskal_p`, plus epsilon-squared
  `(H − k + 1) / (n − k)`.
- **Cohen's d** — `Cohen_d` when the frame has exactly two groups.
- **Correction** — across features: `ANOVA_p_FDR` (Benjamini–Hochberg) and
  `ANOVA_p_Bonferroni`.

Features with fewer than two populated groups are skipped.

### `perform_ancova(df, features, group_col="Diagnosis", covariates=("Age", "Education_Years")) -> pd.DataFrame`

Per feature, on rows complete in covariates + group and with ≥10 non-null feature
values: fits OLS

```
Q('<feature>') ~ C(Q('<Diagnosis>')) + Q('<Age>') + Q('<Education_Years>')
```

and records `ANCOVA_F`, `Group_Coefficient`, `Group_p`, `Model_R2`, `Model_Adj_R2`,
plus `Group_p_FDR` across features. `ANCOVA_F` is the whole-model F (covariates included);
`Group_Coefficient`/`Group_p` belong to the first group dummy, which is the full group effect
only with exactly two groups (Control/MCI in the current data). Failures are logged at debug level and that feature
is simply absent from the output.

### `compute_cognitive_correlations(df, features, score_col="MoCA") -> pd.DataFrame`

Per feature, on rows with a non-null score and ≥5 complete pairs, skipping
zero-variance pairs:

- `Pearson_r`, `Pearson_p`, `R_Squared` (r²), `Pearson_p_FDR` across features.
- `Spearman_rho`, `Spearman_p` (rank correlation, robust to outliers).
- `Slope_B`, `Intercept`, `Std_Error` from `stats.linregress`.
- `N` — the number of complete pairs the correlation used.

## Notes for reviewers

- Two correction families are used: FDR for the feature-level tables, Bonferroni reported
  alongside for the ANOVA table (not cross-checked against the paper's tables).
- Group *labels* come straight from the `Diagnosis` column — `Control`, `MCI`,
  `PossibleAD`, `Other` — so the class cleanup performed by
  `importance.prepare_classification_data` does **not** apply here; the stats functions
  include whatever labels are present.
