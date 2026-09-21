"""Main command-line entrypoint for Delaware Speech NLP replication.

Replicates and extends the study:
"Artificial intelligence-driven natural language processing for identifying linguistic patterns
in Alzheimer’s disease and mild cognitive impairment: A study of lexical, syntactic, and cohesive
features of speech through picture description tasks" (Nyongesa et al., 2025).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from delware_speech.clustering import (
    assign_cluster_domain_names,
    cluster_features_hierarchical,
    cluster_features_kmeans,
    compute_correlation_and_distance,
    evaluate_cluster_elbow_and_silhouette,
    get_numeric_feature_columns,
)
from delware_speech.importance import (
    benchmark_all_models,
    compute_feature_importance_rf,
    prepare_classification_data,
)
from delware_speech.pipeline import (
    process_dataset,
    select_unique_participants,
)
from delware_speech.statistical_analysis import (
    compute_cognitive_correlations,
    perform_ancova,
    perform_group_comparisons,
)
from delware_speech.visualization import (
    plot_cluster_correlation_matrix,
    plot_cognitive_regressions,
    plot_feature_importance,
    plot_task_radar,
    plot_tsne_clusters,
    plot_violin_features,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("delware_speech")

DEFAULT_CORPUS_ROOT = "/shared-data/dementiabank/Delaware"
DEFAULT_DEMO_EXCEL = "/shared-data/dementiabank/Delaware/demo-test-fixed.xlsx"
DEFAULT_DATA_DIR = "data"
DEFAULT_RESULTS_DIR = "results"
DEFAULT_FIGURES_DIR = "figures"


def run_pipeline(
    corpus_root: str = DEFAULT_CORPUS_ROOT,
    demo_excel: str = DEFAULT_DEMO_EXCEL,
    data_dir: str = DEFAULT_DATA_DIR,
    results_dir: str = DEFAULT_RESULTS_DIR,
    figures_dir: str = DEFAULT_FIGURES_DIR,
    do_process: bool = True,
    do_stats: bool = True,
    do_cluster: bool = True,
    do_importance: bool = True,
    do_visualize: bool = True,
) -> None:
    """Run specified or all pipeline stages end-to-end."""
    data_path = Path(data_dir)
    results_path = Path(results_dir)
    figures_path = Path(figures_dir)

    data_path.mkdir(parents=True, exist_ok=True)
    results_path.mkdir(parents=True, exist_ok=True)
    figures_path.mkdir(parents=True, exist_ok=True)

    all_csv = data_path / "processed_features_all.csv"
    unique_csv = data_path / "processed_features_unique.csv"

    # Step 1: Data Processing
    if do_process or not all_csv.exists():
        logger.info(f"1. Processing Delaware CHAT files from: {corpus_root}")
        df_all = process_dataset(corpus_root, demo_excel, show_progress=True)
        if df_all.empty:
            logger.error("Dataset processing produced empty DataFrame. Check paths.")
            return

        df_unique = select_unique_participants(df_all)
        logger.info(f"Processed {len(df_all)} task records, {len(df_unique)} unique participants.")

        df_all.to_csv(all_csv, index=False)
        df_unique.to_csv(unique_csv, index=False)
        try:
            df_all.to_excel(data_path / "processed_features_all.xlsx", index=False)
            df_unique.to_excel(data_path / "processed_features_unique.xlsx", index=False)
        except Exception as e:
            logger.warning(f"Could not write excel files: {e}")
    else:
        logger.info(f"Loading cached dataset from: {unique_csv}")
        df_all = pd.read_csv(all_csv)
        df_unique = pd.read_csv(unique_csv)

    feature_cols = get_numeric_feature_columns(df_unique)
    logger.info(f"Identified {len(feature_cols)} numeric linguistic feature columns.")

    # Step 2: Statistical Analysis
    if do_stats:
        logger.info("2. Performing ANOVA, Kruskal-Wallis, Effect Sizes, and ANCOVA...")
        stats_df = perform_group_comparisons(df_unique, feature_cols, group_col="Diagnosis")
        stats_csv = results_path / "statistical_comparisons.csv"
        stats_df.to_csv(stats_csv, index=False)
        logger.info(f"Saved group comparisons to {stats_csv}")

        ancova_df = perform_ancova(
            df_unique, feature_cols, group_col="Diagnosis", covariates=("Age", "Education_Years")
        )
        ancova_csv = results_path / "ancova_covariates_adjusted.csv"
        ancova_df.to_csv(ancova_csv, index=False)
        logger.info(f"Saved ANCOVA results to {ancova_csv}")

        corr_df = compute_cognitive_correlations(df_unique, feature_cols, score_col="MoCA")
        corr_csv = results_path / "moca_correlations.csv"
        corr_df.to_csv(corr_csv, index=False)
        logger.info(f"Saved MoCA cognitive score correlations to {corr_csv}")

    # Step 3: Clustering
    cluster_df = None
    corr_matrix = None
    if do_cluster:
        logger.info("3. Computing Correlation Matrix, 4-Cluster K-Means, and Hierarchical Clustering...")
        corr_matrix, dist_matrix = compute_correlation_and_distance(df_unique, feature_cols)

        # 4-Cluster K-Means
        kmeans_clusters, sil_score = cluster_features_kmeans(corr_matrix, n_clusters=4, random_state=42)
        kmeans_clusters = assign_cluster_domain_names(kmeans_clusters)
        kmeans_csv = results_path / "kmeans_clusters_k4.csv"
        kmeans_clusters.to_csv(kmeans_csv, index=False)
        logger.info(f"K-Means (k=4) Silhouette Score: {sil_score:.4f}. Saved to {kmeans_csv}")

        # Hierarchical Clustering (complete linkage)
        hc_clusters = cluster_features_hierarchical(corr_matrix, dist_matrix, n_clusters=4, method="complete")
        hc_clusters = assign_cluster_domain_names(hc_clusters)
        hc_csv = results_path / "hierarchical_clusters_k4.csv"
        hc_clusters.to_csv(hc_csv, index=False)

        # Elbow & Silhouette Evaluation
        eval_df = evaluate_cluster_elbow_and_silhouette(corr_matrix, k_range=range(2, 7))
        eval_csv = results_path / "cluster_validation_metrics.csv"
        eval_df.to_csv(eval_csv, index=False)

        cluster_df = kmeans_clusters

    # Step 4: Machine Learning & Feature Importance
    importance_df = None
    if do_importance:
        logger.info("4. Running Random Forest 10-Fold CV & Gini Feature Importance...")
        X, y, feats, classes = prepare_classification_data(df_unique, target_col="Diagnosis", feature_cols=feature_cols)
        logger.info(f"Classification dataset: {len(X)} samples across classes {classes}")

        importance_df = compute_feature_importance_rf(X, y, feats, n_estimators=100, random_state=42)
        imp_csv = results_path / "feature_importance_rf.csv"
        importance_df.to_csv(imp_csv, index=False)
        top5 = importance_df.head(5)[["Rank", "Feature", "Importance_Score"]]
        logger.info(f"Top 5 most predictive features:\n{top5}")

        # Model benchmark (RF vs SVM vs Gradient Boosting)
        benchmark_df = benchmark_all_models(X, y, random_state=42)
        bench_csv = results_path / "model_benchmark_comparison.csv"
        benchmark_df.to_csv(bench_csv, index=False)
        logger.info(f"Model CV Benchmarks:\n{benchmark_df}")

    # Step 5: Visualizations
    if do_visualize:
        logger.info("5. Generating Publication-Quality Figures...")
        if corr_matrix is None or cluster_df is None:
            corr_matrix, _ = compute_correlation_and_distance(df_unique, feature_cols)
            cluster_df, _ = cluster_features_kmeans(corr_matrix, n_clusters=4)

        # Fig 3: Clustered heatmap and t-SNE
        plot_cluster_correlation_matrix(corr_matrix, cluster_df, figures_path / "Figure3_Correlation_Matrix.png")
        plot_tsne_clusters(corr_matrix, cluster_df, figures_path / "Figure3_tSNE_Clusters.png")

        # Feature importance bar plot
        if importance_df is not None:
            plot_feature_importance(importance_df, figures_path / "Figure_Feature_Importance_Top20.png", top_n=20)

        # Fig 5: Violin plots of key features
        key_violin_feats = [
            "hypernym_count", "open_class_words_rate", "syntactic_complexity",
            "coleman_liau_index", "pronouns_rate", "spatial_deixis_rate",
            "adverbs_rate", "personal_deixis_rate", "past_tense_rate",
        ]
        plot_violin_features(
            df_unique, key_violin_feats, figures_path / "Figure5_Feature_Violins.png", group_col="Diagnosis"
        )

        # Fig 6: Cognitive correlations
        key_regr_feats = [
            "syntactic_complexity", "coleman_liau_index", "pronouns_rate",
            "spatial_deixis_rate", "adverbs_rate", "past_tense_rate",
        ]
        plot_cognitive_regressions(
            df_unique, key_regr_feats, figures_path / "Figure6_MoCA_Regressions.png", score_col="MoCA"
        )

        # Fig 4b: Task radar plots
        radar_feats = [
            "pronouns_rate", "spatial_deixis_rate", "syntactic_complexity",
            "past_tense_rate", "open_class_words_rate",
        ]
        plot_task_radar(df_all, radar_feats, figures_path / "Figure4_Task_Radar.png")

        logger.info(f"All figures generated and saved to {figures_path}/")

    logger.info("Pipeline execution complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Delaware Speech NLP pipeline (Nyongesa et al., 2025)")
    parser.add_argument("--all", action="store_true", help="Execute complete pipeline end-to-end")
    parser.add_argument("--process", action="store_true", help="Process raw transcripts and demographics")
    parser.add_argument("--stats", action="store_true", help="Run statistical analysis and correlations")
    parser.add_argument("--cluster", action="store_true", help="Run correlation clustering and t-SNE")
    parser.add_argument("--importance", action="store_true", help="Run ML classification and feature importance")
    parser.add_argument("--visualize", action="store_true", help="Generate publication figures")
    parser.add_argument("--corpus-root", default=DEFAULT_CORPUS_ROOT, help="Path to Delaware dataset directory")
    parser.add_argument("--demo-excel", default=DEFAULT_DEMO_EXCEL, help="Path to demo-test-fixed.xlsx")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR, help="Directory to save clean datasets")
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR, help="Directory to save statistical outputs")
    parser.add_argument("--figures-dir", default=DEFAULT_FIGURES_DIR, help="Directory to save figure images")

    args = parser.parse_args()

    run_all = args.all or not any([args.process, args.stats, args.cluster, args.importance, args.visualize])

    run_pipeline(
        corpus_root=args.corpus_root,
        demo_excel=args.demo_excel,
        data_dir=args.data_dir,
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
        do_process=run_all or args.process,
        do_stats=run_all or args.stats,
        do_cluster=run_all or args.cluster,
        do_importance=run_all or args.importance,
        do_visualize=run_all or args.visualize,
    )


if __name__ == "__main__":
    main()
