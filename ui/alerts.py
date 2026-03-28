import streamlit as st

def render_alert_queue(df):
    st.subheader("Alert Queue")
    alerts_df = df[df["alert_flag"] == 1].copy()

    col1, col2, col3 = st.columns(3)
    with col1:
        sector_filter = st.multiselect("Sector", sorted(df["sector"].dropna().astype(str).unique()) if "sector" in df.columns else [])
    with col2:
        country_filter = st.multiselect("Country", sorted(df["country"].dropna().astype(str).unique()) if "country" in df.columns else [])
    with col3:
        band_filter = st.multiselect("Priority Band", sorted(df["priority_band"].dropna().astype(str).unique()) if "priority_band" in df.columns else [])

    filtered = alerts_df.copy()
    if sector_filter and "sector" in filtered.columns:
        filtered = filtered[filtered["sector"].astype(str).isin(sector_filter)]
    if country_filter and "country" in filtered.columns:
        filtered = filtered[filtered["country"].astype(str).isin(country_filter)]
    if band_filter and "priority_band" in filtered.columns:
        filtered = filtered[filtered["priority_band"].astype(str).isin(band_filter)]

    view_cols = ["surveillance_rank","customer_id","customer_name","sector","country","priority_band","final_risk_score","alert_reason_summary","triggered_rules"]
    view_cols = [c for c in view_cols if c in filtered.columns]

    st.dataframe(filtered[view_cols], use_container_width=True, height=500)
    st.download_button("Download Alert Queue CSV", data=filtered.to_csv(index=False).encode("utf-8"), file_name="financial_crime_alert_queue.csv", mime="text/csv")
