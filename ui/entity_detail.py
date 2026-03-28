import streamlit as st

def render_entity_detail(df):
    st.subheader("Entity Detail")
    if "customer_id" not in df.columns:
        st.info("customer_id column not found.")
        return

    selected = st.selectbox("Select Customer ID", df["customer_id"].astype(str).tolist())
    entity = df[df["customer_id"].astype(str) == str(selected)].copy()
    if entity.empty:
        st.warning("Entity not found.")
        return

    row = entity.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Customer ID", str(row.get("customer_id", "")))
    c2.metric("Final Risk Score", f"{float(row.get('final_risk_score', 0)):.4f}")
    c3.metric("Priority Band", str(row.get("priority_band", "")))
    c4.metric("Alert Flag", str(int(row.get("alert_flag", 0))))

    left, right = st.columns(2)
    with left:
        st.markdown("**Profile**")
        profile_cols = ["customer_name","entity_type","country","province","sector","business_type","occupation","kyc_risk_band"]
        profile = {c: row.get(c, None) for c in profile_cols if c in entity.columns}
        st.json(profile)

        st.markdown("**Risk Signals**")
        signal_cols = ["supervised_score","anomaly_score_norm","graph_risk_score","tbml_risk_score","rule_score_norm","turnover_vs_expected","cross_border_ratio","cash_ratio","rapid_movement_ratio"]
        signals = {c: row.get(c, None) for c in signal_cols if c in entity.columns}
        st.json(signals)

    with right:
        st.markdown("**Alert Reason Summary**")
        st.write(str(row.get("alert_reason_summary", "")))

        st.markdown("**Triggered Rules**")
        st.write(str(row.get("triggered_rules", "")))

        note_key = f"notes_{selected}"
        current = st.session_state.get(note_key, "")
        st.session_state[note_key] = st.text_area("Case Notes", value=current, height=240)
