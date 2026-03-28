import numpy as np
import pandas as pd

from config import DEFAULT_ALERT_RATE, W_SUPERVISED, W_RULES, W_ANOMALY, W_GRAPH, W_TBML
from engine.helpers import minmax_scale

def generate_alert_reason(row):
    reasons = []
    if row.get("supervised_score", 0) >= 0.70: reasons.append("High supervised ML risk")
    if row.get("rule_score_norm", 0) >= 0.50: reasons.append("Multiple rule triggers")
    if row.get("anomaly_score_norm", 0) >= 0.80: reasons.append("Strong anomaly signal")
    if row.get("graph_risk_score", 0) >= 0.75: reasons.append("High network risk")
    if row.get("tbml_risk_score", 0) >= 0.60: reasons.append("Trade-based ML risk indicators")
    if row.get("turnover_vs_expected", 0) >= 8: reasons.append("Turnover far above expected profile")
    if row.get("cross_border_ratio", 0) >= 0.25: reasons.append("Elevated cross-border activity")
    if row.get("cash_ratio", 0) >= 0.60: reasons.append("Cash-intensive activity")
    if row.get("rapid_movement_ratio", 0) >= 0.15: reasons.append("Rapid movement of funds")
    if str(row.get("triggered_rules", "none")) != "none": reasons.append("Triggered explicit surveillance rules")
    if len(reasons) == 0: reasons.append("Composite score exceeded monitoring threshold")
    return " | ".join(reasons[:6])

def build_surveillance_output(df, supervised_scores, anomaly_scores, alert_rate=DEFAULT_ALERT_RATE):
    out = df.copy()
    out["supervised_score"] = pd.Series(supervised_scores, index=out.index).fillna(0)
    out["anomaly_score"] = pd.Series(anomaly_scores, index=out.index).fillna(0)
    out["anomaly_score_norm"] = minmax_scale(out["anomaly_score"])
    out["graph_risk_score"] = out["graph_risk_score"].fillna(0)
    out["tbml_risk_score"] = out["tbml_risk_score"].fillna(0)
    out["rule_score_norm"] = out["rule_score_norm"].fillna(0)

    out["final_risk_score"] = (
        W_SUPERVISED * out["supervised_score"] +
        W_RULES * out["rule_score_norm"] +
        W_ANOMALY * out["anomaly_score_norm"] +
        W_GRAPH * out["graph_risk_score"] +
        W_TBML * out["tbml_risk_score"]
    )

    alert_rate = float(alert_rate)
    alert_rate = min(max(alert_rate, 0.0001), 0.20)
    final_alert_threshold = float(out["final_risk_score"].quantile(1 - alert_rate))
    out["alert_flag"] = (out["final_risk_score"] >= final_alert_threshold).astype(int)

    q80 = float(out["final_risk_score"].quantile(0.80))
    q95 = float(out["final_risk_score"].quantile(0.95))
    q99 = float(out["final_risk_score"].quantile(0.99))
    max_score = float(out["final_risk_score"].max())
    bins = [-0.01, q80, q95, q99, max(max_score + 1e-6, q99 + 1e-6)]
    out["priority_band"] = pd.cut(out["final_risk_score"], bins=bins, labels=["Low","Medium","High","Critical"], include_lowest=True)

    out = out.sort_values("final_risk_score", ascending=False).reset_index(drop=True)
    out["surveillance_rank"] = np.arange(1, len(out) + 1)
    out["alert_reason_summary"] = out.apply(generate_alert_reason, axis=1)
    return out, final_alert_threshold, alert_rate
