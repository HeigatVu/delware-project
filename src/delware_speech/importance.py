"""Feature importance and diagnostic machine learning classification module.

Replicates Importance_Features.R and paper modeling:
- Random Forest 10-fold CV with Gini impurity feature ranking (top 20 features)
- Benchmark comparisons with Support Vector Machine (RBF) and Gradient Boosting
"""

from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from delware_speech.clustering import get_numeric_feature_columns


def prepare_classification_data(
    df: pd.DataFrame,
    target_col: str = "Diagnosis",
    feature_cols: List[str] | None = None,
) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """Prepare feature matrix X and target labels y for binary or multi-class diagnosis."""
    clean_df = df.dropna(subset=[target_col]).copy()
    # Normalize diagnosis strings
    clean_df[target_col] = clean_df[target_col].astype(str).str.strip()
    valid_classes = [c for c in clean_df[target_col].unique() if c.lower() not in ("other", "unknown", "nan")]
    clean_df = clean_df[clean_df[target_col].isin(valid_classes)]

    if feature_cols is None:
        feature_cols = get_numeric_feature_columns(clean_df)

    X_raw = clean_df[feature_cols].values
    y_raw = clean_df[target_col].values

    # Impute missing feature values with median
    imputer = SimpleImputer(strategy="median")
    X = imputer.fit_transform(X_raw)

    return X, y_raw, feature_cols, valid_classes


def evaluate_classifier_cv(
    clf: object,
    X: np.ndarray,
    y: np.ndarray,
    n_splits: int = 10,
    random_state: int = 42,
) -> Dict[str, float]:
    """Perform n-fold stratified cross-validation and compute accuracy, kappa, and balanced accuracy."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    accuracies = []
    kappas = []
    balanced_accs = []

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Standardize within fold to prevent data leakage
        scaler = StandardScaler()
        X_train_sc = scaler.fit_transform(X_train)
        X_test_sc = scaler.transform(X_test)

        clf.fit(X_train_sc, y_train)
        preds = clf.predict(X_test_sc)

        acc = float(np.mean(preds == y_test))
        accuracies.append(acc)

        try:
            kap = float(cohen_kappa_score(y_test, preds))
        except Exception:
            kap = 0.0
        kappas.append(kap)

        # Balanced accuracy
        classes = np.unique(y_test)
        recalls = [np.mean(preds[y_test == c] == c) for c in classes if np.sum(y_test == c) > 0]
        balanced_accs.append(float(np.mean(recalls)) if recalls else acc)

    return {
        "Accuracy_Mean": float(np.mean(accuracies)),
        "Accuracy_Std": float(np.std(accuracies)),
        "Kappa_Mean": float(np.mean(kappas)),
        "Kappa_Std": float(np.std(kappas)),
        "Balanced_Acc_Mean": float(np.mean(balanced_accs)),
    }


def compute_feature_importance_rf(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: List[str],
    n_estimators: int = 100,
    random_state: int = 42,
) -> pd.DataFrame:
    """Train Random Forest classifier and extract Mean Decrease in Gini importance."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    rf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state, max_features="sqrt")
    rf.fit(X_scaled, y)

    importances = rf.feature_importances_
    # Scale for readability (sum to 100 or raw percentage)
    gini_scores = importances * 100.0

    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance_Gini": importances,
        "Importance_Score": gini_scores,
    }).sort_values(by="Importance_Score", ascending=False).reset_index(drop=True)

    importance_df["Rank"] = range(1, len(importance_df) + 1)
    return importance_df


def benchmark_all_models(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int = 42,
) -> pd.DataFrame:
    """Compare Random Forest, SVM (RBF), and Gradient Boosting using 10-fold CV."""
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "SVM (RBF)": SVC(kernel="rbf", random_state=random_state),
        "Gradient Boosting": GradientBoostingClassifier(random_state=random_state),
    }

    records = []
    for name, clf in models.items():
        metrics = evaluate_classifier_cv(clf, X, y, n_splits=10, random_state=random_state)
        rec = {"Model": name}
        rec.update(metrics)
        records.append(rec)

    return pd.DataFrame(records)
