import streamlit as st
import plotly.express as px

def render_dashboard(summary, surveillance_df, fi_top):
    st.subheader("Executive Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Population", f"{summary['population']:,}")
    c2.metric("Alerts", f"{summary['alerts']:,}")
    c3.metric("Alert Rate", f"{summary['alert_rate_percent']:.2f}%")
    c4.metric("ROC AUC", f"{summary['roc_auc']:.3f}" if summary["roc_auc"] is not None else "N/A")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("High Cases", f"{summary['high_cases']:,}")
    c6.metric("Critical Cases", f"{summary['critical_cases']:,}")
    c7.metric("Supervised Threshold", f"{summary['selected_threshold_supervised_model']:.4f}")
    c8.metric("Fused Threshold", f"{summary['final_alert_threshold_fused_score']:.4f}")

    left, right = st.columns(2)

    if "priority_band" in surveillance_df.columns:
        band = surveillance_df["priority_band"].astype(str).value_counts(dropna=False).reset_index()
        band.columns = ["priority_band", "count"]
        left.plotly_chart(px.bar(band, x="priority_band", y="count", title="Risk Band Distribution"), use_container_width=True)

    if "sector" in surveillance_df.columns:
        sector = surveillance_df.groupby("sector", observed=False)["alert_flag"].sum().sort_values(ascending=False).head(10).reset_index()
        right.plotly_chart(px.bar(sector, x="sector", y="alert_flag", title="Top 10 Sectors by Alerts"), use_container_width=True)

    st.subheader("Top Feature Importance")
    st.dataframe(fi_top, use_container_width=True, height=350)
