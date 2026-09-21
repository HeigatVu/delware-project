"""Visualization suite generating publication-grade figures matching Nyongesa et al. (2025).

Replaces R scripts (Cluster_Analysis.R, Importance_Features.R, t-SNE_PLOTS_.R)
with pure Python Matplotlib/Seaborn implementations:
- Figure 3: Clustered Correlation Heatmap & 2D t-SNE projection
- Figure 4: Task-specific Radar Plots
- Figure 5: Feature distribution Violin Plots across diagnostic groups
- Figure 6: Cognitive Score (MoCA) Scatter and Regression Plots
- Feature Importance: Top 20 predictive features bar chart
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.manifold import TSNE

matplotlib.use("Agg")  # Non-interactive backend for headless environments


# Color palettes matching paper aesthetics
CLUSTER_PALETTE = ["#562a79", "#62b8d7", "#de8b44", "#bc2a21"]
DIAGNOSIS_PALETTE = {"Control": "#2b83ba", "MCI": "#fdae61", "PossibleAD": "#d7191c"}


def plot_cluster_correlation_matrix(
    corr_matrix: pd.DataFrame,
    cluster_df: pd.DataFrame,
    output_path: Union[str, Path],
) -> None:
    """Plot clustered correlation matrix heatmap with domain blocks (Figure 3)."""
    # Sort correlation matrix by cluster
    sorted_df = cluster_df.sort_values(by="Cluster")
    ordered_feats = [f for f in sorted_df["Feature"] if f in corr_matrix.columns]
    sub_corr = corr_matrix.loc[ordered_feats, ordered_feats]

    fig, ax = plt.subplots(figsize=(14, 12), dpi=300)
    cmap = sns.diverging_palette(240, 10, as_cmap=True)
    sns.heatmap(
        sub_corr,
        cmap=cmap,
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        linewidths=0.2,
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation (r)"},
        ax=ax,
    )
    ax.set_title("Linguistic Feature Multi-Pass Correlation Matrix & Clusters", fontsize=14, weight="bold", pad=15)
    plt.xticks(rotation=90, fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_tsne_clusters(
    corr_matrix: pd.DataFrame,
    cluster_df: pd.DataFrame,
    output_path: Union[str, Path],
    random_state: int = 42,
) -> None:
    """Replicate t-SNE_PLOTS_.R: Project features into 2D space colored by cluster."""
    features = [f for f in cluster_df["Feature"] if f in corr_matrix.columns]
    X = corr_matrix.loc[features].values

    perplexity = min(10, max(2, len(features) // 4))
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=random_state, max_iter=1000)
    Y = tsne.fit_transform(X)

    merged = cluster_df.set_index("Feature").loc[features].reset_index()
    merged["TSNE1"] = Y[:, 0]
    merged["TSNE2"] = Y[:, 1]
    merged["Cluster_Label"] = merged["Cluster"].astype(str)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    clusters = sorted(merged["Cluster"].unique())

    for idx, c in enumerate(clusters):
        sub = merged[merged["Cluster"] == c]
        color = CLUSTER_PALETTE[idx % len(CLUSTER_PALETTE)]
        ax.scatter(sub["TSNE1"], sub["TSNE2"], c=color, label=f"Cluster {c}", s=90, alpha=0.85, edgecolors="none")

    ax.set_title("t-SNE Projection of Clustered Linguistic Domains", fontsize=14, weight="bold")
    ax.set_xlabel("t-SNE Dimension 1", fontsize=11)
    ax.set_ylabel("t-SNE Dimension 2", fontsize=11)
    ax.legend(title="Cluster", frameon=True, loc="upper right")
    sns.despine()
    plt.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_feature_importance(
    importance_df: pd.DataFrame,
    output_path: Union[str, Path],
    top_n: int = 20,
) -> None:
    """Plot top N predictive linguistic features ranked by Random Forest Gini impurity."""
    top_df = importance_df.head(top_n).sort_values(by="Importance_Score", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    y_pos = np.arange(len(top_df))
    bars = ax.barh(y_pos, top_df["Importance_Score"], color="#2c7bb6", alpha=0.85, edgecolor="#1a476f")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_df["Feature"], fontsize=9)
    ax.set_xlabel("Feature Importance (Mean Decrease in Gini)", fontsize=11)
    ax.set_title(f"Top {top_n} Diagnostic Linguistic Features (Random Forest)", fontsize=13, weight="bold")

    # Add numeric labels to bars
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.1, bar.get_y() + bar.get_height() / 2, f"{w:.2f}", va="center", fontsize=8, color="#333333")

    sns.despine()
    plt.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_violin_features(
    df: pd.DataFrame,
    features_to_plot: List[str],
    output_path: Union[str, Path],
    group_col: str = "Diagnosis",
) -> None:
    """Replicate Figure 5: Multi-panel violin plots showing feature distributions across diagnoses."""
    clean = df.dropna(subset=[group_col]).copy()
    valid_features = [f for f in features_to_plot if f in clean.columns]
    if not valid_features:
        return

    n_feats = len(valid_features)
    ncols = min(3, n_feats)
    nrows = int(np.ceil(n_feats / ncols))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 4.5, nrows * 3.8), dpi=300)
    axes = np.atleast_1d(axes).flatten()

    for i, feat in enumerate(valid_features):
        ax = axes[i]
        sns.violinplot(
            data=clean,
            x=group_col,
            y=feat,
            palette="Set2",
            inner="quartile",
            ax=ax,
            cut=0,
        )
        ax.set_title(feat.replace("_", " ").title(), fontsize=11, weight="semibold")
        ax.set_xlabel("")
        ax.set_ylabel("Value", fontsize=9)
        sns.despine(ax=ax)

    # Turn off unused subplot axes
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    fig.suptitle("Linguistic Feature Distributions Across Diagnostic Groups", fontsize=15, weight="bold", y=1.02)
    plt.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_cognitive_regressions(
    df: pd.DataFrame,
    features_to_plot: List[str],
    output_path: Union[str, Path],
    score_col: str = "MoCA",
    group_col: str = "Diagnosis",
) -> None:
    """Replicate Figure 6: Scatter plots with regression lines against cognitive assessment scores."""
    clean = df.dropna(subset=[score_col, group_col]).copy()
    valid_features = [f for f in features_to_plot if f in clean.columns]
    if not valid_features:
        return

    n_feats = len(valid_features)
    ncols = min(3, n_feats)
    nrows = int(np.ceil(n_feats / ncols))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 4.5, nrows * 4.0), dpi=300)
    axes = np.atleast_1d(axes).flatten()

    for i, feat in enumerate(valid_features):
        ax = axes[i]
        sub = clean.dropna(subset=[feat, score_col])
        if len(sub) < 5:
            continue

        sns.regplot(
            data=sub,
            x=feat,
            y=score_col,
            scatter_kws={"alpha": 0.6, "color": "#2c7bb6"},
            line_kws={"color": "#d7191c", "linewidth": 2},
            ax=ax,
        )

        r_val = float(np.corrcoef(sub[feat], sub[score_col])[0, 1]) if len(sub) > 2 else 0.0
        ax.set_title(f"{feat.replace('_', ' ').title()}\n(r = {r_val:.2f})", fontsize=10, weight="semibold")
        ax.set_xlabel(feat.replace("_", " ").title(), fontsize=9)
        ax.set_ylabel(score_col, fontsize=9)
        sns.despine(ax=ax)

    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    fig.suptitle(
        f"Correlations: Linguistic Features vs. Cognitive Assessment ({score_col})",
        fontsize=14,
        weight="bold",
        y=1.02,
    )
    plt.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_task_radar(
    df: pd.DataFrame,
    features_to_plot: List[str],
    output_path: Union[str, Path],
    task_col: str = "Task",
    group_col: str = "Diagnosis",
) -> None:
    """Replicate Figure 4(b): Radar plots comparing normalized features across picture description tasks."""
    clean = df.dropna(subset=[task_col, group_col]).copy()
    valid_features = [f for f in features_to_plot if f in clean.columns]
    if len(valid_features) < 3:
        return

    tasks = [t for t in clean[task_col].unique() if t in ("Cookie", "Cat", "Rockwell")]
    if not tasks:
        tasks = list(clean[task_col].unique())[:3]

    num_vars = len(valid_features)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Complete loop

    fig, axes = plt.subplots(
        nrows=1,
        ncols=len(tasks),
        figsize=(len(tasks) * 5.5, 5.5),
        subplot_kw=dict(polar=True),
        dpi=300,
    )
    axes = np.atleast_1d(axes)

    # Standardize features across entire dataset for fair radar scale
    norm_df = clean.copy()
    for f in valid_features:
        std = norm_df[f].std()
        norm_df[f] = (norm_df[f] - norm_df[f].mean()) / std if std > 0 else 0.0

    groups = sorted(clean[group_col].unique())

    for t_idx, task in enumerate(tasks):
        ax = axes[t_idx]
        task_sub = norm_df[norm_df[task_col] == task]

        for g in groups:
            g_sub = task_sub[task_sub[group_col] == g]
            if g_sub.empty:
                continue
            values = [float(g_sub[f].mean()) for f in valid_features]
            values += values[:1]
            ax.plot(angles, values, label=str(g), linewidth=2)
            ax.fill(angles, values, alpha=0.15)

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), [f.replace("_", "\n") for f in valid_features], fontsize=8)
        ax.set_title(f"Task: {task}", weight="bold", size=12, position=(0.5, 1.1))
        if t_idx == 0:
            ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1), fontsize=9)

    fig.suptitle("Task-Specific Linguistic Profiles Across Diagnostic Groups", fontsize=14, weight="bold", y=1.05)
    plt.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, bbox_inches="tight")
    plt.close(fig)
