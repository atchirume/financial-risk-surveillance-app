import json
import joblib

from config import OUTPUTS_DIR, MODELS_DIR

def save_outputs(df, supervised_model, anomaly_model, metrics, fi_top, fi_full, final_alert_threshold, alert_rate_used):
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    output_cols = [
        "surveillance_rank","customer_id","customer_name","entity_type","country","province","sector",
        "kyc_risk_band","pep_flag","adverse_media_flag","sanctions_watchlist_flag","previous_sar_flag",
        "shell_company_flag","total_txn_amount","txn_count","cross_border_count","cash_ratio",
        "round_amount_ratio","night_txn_ratio","structured_ratio","rapid_movement_count",
        "high_risk_country_txn_count","graph_risk_score","tbml_risk_score","rule_score_norm",
        "supervised_score","anomaly_score","anomaly_score_norm","final_risk_score","priority_band",
        "alert_flag","triggered_rules","alert_reason_summary","turnover_vs_expected",
        "counterparty_intensity","suspicious_flag","alert_disposition",
    ]
    output_cols = [c for c in output_cols if c in df.columns]

    df[output_cols].to_csv(OUTPUTS_DIR / "prioritized_surveillance_watchlist.csv", index=False)
    df[df["alert_flag"] == 1][output_cols].to_csv(OUTPUTS_DIR / "financial_crime_alert_queue.csv", index=False)
    df.head(100)[output_cols].to_csv(OUTPUTS_DIR / "top_100_high_risk_entities.csv", index=False)

    fi_top.to_csv(OUTPUTS_DIR / "top_feature_importance.csv", index=False)
    fi_full.to_csv(OUTPUTS_DIR / "full_feature_importance.csv", index=False)

    band_summary = (
        df.groupby("priority_band", observed=False)
        .agg(customers=("customer_id","count"), alerts=("alert_flag","sum"),
             avg_final_risk_score=("final_risk_score","mean"), avg_supervised_score=("supervised_score","mean"))
        .reset_index()
    )
    band_summary.to_csv(OUTPUTS_DIR / "priority_band_summary.csv", index=False)

    if "sector" in df.columns:
        sector_summary = (
            df.groupby("sector", observed=False)
            .agg(customers=("customer_id","count"), alerts=("alert_flag","sum"),
                 avg_final_risk_score=("final_risk_score","mean"))
            .sort_values(["alerts","avg_final_risk_score"], ascending=[False, False])
            .reset_index()
        )
        sector_summary.to_csv(OUTPUTS_DIR / "sector_risk_summary.csv", index=False)

    if "country" in df.columns:
        country_summary = (
            df.groupby("country", observed=False)
            .agg(customers=("customer_id","count"), alerts=("alert_flag","sum"),
                 avg_final_risk_score=("final_risk_score","mean"))
            .sort_values(["alerts","avg_final_risk_score"], ascending=[False, False])
            .reset_index()
        )
        country_summary.to_csv(OUTPUTS_DIR / "country_risk_summary.csv", index=False)

    summary = {
        "population": int(len(df)),
        "alerts": int(df["alert_flag"].sum()),
        "alert_rate_percent": round(100 * df["alert_flag"].mean(), 4),
        "critical_cases": int((df["priority_band"] == "Critical").sum()),
        "high_cases": int((df["priority_band"] == "High").sum()),
        "selected_threshold_supervised_model": float(metrics["selected_threshold"]),
        "final_alert_threshold_fused_score": float(final_alert_threshold),
        "alert_rate_used": float(alert_rate_used),
        "roc_auc": None if str(metrics["roc_auc"]) == "nan" else metrics["roc_auc"],
        "average_precision": None if str(metrics["average_precision"]) == "nan" else metrics["average_precision"],
        "precision_at_selected_threshold": metrics["precision_at_selected_threshold"],
        "recall_at_selected_threshold": metrics["recall_at_selected_threshold"],
        "f1_at_selected_threshold": metrics["f1_at_selected_threshold"],
        "confusion_matrix": metrics["confusion_matrix"],
        "threshold_details": metrics["threshold_details"],
        "classification_report": metrics["classification_report"],
        "dropped_high_cardinality_columns": metrics.get("dropped_high_cardinality_columns", []),
    }

    with open(OUTPUTS_DIR / "surveillance_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    joblib.dump(supervised_model, MODELS_DIR / "financial_crime_supervised_model.joblib")
    joblib.dump(anomaly_model, MODELS_DIR / "financial_crime_anomaly_model.joblib")
    return summary
