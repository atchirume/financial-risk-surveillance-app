import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score, precision_recall_curve, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.calibration import CalibratedClassifierCV

from config import RANDOM_SEED

def choose_operating_threshold(y_true, proba, precision_floor=0.20):
    if len(np.unique(y_true)) < 2:
        return 0.20, {"selected_threshold": 0.20, "method": "fallback_single_class", "precision": None, "recall": None, "f1": None}

    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    if len(thresholds) == 0:
        return 0.20, {"selected_threshold": 0.20, "method": "fallback_no_thresholds", "precision": None, "recall": None, "f1": None}

    pr_df = pd.DataFrame({"threshold": thresholds, "precision": precision[:-1], "recall": recall[:-1]})
    pr_df["f1"] = np.where((pr_df["precision"] + pr_df["recall"]) == 0, 0, 2 * pr_df["precision"] * pr_df["recall"] / (pr_df["precision"] + pr_df["recall"]))
    candidates = pr_df[pr_df["precision"] >= precision_floor].copy()
    if len(candidates) == 0:
        candidates = pr_df.copy()

    best = candidates.sort_values(["f1", "precision", "threshold"], ascending=[False, False, False]).iloc[0]
    return float(best["threshold"]), {"selected_threshold": float(best["threshold"]), "method": "pr_curve_f1_with_precision_floor", "precision": float(best["precision"]), "recall": float(best["recall"]), "f1": float(best["f1"])}

def prepare_features(df):
    excluded = {"customer_id","customer_name","triggered_rules","alert_disposition","suspicious_flag"}
    possible_id_like = ["account_id","account_number","transaction_id","txn_id","tbml_id","case_id","swift_code","iban","passport_number","national_id","phone_number","email","address","full_address","registered_address","counterparty_name","customer_name_summary"]
    for col in possible_id_like:
        if col in df.columns:
            excluded.add(col)

    feature_cols = [c for c in df.columns if c not in excluded]
    X = df[feature_cols].copy()
    y = df["suspicious_flag"].astype(int).copy()

    for col in X.columns:
        if pd.api.types.is_bool_dtype(X[col]):
            X[col] = X[col].astype(int)
            continue
        if pd.api.types.is_numeric_dtype(X[col]):
            X[col] = pd.to_numeric(X[col], errors="coerce")
            continue

        converted = pd.to_numeric(X[col], errors="coerce")
        if len(converted) > 0 and (converted.notna().sum() / len(converted) > 0.90):
            X[col] = converted
        else:
            X[col] = X[col].astype(str).replace({"nan": np.nan, "None": np.nan, "NaT": np.nan})

    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    dropped = [c for c in categorical_cols if X[c].nunique(dropna=True) > 50]
    if dropped:
        X = X.drop(columns=dropped, errors="ignore")

    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in X.columns if c not in numeric_cols]
    return X, y, numeric_cols, categorical_cols, dropped

def extract_feature_importance(fitted_pipeline, top_n=40):
    try:
        preprocessor = fitted_pipeline.named_steps["preprocessor"]
        model = fitted_pipeline.named_steps["model"]
        feature_names = preprocessor.get_feature_names_out()
        fi = pd.DataFrame({"feature": feature_names, "importance": model.feature_importances_}).sort_values("importance", ascending=False)
        return fi.head(top_n).reset_index(drop=True), fi.reset_index(drop=True)
    except Exception:
        empty = pd.DataFrame(columns=["feature", "importance"])
        return empty, empty

def train_supervised_model(df):
    X, y, numeric_cols, categorical_cols, dropped = prepare_features(df)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_cols),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=True))]), categorical_cols),
        ],
        remainder="drop",
    )

    base_rf = RandomForestClassifier(n_estimators=260, max_depth=12, min_samples_leaf=4, min_samples_split=10, class_weight="balanced_subsample", random_state=RANDOM_SEED, n_jobs=-1)
    base_pipeline = Pipeline([("preprocessor", preprocessor), ("model", base_rf)])

    stratify_y = y if y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=RANDOM_SEED, stratify=stratify_y)

    base_pipeline.fit(X_train, y_train)
    calibrated = CalibratedClassifierCV(estimator=base_pipeline, method="sigmoid", cv=3)
    calibrated.fit(X_train, y_train)

    test_proba = calibrated.predict_proba(X_test)[:, 1]
    selected_threshold, threshold_info = choose_operating_threshold(y_test, test_proba)
    test_pred = (test_proba >= selected_threshold).astype(int)

    roc_auc = float(roc_auc_score(y_test, test_proba)) if y_test.nunique() > 1 else np.nan
    avg_precision = float(average_precision_score(y_test, test_proba)) if y_test.nunique() > 1 else np.nan

    metrics = {
        "roc_auc": roc_auc,
        "average_precision": avg_precision,
        "selected_threshold": selected_threshold,
        "threshold_details": threshold_info,
        "precision_at_selected_threshold": float(precision_score(y_test, test_pred, zero_division=0)),
        "recall_at_selected_threshold": float(recall_score(y_test, test_pred, zero_division=0)),
        "f1_at_selected_threshold": float(f1_score(y_test, test_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, test_pred).tolist(),
        "classification_report": classification_report(y_test, test_pred, zero_division=0),
        "dropped_high_cardinality_columns": dropped,
    }

    full_scores = calibrated.predict_proba(X)[:, 1]
    fi_top, fi_full = extract_feature_importance(base_pipeline, top_n=50)
    return calibrated, full_scores, metrics, fi_top, fi_full

def train_anomaly_model(df):
    numeric_df = df.select_dtypes(include=[np.number, "bool"]).copy().drop(columns=["customer_id","suspicious_flag"], errors="ignore")
    anomaly_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", IsolationForest(n_estimators=140, contamination=0.04, random_state=RANDOM_SEED, n_jobs=-1)),
    ])
    anomaly_pipeline.fit(numeric_df)
    X_imp = anomaly_pipeline.named_steps["imputer"].transform(numeric_df)
    X_scaled = anomaly_pipeline.named_steps["scaler"].transform(X_imp)
    anomaly_scores = -anomaly_pipeline.named_steps["model"].score_samples(X_scaled)
    return anomaly_pipeline, anomaly_scores
