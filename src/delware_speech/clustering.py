"""Linguistic feature clustering module replicating Cluster_Analysis.R in Python.

Implements Pearson correlation-based distance matrices, hierarchical complete-linkage
clustering, 4-cluster K-Means, silhouette validation, and elbow curve analysis.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


EXCLUDE_NON_FEATURE_COLS = {
    "ID", "Record_ID", "Visit_Number", "Task", "Task_Raw", "Age", "Sex",
    "Education_Code", "Education_Years", "Diagnosis", "MoCA", "Participant_Text",
    "total_counts", "word_count", "sentence_count",
}


def get_numeric_feature_columns(df: pd.DataFrame) -> List[str]:
    """Filter columns to pure numeric linguistic features for clustering."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return [c for c in numeric_cols if c not in EXCLUDE_NON_FEATURE_COLS and df[c].std() > 0]


def compute_correlation_and_distance(
    df: pd.DataFrame,
    feature_cols: List[str],
) -> Tuple[pd.DataFrame, np.ndarray]:
    """Compute Pearson correlation matrix and distance matrix (1 - R)."""
    sub_df = df[feature_cols].dropna()
    corr_matrix = sub_df.corr(method="pearson").fillna(0.0)

    # Distance matrix D = 1 - R clipped to [0, 2]
    dist_matrix = np.clip(1.0 - corr_matrix.values, 0.0, 2.0)
    np.fill_diagonal(dist_matrix, 0.0)
    return corr_matrix, dist_matrix


def cluster_features_hierarchical(
    corr_matrix: pd.DataFrame,
    dist_matrix: np.ndarray,
    n_clusters: int = 4,
    method: str = "complete",
) -> pd.DataFrame:
    """Perform hierarchical clustering on linguistic features to find n_clusters."""
    # Convert square distance matrix to condensed 1D distance vector
    condensed_dist = squareform(dist_matrix, checks=False)
    hc_linkage = linkage(condensed_dist, method=method)

    # Cut tree at n_clusters
    labels = fcluster(hc_linkage, t=n_clusters, criterion="maxclust")

    cluster_df = pd.DataFrame({
        "Feature": corr_matrix.columns,
        "Cluster": labels,
    }).sort_values(by=["Cluster", "Feature"]).reset_index(drop=True)

    return cluster_df


def cluster_features_kmeans(
    corr_matrix: pd.DataFrame,
    n_clusters: int = 4,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, float]:
    """Perform K-Means clustering on feature correlation profiles."""
    X = corr_matrix.values
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)
    score = float(silhouette_score(X, labels)) if len(np.unique(labels)) > 1 else 0.0

    cluster_df = pd.DataFrame({
        "Feature": corr_matrix.columns,
        "Cluster": labels + 1,  # 1-indexed
    }).sort_values(by=["Cluster", "Feature"]).reset_index(drop=True)

    return cluster_df, score


def evaluate_cluster_elbow_and_silhouette(
    corr_matrix: pd.DataFrame,
    k_range: range = range(2, 7),
    random_state: int = 42,
) -> pd.DataFrame:
    """Evaluate elbow inertias and silhouette scores for k in k_range."""
    X = corr_matrix.values
    records = []
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = kmeans.fit_predict(X)
        sil = float(silhouette_score(X, labels)) if len(np.unique(labels)) > 1 else 0.0
        records.append({
            "k": k,
            "Inertia": float(kmeans.inertia_),
            "Silhouette_Score": sil,
        })
    return pd.DataFrame(records)


def assign_cluster_domain_names(cluster_df: pd.DataFrame) -> pd.DataFrame:
    """Assign interpretive clinical domain names to clusters based on characteristic features."""
    df = cluster_df.copy()
    domain_map: Dict[int, str] = {}

    for c in sorted(df["Cluster"].unique()):
        feats = df[df["Cluster"] == c]["Feature"].tolist()
        feat_str = " ".join(feats).lower()
        if any(w in feat_str for w in ["flesch", "ttr", "diversity", "density", "honore", "brunet"]):
            domain_map[c] = "Readability & Lexical Diversity"
        elif any(w in feat_str for w in ["complexity", "sentence_length", "dale_chall", "clauses", "fog"]):
            domain_map[c] = "Complexity, Fluency & Structural Metrics"
        elif any(w in feat_str for w in ["polarity", "subjectivity", "deixis", "tense", "pronoun"]):
            domain_map[c] = "Sentiment, Temporal & Discourse Markers"
        else:
            domain_map[c] = "Advanced Syntactic & Lexical Sophistication"

    df["Domain"] = df["Cluster"].map(domain_map)
    return df
