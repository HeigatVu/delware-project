"""Statistical analysis module for linguistic features and cognitive scores.

Implements ANOVA, Kruskal-Wallis, post-hoc tests, effect sizes (partial eta-squared,
Cohen's d, epsilon-squared), ANCOVA covariate adjustments, and MoCA correlations
per Nyongesa et al. (2025).
"""

from __future__ import annotations

import logging
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.multitest import multipletests

logger = logging.getLogger(__name__)


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Calculate Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_sd)


def perform_group_comparisons(
    df: pd.DataFrame,
    features: List[str],
    group_col: str = "Diagnosis",
) -> pd.DataFrame:
    """Perform ANOVA, Kruskal-Wallis, and effect sizes across diagnostic groups.

    Args:
        df: DataFrame containing linguistic features and diagnostic groups.
        features: List of column names corresponding to numeric linguistic features.
        group_col: Column defining diagnostic categories.

    Returns:
        DataFrame summarizing test statistics, p-values, adjusted p-values, and effect sizes.
    """
    valid_groups = [g for g in df[group_col].dropna().unique() if str(g).strip()]
    results = []

    for feat in features:
        if feat not in df.columns:
            continue

        grouped_data = [
            df[df[group_col] == g][feat].dropna().values
            for g in valid_groups
            if len(df[df[group_col] == g][feat].dropna()) > 0
        ]

        if len(grouped_data) < 2:
            continue

        # Descriptive stats per group
        means = {
            f"Mean_{g}": float(np.mean(vals)) if len(vals) else np.nan
            for g, vals in zip(valid_groups, grouped_data)
        }
        stds = {
            f"SD_{g}": float(np.std(vals, ddof=1)) if len(vals) > 1 else np.nan
            for g, vals in zip(valid_groups, grouped_data)
        }

        # ANOVA (F-test)
        try:
            f_stat, f_pval = stats.f_oneway(*grouped_data)
            # Partial eta-squared
            total_ss = np.sum((np.concatenate(grouped_data) - np.mean(np.concatenate(grouped_data))) ** 2)
            group_ss = sum(len(v) * (np.mean(v) - np.mean(np.concatenate(grouped_data))) ** 2 for v in grouped_data)
            eta_sq = group_ss / total_ss if total_ss > 0 else 0.0
        except Exception:
            f_stat, f_pval, eta_sq = np.nan, np.nan, np.nan

        # Kruskal-Wallis test (H-test)
        try:
            h_stat, h_pval = stats.kruskal(*grouped_data)
            # Epsilon-squared: (H - k + 1) / (n - k)
            n_tot = sum(len(v) for v in grouped_data)
            k = len(grouped_data)
            epsilon_sq = (h_stat - k + 1) / (n_tot - k) if n_tot > k else 0.0
        except Exception:
            h_stat, h_pval, epsilon_sq = np.nan, np.nan, np.nan

        # Cohen's d if exactly 2 groups
        d_val = np.nan
        if len(grouped_data) == 2:
            d_val = compute_cohens_d(grouped_data[0], grouped_data[1])

        row_dict = {
            "Feature": feat,
            "ANOVA_F": f_stat,
            "ANOVA_p": f_pval,
            "Partial_Eta_Sq": eta_sq,
            "Kruskal_H": h_stat,
            "Kruskal_p": h_pval,
            "Epsilon_Sq": epsilon_sq,
            "Cohen_d": d_val,
        }
        row_dict.update(means)
        row_dict.update(stds)
        results.append(row_dict)

    res_df = pd.DataFrame(results)
    if not res_df.empty:
        # Multiple testing correction (FDR and Bonferroni)
        valid_p = res_df["ANOVA_p"].dropna()
        if len(valid_p) > 0:
            _, p_fdr, _, _ = multipletests(valid_p, method="fdr_bh")
            _, p_bonf, _, _ = multipletests(valid_p, method="bonferroni")
            res_df.loc[valid_p.index, "ANOVA_p_FDR"] = p_fdr
            res_df.loc[valid_p.index, "ANOVA_p_Bonferroni"] = p_bonf

    return res_df


def perform_ancova(
    df: pd.DataFrame,
    features: List[str],
    group_col: str = "Diagnosis",
    covariates: Tuple[str, ...] = ("Age", "Education_Years"),
) -> pd.DataFrame:
    """Perform ANCOVA controlling for demographic covariates (Age and Education).

    Model: Feature ~ C(Diagnosis) + Age + Education_Years
    """
    records = []
    clean_df = df.dropna(subset=list(covariates) + [group_col])

    for feat in features:
        if feat not in clean_df.columns:
            continue
        sub = clean_df.dropna(subset=[feat])
        if len(sub) < 10:
            continue

        formula = f"Q('{feat}') ~ C(Q('{group_col}')) + " + " + ".join([f"Q('{c}')" for c in covariates])
        try:
            model = ols(formula, data=sub).fit()
            group_term = [term for term in model.pvalues.index if f"C(Q('{group_col}'))" in term]
            if group_term:
                term = group_term[0]
                p_val = model.pvalues[term]
                coef = model.params[term]
                f_stat = model.fvalue
                r_sq = model.rsquared
                adj_r_sq = model.rsquared_adj
                records.append({
                    "Feature": feat,
                    "ANCOVA_F": f_stat,
                    "Group_Coefficient": coef,
                    "Group_p": p_val,
                    "Model_R2": r_sq,
                    "Model_Adj_R2": adj_r_sq,
                })
        except Exception as err:
            logger.debug(f"ANCOVA failed for {feat}: {err}")

    ancova_df = pd.DataFrame(records)
    if not ancova_df.empty:
        valid_p = ancova_df["Group_p"].dropna()
        if len(valid_p) > 0:
            _, p_fdr, _, _ = multipletests(valid_p, method="fdr_bh")
            ancova_df.loc[valid_p.index, "Group_p_FDR"] = p_fdr

    return ancova_df


def compute_cognitive_correlations(
    df: pd.DataFrame,
    features: List[str],
    score_col: str = "MoCA",
) -> pd.DataFrame:
    """Compute Pearson and Spearman correlations between linguistic features and cognitive scores."""
    clean_df = df.dropna(subset=[score_col])
    results = []

    for feat in features:
        if feat not in clean_df.columns:
            continue

        pair = clean_df[[feat, score_col]].dropna()
        if len(pair) < 5:
            continue

        x = pair[feat].values
        y = pair[score_col].values

        if np.std(x) == 0 or np.std(y) == 0:
            continue

        # Pearson
        r_pearson, p_pearson = stats.pearsonr(x, y)
        r_sq = r_pearson ** 2

        # Spearman
        rho_spearman, p_spearman = stats.spearmanr(x, y)

        # Linear regression slope
        slope, intercept, _, _, stderr = stats.linregress(x, y)

        results.append({
            "Feature": feat,
            "Cognitive_Score": score_col,
            "N": len(pair),
            "Pearson_r": r_pearson,
            "Pearson_p": p_pearson,
            "R_Squared": r_sq,
            "Spearman_rho": rho_spearman,
            "Spearman_p": p_spearman,
            "Slope_B": slope,
            "Intercept": intercept,
            "Std_Error": stderr,
        })

    corr_df = pd.DataFrame(results)
    if not corr_df.empty:
        valid_p = corr_df["Pearson_p"].dropna()
        if len(valid_p) > 0:
            _, p_fdr, _, _ = multipletests(valid_p, method="fdr_bh")
            corr_df.loc[valid_p.index, "Pearson_p_FDR"] = p_fdr

    return corr_df
