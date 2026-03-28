import numpy as np
import pandas as pd

from engine.graph_features import build_graph_features
from engine.helpers import ensure_columns, safe_div, minmax_scale
from engine.rules_engine import apply_rules

def build_tbml_features(tbml):
    if tbml is None or len(tbml) == 0:
        return pd.DataFrame(columns=[
            "customer_id","tbml_count","tbml_high_risk_country_count",
            "tbml_over_invoicing_count","tbml_under_invoicing_count",
            "tbml_avg_invoice_deviation_ratio","tbml_risk_score",
        ])

    required_cols = ["customer_id","tbml_id","high_risk_country_flag","over_invoicing_flag","under_invoicing_flag","invoice_deviation_ratio"]
    tbml = ensure_columns(tbml.copy(), required_cols, fill_value=0)

    tbml_features = tbml.groupby("customer_id", as_index=False).agg(
        tbml_count=("tbml_id","count"),
        tbml_high_risk_country_count=("high_risk_country_flag","sum"),
        tbml_over_invoicing_count=("over_invoicing_flag","sum"),
        tbml_under_invoicing_count=("under_invoicing_flag","sum"),
        tbml_avg_invoice_deviation_ratio=("invoice_deviation_ratio","mean"),
    )

    tbml_features["tbml_avg_invoice_deviation_ratio"] = tbml_features["tbml_avg_invoice_deviation_ratio"].fillna(1.0)
    tbml_features["tbml_risk_score"] = (
        minmax_scale(tbml_features["tbml_count"]) +
        minmax_scale(tbml_features["tbml_high_risk_country_count"]) +
        minmax_scale(tbml_features["tbml_over_invoicing_count"]) +
        minmax_scale(tbml_features["tbml_under_invoicing_count"]) +
        minmax_scale(abs(tbml_features["tbml_avg_invoice_deviation_ratio"] - 1.0))
    ) / 5.0
    return tbml_features

def build_master_table(data):
    customers = data["customers"].copy()
    customer_summary = data["customer_summary"].copy()
    cases = data["cases"].copy()

    graph_features = build_graph_features(data["transactions"], data["customer_networks"], data["corporate_links"])
    tbml_features = build_tbml_features(data["tbml"])

    df = customers.merge(customer_summary, on="customer_id", how="left", suffixes=("", "_summary"))
    if len(graph_features) > 0:
        df = df.merge(graph_features, on="customer_id", how="left")
    if len(tbml_features) > 0:
        df = df.merge(tbml_features, on="customer_id", how="left")

    case_cols = [c for c in ["customer_id","suspicious_flag","alert_disposition"] if c in cases.columns]
    if len(case_cols) > 1:
        df = df.merge(cases[case_cols], on="customer_id", how="left")
    else:
        df["suspicious_flag"] = 0
        df["alert_disposition"] = "unknown"

    numeric_candidate_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_candidate_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0)

    default_numeric_cols = [
        "total_txn_amount","expected_monthly_turnover","txn_count","unique_counterparties",
        "cash_ratio","cross_border_ratio","round_amount_ratio","night_txn_ratio","structured_ratio",
        "rapid_movement_ratio","graph_risk_score","tbml_risk_score","suspicious_flag",
        "previous_sar_flag","cross_border_count","rapid_movement_count","high_risk_country_txn_count",
        "sanctioned_corridor_count","dormant_account_flag","dormant_activation_count","pep_flag",
        "adverse_media_flag","sanctions_watchlist_flag","shell_company_flag",
    ]
    df = ensure_columns(df, default_numeric_cols, fill_value=0)

    if "alert_disposition" not in df.columns:
        df["alert_disposition"] = "unknown"

    datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    for col in datetime_cols:
        df[f"{col}_year"] = df[col].dt.year.fillna(0).astype(int)
        df[f"{col}_month"] = df[col].dt.month.fillna(0).astype(int)
        df[f"{col}_day"] = df[col].dt.day.fillna(0).astype(int)
        reference_date = pd.Timestamp.today().normalize()
        df[f"{col}_age_days"] = (reference_date - df[col]).dt.days.fillna(-1).astype(int)

    if len(datetime_cols) > 0:
        df = df.drop(columns=datetime_cols, errors="ignore")

    df["turnover_vs_expected"] = safe_div(df["total_txn_amount"], df["expected_monthly_turnover"])
    df["counterparty_intensity"] = safe_div(df["txn_count"], np.maximum(df["unique_counterparties"], 1))
    df["cross_border_amount_intensity"] = df["cross_border_ratio"].fillna(0) * df["total_txn_amount"].fillna(0)
    df["cash_amount_intensity"] = df["cash_ratio"].fillna(0) * df["total_txn_amount"].fillna(0)
    df["rapid_flow_intensity"] = df["rapid_movement_ratio"].fillna(0) * df["txn_count"].fillna(0)

    for c in ["cash_ratio","cross_border_ratio","round_amount_ratio","night_txn_ratio","structured_ratio","rapid_movement_ratio","graph_risk_score","tbml_risk_score"]:
        if c in df.columns:
            df[c] = df[c].fillna(0)

    df["suspicious_flag"] = df["suspicious_flag"].fillna(0).astype(int)
    return apply_rules(df)
