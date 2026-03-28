import json
import streamlit as st

from engine.pipeline import run_pipeline
from ui.dashboard import render_dashboard
from ui.alerts import render_alert_queue
from ui.entity_detail import render_entity_detail

st.set_page_config(page_title="Financial Risk Surveillance Platform", page_icon="🛡️", layout="wide")
st.title("Financial Risk Surveillance Platform")
st.caption("Enterprise Version 1 • Prototype for Banks and Financial Intelligence Units")

with st.sidebar:
    st.header("Controls")
    alert_rate = st.slider(
        "Alert rate (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Top percentage of highest-risk entities to flag."
    )
    run_clicked = st.button("Run Surveillance Pipeline", type="primary", use_container_width=True)

if run_clicked:
    with st.spinner("Running surveillance engine..."):
        st.session_state["artifacts"] = run_pipeline(alert_rate=alert_rate / 100.0)

if "artifacts" not in st.session_state:
    st.info("Click 'Run Surveillance Pipeline' in the sidebar to generate results.")
else:
    artifacts = st.session_state["artifacts"]
    summary = artifacts["summary"]
    surveillance_df = artifacts["surveillance_df"]
    fi_top = artifacts["feature_importance_top"]

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Alert Queue", "Entity Detail"])

    with tab1:
        render_dashboard(summary, surveillance_df, fi_top)
    with tab2:
        render_alert_queue(surveillance_df)
    with tab3:
        render_entity_detail(surveillance_df)

    st.divider()
    st.subheader("Export Buttons")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download Watchlist CSV",
            data=surveillance_df.to_csv(index=False).encode("utf-8"),
            file_name="prioritized_surveillance_watchlist.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download Top 100 CSV",
            data=surveillance_df.head(100).to_csv(index=False).encode("utf-8"),
            file_name="top_100_high_risk_entities.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col3:
        st.download_button(
            "Download Summary JSON",
            data=json.dumps(summary, indent=2).encode("utf-8"),
            file_name="surveillance_summary.json",
            mime="application/json",
            use_container_width=True,
        )
