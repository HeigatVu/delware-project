# Generated outputs

The pipeline writes each result beside the other outputs for the same analysis. Files appear when their stage runs. Use `--output-dir` to choose another root; `--data-dir`, `--results-dir`, and `--figures-dir` remain available as overrides.

| Folder | What it contains |
|---|---|
| [processed-data/](processed-data/) | All task records and one row per participant |
| [group-comparisons/](group-comparisons/) | Diagnosis comparisons, ANCOVA, and feature distributions |
| [cognitive-scores/](cognitive-scores/) | Feature correlations and plots against MoCA |
| [clustering/](clustering/) | Cluster assignments, validation, correlation heatmap, and t-SNE |
| [classification/](classification/) | Model benchmarks and feature importance |
| [task-profiles/](task-profiles/) | Feature profiles across picture-description tasks |

## Processed data

- [All task records (CSV)](processed-data/processed_features_all.csv)
- [Unique participants (CSV)](processed-data/processed_features_unique.csv)
- [All task records (Excel)](processed-data/processed_features_all.xlsx)

## Group comparisons

- [Statistical comparisons](group-comparisons/statistical_comparisons.csv)
- [ANCOVA adjusted for age and education](group-comparisons/ancova_covariates_adjusted.csv)
- [Feature distributions by diagnosis](group-comparisons/Figure5_Feature_Violins.png)

## Cognitive scores

- [Feature correlations with MoCA](cognitive-scores/moca_correlations.csv)
- [MoCA regression plots](cognitive-scores/Figure6_MoCA_Regressions.png)

## Clustering

- [K-means assignments](clustering/kmeans_clusters_k4.csv)
- [Hierarchical assignments](clustering/hierarchical_clusters_k4.csv)
- [Cluster validation metrics](clustering/cluster_validation_metrics.csv)
- [Clustered correlation matrix](clustering/Figure3_Correlation_Matrix.png)
- [t-SNE cluster plot](clustering/Figure3_tSNE_Clusters.png)

## Classification

- [Random Forest feature importance](classification/feature_importance_rf.csv)
- [Model benchmarks](classification/model_benchmark_comparison.csv)
- [Top 20 feature importance plot](classification/Figure_Feature_Importance_Top20.png)

## Task profiles

- [Feature profiles by picture-description task](task-profiles/Figure4_Task_Radar.png)
