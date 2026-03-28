from engine.data_loader import load_data
from engine.feature_engineering import build_master_table
from engine.modeling import train_supervised_model, train_anomaly_model
from engine.risk_fusion import build_surveillance_output
from engine.exporters import save_outputs

def run_pipeline(alert_rate=0.01):
    data = load_data()
    master_df = build_master_table(data)
    supervised_model, supervised_scores, metrics, fi_top, fi_full = train_supervised_model(master_df)
    anomaly_model, anomaly_scores = train_anomaly_model(master_df)
    surveillance_df, final_alert_threshold, alert_rate_used = build_surveillance_output(master_df, supervised_scores, anomaly_scores, alert_rate=alert_rate)
    summary = save_outputs(surveillance_df, supervised_model, anomaly_model, metrics, fi_top, fi_full, final_alert_threshold, alert_rate_used)
    return {
        "summary": summary,
        "surveillance_df": surveillance_df,
        "feature_importance_top": fi_top,
        "feature_importance_full": fi_full,
        "metrics": metrics,
    }
