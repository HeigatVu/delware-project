"""Tests for statistical_analysis module."""

import numpy as np
import pandas as pd
from delware_speech.statistical_analysis import (
    compute_cohens_d,
    perform_group_comparisons,
    perform_ancova,
    compute_cognitive_correlations,
)


def test_compute_cohens_d():
    g1 = np.array([10.0, 12.0, 14.0, 16.0])
    g2 = np.array([5.0, 7.0, 9.0, 11.0])
    d = compute_cohens_d(g1, g2)
    assert d > 0


def test_perform_group_comparisons():
    np.random.seed(42)
    n = 30
    df = pd.DataFrame({
        "Diagnosis": ["Control"] * n + ["MCI"] * n,
        "pronouns_rate": list(np.random.normal(0.10, 0.02, n)) + list(np.random.normal(0.18, 0.03, n)),
        "syntactic_complexity": list(np.random.normal(1.5, 0.2, n)) + list(np.random.normal(1.1, 0.2, n)),
    })

    res = perform_group_comparisons(df, ["pronouns_rate", "syntactic_complexity"])
    assert len(res) == 2
    assert "ANOVA_F" in res.columns
    assert "ANOVA_p" in res.columns
    assert "Partial_Eta_Sq" in res.columns
    assert "Cohen_d" in res.columns
    assert "ANOVA_p_FDR" in res.columns

    # Check that p-values are significant for clearly separated groups
    for _, row in res.iterrows():
        assert row["ANOVA_p"] < 0.01


def test_perform_ancova():
    np.random.seed(42)
    n = 25
    df = pd.DataFrame({
        "Diagnosis": ["Control"] * n + ["MCI"] * n,
        "Age": np.random.uniform(60, 85, 2 * n),
        "Education_Years": np.random.uniform(10, 20, 2 * n),
        "feat_test": list(np.random.normal(5, 1, n)) + list(np.random.normal(2, 1, n)),
    })

    res = perform_ancova(df, ["feat_test"])
    assert len(res) == 1
    assert "ANCOVA_F" in res.columns
    assert "Group_p" in res.columns
    assert "Group_Coefficient" in res.columns


def test_compute_cognitive_correlations():
    np.random.seed(42)
    n = 40
    moca = np.random.uniform(18, 30, n)
    feat = 0.5 * moca + np.random.normal(0, 1, n)
    df = pd.DataFrame({"MoCA": moca, "feat_corr": feat})

    res = compute_cognitive_correlations(df, ["feat_corr"], score_col="MoCA")
    assert len(res) == 1
    assert res.iloc[0]["Pearson_r"] > 0.6
    assert res.iloc[0]["Pearson_p"] < 0.001
    assert res.iloc[0]["R_Squared"] > 0.3
