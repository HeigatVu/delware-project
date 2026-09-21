"""Tests for clustering and importance modules."""

import numpy as np
import pandas as pd
from delware_speech.clustering import (
    compute_correlation_and_distance,
    cluster_features_kmeans,
    cluster_features_hierarchical,
    evaluate_cluster_elbow_and_silhouette,
)
from delware_speech.importance import (
    prepare_classification_data,
    evaluate_classifier_cv,
    compute_feature_importance_rf,
    benchmark_all_models,
)
from sklearn.ensemble import RandomForestClassifier


def test_clustering_kmeans_and_hierarchical():
    np.random.seed(42)
    n_samples = 40
    data = {
        f"feat_{i}": np.random.normal(0, 1, n_samples) for i in range(10)
    }
    # Make feat_0, feat_1 correlated
    data["feat_1"] = data["feat_0"] + np.random.normal(0, 0.1, n_samples)
    df = pd.DataFrame(data)

    feature_cols = list(data.keys())
    corr_matrix, dist_matrix = compute_correlation_and_distance(df, feature_cols)
    assert corr_matrix.shape == (10, 10)
    assert dist_matrix.shape == (10, 10)
    assert np.all(np.diag(dist_matrix) == 0.0)

    # Test K-Means
    km_df, sil_score = cluster_features_kmeans(corr_matrix, n_clusters=3, random_state=42)
    assert len(km_df) == 10
    assert "Cluster" in km_df.columns
    assert -1.0 <= sil_score <= 1.0

    # Test Hierarchical
    hc_df = cluster_features_hierarchical(corr_matrix, dist_matrix, n_clusters=3, method="complete")
    assert len(hc_df) == 10
    assert len(hc_df["Cluster"].unique()) <= 3

    # Test Elbow and Silhouette
    eval_df = evaluate_cluster_elbow_and_silhouette(corr_matrix, k_range=range(2, 5))
    assert len(eval_df) == 3
    assert "Inertia" in eval_df.columns
    assert "Silhouette_Score" in eval_df.columns


def test_importance_and_benchmarks():
    np.random.seed(42)
    n = 30
    df = pd.DataFrame({
        "Diagnosis": ["Control"] * n + ["MCI"] * n,
        "f1": list(np.random.normal(5, 1, n)) + list(np.random.normal(1, 1, n)),
        "f2": list(np.random.normal(0, 1, n)) + list(np.random.normal(0, 1, n)),
        "f3": list(np.random.normal(2, 1, n)) + list(np.random.normal(4, 1, n)),
    })

    X, y, feats, classes = prepare_classification_data(df, target_col="Diagnosis", feature_cols=["f1", "f2", "f3"])
    assert X.shape == (2 * n, 3)
    assert len(y) == 2 * n

    rf = RandomForestClassifier(n_estimators=10, random_state=42)
    metrics = evaluate_classifier_cv(rf, X, y, n_splits=3)
    assert "Accuracy_Mean" in metrics
    assert metrics["Accuracy_Mean"] > 0.7  # f1 strongly separates

    imp_df = compute_feature_importance_rf(X, y, feats, n_estimators=10)
    assert len(imp_df) == 3
    assert imp_df.iloc[0]["Feature"] in ("f1", "f3")

    bench = benchmark_all_models(X, y)
    assert len(bench) == 3
    assert "Model" in bench.columns
