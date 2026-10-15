# `visualization` — publication figures

Source: `src/delware_speech/visualization.py` (308 lines).
Replicates the plotting of `reference_repo/speech/Cluster_Analysis.R`,
`Importance_Features.R`, and `t-SNE_PLOTS_.R` in Matplotlib/Seaborn.
Verified by the figure files produced under `output/` in end-to-end runs (no unit
tests — see "Testing" below).

## What it does

Regenerates the paper's Figures 3–6 and the feature-importance chart from pipeline
outputs. Every function writes a 300-dpi PNG and creates its output directory; the
non-interactive `Agg` backend is forced at import so everything works headless.

## Constants

- `CLUSTER_PALETTE` — `["#562a79", "#62b8d7", "#de8b44", "#bc2a21"]` (purple, blue,
  orange, red) for cluster labels.
- `DIAGNOSIS_PALETTE` — `Control` `#2b83ba`, `MCI` `#fdae61`, `PossibleAD` `#d7191c`
  (currently unused by any plot).

## Functions

### `plot_cluster_correlation_matrix(corr_matrix, cluster_df, output_path)`

Figure 3 (heatmap). Orders the correlation matrix by cluster assignment so domain
blocks are visible, then draws a diverging seaborn heatmap (vmin −1, vmax 1, center 0,
square cells). Title: *"Linguistic Feature Multi-Pass Correlation Matrix & Clusters"*.

### `plot_tsne_clusters(corr_matrix, cluster_df, output_path, random_state=42)`

Figure 3 (companion). 2-D t-SNE of the feature correlation profiles — rows are
features, so points are features colored by cluster. Perplexity adapts to the feature
count: `min(10, max(2, n_features // 4))`, 1000 iterations. Modelled on
`t-SNE_PLOTS_.R` (settings not diffed line by line).

### `plot_feature_importance(importance_df, output_path, top_n=20)`

Horizontal bar chart of the top-N features by `Importance_Score` (Gini × 100), value
labels on each bar. Input: the frame from `importance.compute_feature_importance_rf`.

### `plot_violin_features(df, features_to_plot, output_path, group_col="Diagnosis")`

Figure 5. Grid of violin plots (3 per row, quartiles inside, `cut=0` so violins stop
at the data) of the selected features split by diagnosis. Unused axes are switched
off; missing feature columns are skipped silently.

### `plot_cognitive_regressions(df, features_to_plot, output_path, score_col="MoCA", group_col="Diagnosis")`

Figure 6. Grid of scatter + regression plots (seaborn `regplot`, blue points, red line)
of each feature against the cognitive score; each panel title carries that panel's
Pearson r. Panels with fewer than 5 complete pairs are left empty.

### `plot_task_radar(df, features_to_plot, output_path, task_col="Task", group_col="Diagnosis")`

Figure 4(b). One polar subplot per picture task present among `Cookie`, `Cat`, `Rockwell` (only if none
of those exist does it fall back to the first three task values); features are standardized
across the whole dataset (z-scores) before averaging per diagnosis group so the radar
scales are comparable; each group is a filled polygon. Requires ≥3 valid features.

## Which inputs feed which figure

| Figure | Data source (written by `main.py`) |
|--------|-------------------------------------|
| Correlation matrix, t-SNE | `corr_matrix` + K-Means `cluster_df` (recomputed on the fly if clustering was skipped) |
| Importance bar chart | in-memory `importance_df`; drawn only when `--importance` ran in the same invocation (the CSV is written, not re-read) |
| Violins | `output/speech-features/processed-data/processed_features_unique.csv`, selected features |
| Regressions | `output/speech-features/processed-data/processed_features_unique.csv`, selected features |
| Radar | `output/speech-features/processed-data/processed_features_all.csv` (all task rows, not unique) |

## Testing

Plotting code has no unit tests in `tests/`; correctness is checked visually against
the paper's figures via the PNGs in `output/` produced by end-to-end runs
(`python main.py --visualize`). The z-scored radar and the adaptive t-SNE perplexity
are the two spots where output depends on data shape.
