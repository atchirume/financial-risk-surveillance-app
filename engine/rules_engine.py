import pandas as pd
from engine.helpers import ensure_columns

def apply_rules(df):
    out = df.copy()

    needed_numeric = [
        "txn_count","round_amount_ratio","structured_ratio","cross_border_count","cross_border_ratio",
        "cash_ratio","total_txn_amount","rapid_movement_count","rapid_movement_ratio",
        "sanctioned_corridor_count","high_risk_country_txn_count","shell_company_flag",
        "expected_monthly_turnover","pep_flag","sanctions_watchlist_flag","adverse_media_flag",
        "dormant_account_flag","dormant_activation_count","turnover_vs_expected","night_txn_ratio",
        "unique_counterparties","counterparty_intensity","previous_sar_flag","tbml_count",
        "tbml_high_risk_country_count","tbml_over_invoicing_count","tbml_under_invoicing_count",
        "tbml_avg_invoice_deviation_ratio",
    ]
    out = ensure_columns(out, needed_numeric, fill_value=0)

    if "kyc_risk_band" not in out.columns:
        out["kyc_risk_band"] = "Low"

    out["rule_structuring"] = ((out["txn_count"].fillna(0) >= 12) & (out["round_amount_ratio"].fillna(0) > 0.22) & (out["structured_ratio"].fillna(0) > 0.08)).astype(int)
    out["rule_cross_border_spike"] = ((out["cross_border_count"].fillna(0) >= 8) & (out["cross_border_ratio"].fillna(0) > 0.18)).astype(int)
    out["rule_cash_intensity"] = ((out["cash_ratio"].fillna(0) > 0.55) & (out["total_txn_amount"].fillna(0) > 50000)).astype(int)
    out["rule_rapid_movement"] = ((out["rapid_movement_count"].fillna(0) >= 4) | (out["rapid_movement_ratio"].fillna(0) > 0.10)).astype(int)
    out["rule_high_risk_corridor"] = ((out["sanctioned_corridor_count"].fillna(0) >= 3) | (out["high_risk_country_txn_count"].fillna(0) >= 5)).astype(int)
    out["rule_shell_turnover_mismatch"] = ((out["shell_company_flag"].fillna(0) == 1) & (out["total_txn_amount"].fillna(0) > 5 * out["expected_monthly_turnover"].fillna(1))).astype(int)
    out["rule_kyc_profile_mismatch"] = ((out["total_txn_amount"].fillna(0) > 6 * out["expected_monthly_turnover"].fillna(1)) & (out["kyc_risk_band"].fillna("Low").astype(str).str.upper() == "HIGH")).astype(int)
    out["rule_pep_sanctions_attention"] = ((out["pep_flag"].fillna(0) == 1) | (out["sanctions_watchlist_flag"].fillna(0) == 1) | (out["adverse_media_flag"].fillna(0) == 1)).astype(int)
    out["rule_dormant_activation"] = ((out["dormant_account_flag"].fillna(0) == 1) & (out["dormant_activation_count"].fillna(0) > 0)).astype(int)
    out["rule_extreme_turnover_ratio"] = (out["turnover_vs_expected"].fillna(0) > 10).astype(int)
    out["rule_night_activity"] = ((out["night_txn_ratio"].fillna(0) > 0.35) & (out["txn_count"].fillna(0) >= 10)).astype(int)
    out["rule_counterparty_dispersion"] = ((out["unique_counterparties"].fillna(0) >= 25) & (out["counterparty_intensity"].fillna(0) > 1.2)).astype(int)
    out["rule_repeat_sar_attention"] = (out["previous_sar_flag"].fillna(0) >= 1).astype(int)
    out["rule_tbml_attention"] = ((out["tbml_count"].fillna(0) >= 2) | (out["tbml_high_risk_country_count"].fillna(0) >= 1) | (out["tbml_over_invoicing_count"].fillna(0) >= 1) | (out["tbml_under_invoicing_count"].fillna(0) >= 1)).astype(int)

    rule_cols = [c for c in out.columns if c.startswith("rule_")]
    out["rule_score_raw"] = out[rule_cols].sum(axis=1)
    max_rule = out["rule_score_raw"].max()
    out["rule_score_norm"] = 0.0 if pd.isna(max_rule) or max_rule == 0 else out["rule_score_raw"] / max_rule

    triggered_rules = []
    for _, row in out[["customer_id"] + rule_cols].iterrows():
        hits = [c for c in rule_cols if row[c] == 1]
        triggered_rules.append(", ".join(hits) if hits else "none")
    out["triggered_rules"] = triggered_rules
    return out
