import json
import streamlit as st

from engine.pipeline import run_pipeline
from ui.dashboard import render_dashboard
from ui.alerts import render_alert_queue
from ui.entity_detail import render_entity_detail

st.set_page_config(
    page_title="Financial Risk Surveillance Platform",
    page_icon="🛡️",
    layout="wide"
)

st.markdown(
    """
    <style>
    .doc-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(23,78,166,0.10);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 8px 22px rgba(11,31,58,0.06);
    }
    .hero-card {
        background: linear-gradient(135deg, #0B1F3A 0%, #174EA6 58%, #D4A017 145%);
        padding: 26px 28px;
        border-radius: 22px;
        color: white;
        box-shadow: 0 18px 40px rgba(11,31,58,0.18);
        margin-bottom: 18px;
    }
    .hero-card h1 {
        margin: 0 0 6px 0;
        font-size: 2rem;
        line-height: 1.1;
    }
    .hero-card p {
        margin: 0;
        font-size: 1rem;
        color: rgba(255,255,255,0.92);
    }
    .subtle-note {
        font-size: 0.95rem;
        color: #5B6575;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "🚨 Alert Queue",
        "🔍 Entity Detail",
        "📘 Methodology & Documentation"
    ])

    with tab1:
        render_dashboard(summary, surveillance_df, fi_top)

    with tab2:
        render_alert_queue(surveillance_df)

    with tab3:
        render_entity_detail(surveillance_df)

    with tab4:
        st.markdown(
            """
            <div class="hero-card">
                <h1>Financial Risk Surveillance Framework</h1>
                <p>Integrated Machine Learning, Rule-Based, Anomaly Detection and Network Analytics System for Financial Crime Risk Detection</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 System Overview")
        st.markdown(
            """
            <div class="doc-card">
            This platform is a <b>multi-layer financial risk detection and prioritisation system</b>
            designed to support banks, regulators, compliance units, and Financial Intelligence Units (FIUs)
            in identifying, ranking, and investigating potential financial crime risks.

            The framework integrates:
            <ul>
                <li>Supervised Machine Learning classification</li>
                <li>Unsupervised anomaly detection</li>
                <li>Rule-based AML indicators</li>
                <li>Graph / network risk analytics</li>
                <li>Trade-Based Money Laundering (TBML) indicators</li>
            </ul>

            The outputs of these components are fused into a <b>single composite risk score</b> used to generate
            a prioritised alert queue aligned with investigative capacity.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Risk Scoring Framework")
        st.markdown(
            """
            The system computes a composite risk score as a weighted aggregation of multiple detection layers:
            """
        )

        st.latex(r"""
        \text{Final Risk Score}_i
        =
        0.52 \cdot ML_i
        +
        0.18 \cdot Rule_i
        +
        0.12 \cdot Anomaly_i
        +
        0.10 \cdot Graph_i
        +
        0.08 \cdot TBML_i
        """)

        st.markdown(
            """
            <div class="doc-card">
            Where:
            <ul>
                <li><b>ML</b>: supervised classification probability</li>
                <li><b>Rule</b>: rule-based AML trigger score</li>
                <li><b>Anomaly</b>: Isolation Forest anomaly score</li>
                <li><b>Graph</b>: network centrality and connectivity risk score</li>
                <li><b>TBML</b>: trade-based money laundering signal score</li>
            </ul>

            This hybrid structure combines statistical learning, expert-driven indicators,
            structural network intelligence, and transaction anomaly signals into a unified risk metric.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Risk Engine Architecture")
        st.markdown(
            """
            <div class="doc-card">
            <b>1. Data Integration</b><br>
            Customer, account, transaction, case-history, network, and TBML datasets are integrated into
            a unified analytical environment.<br><br>

            <b>2. Feature Engineering</b><br>
            The system constructs behavioural, transactional, structural, and historical indicators,
            including turnover intensity, counterparty relationships, rapid movement of funds, cross-border activity,
            dormant account activation, and expected-versus-observed transaction mismatches.<br><br>

            <b>3. Modelling Layer</b><br>
            A supervised classifier estimates the probability of suspicious behaviour using labelled case data,
            while an anomaly model identifies statistically unusual patterns that may not be captured by historical labels.<br><br>

            <b>4. Rules and Network Intelligence</b><br>
            Expert-defined AML rules and graph-based risk metrics capture typologies, relationships,
            and hidden structural exposure beyond pure statistical prediction.<br><br>

            <b>5. Risk Fusion and Alerting</b><br>
            All signals are combined into a single composite score used to rank entities and generate alerts.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Core Data Inputs")
        st.markdown(
            """
            <div class="doc-card">
            The platform is designed to work with the following core datasets:
            <ul>
                <li><b>customers.csv</b> – customer or entity master information</li>
                <li><b>accounts.csv</b> – account-level information</li>
                <li><b>transactions.csv</b> – transaction history</li>
                <li><b>cases.csv</b> – historical suspicious case records / dispositions</li>
                <li><b>customer_transaction_summary.csv</b> – pre-aggregated customer transaction indicators</li>
            </ul>

            Optional supporting datasets include:
            <ul>
                <li><b>customer_networks.csv</b> – declared or inferred customer relationships</li>
                <li><b>corporate_links.csv</b> – corporate linkages and beneficial ownership proxies</li>
                <li><b>tbml_transactions.csv</b> – trade-based money laundering indicators</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Feature Engineering and Indicators")
        st.markdown(
            """
            <div class="doc-card">
            The model framework constructs a broad range of indicators, including:
            <ul>
                <li>Transaction count and amount intensity</li>
                <li>Turnover relative to expected activity</li>
                <li>Cash transaction intensity</li>
                <li>Cross-border activity ratios</li>
                <li>Round-amount behaviour and structuring indicators</li>
                <li>Rapid movement and velocity indicators</li>
                <li>High-risk corridor activity</li>
                <li>Network degree, PageRank, clustering, and approximate betweenness</li>
                <li>TBML flags such as high-risk country exposure and invoice deviation patterns</li>
            </ul>
            These variables support both risk scoring and analyst interpretation.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Capacity-Based Alerting Framework")
        st.markdown(
            """
            <div class="doc-card">
            Rather than relying exclusively on static cut-off rules, the platform supports a
            <b>capacity-based alerting framework</b>. Under this approach, the top <b>X%</b> of highest-risk
            entities are flagged, where X can be aligned with investigative capacity.

            This improves:
            <ul>
                <li>Operational relevance</li>
                <li>Alert manageability</li>
                <li>Signal-to-noise ratio</li>
                <li>Risk-based prioritisation</li>
            </ul>

            In the current prototype, the user controls the alert rate directly from the sidebar.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Outputs Produced by the Platform")
        st.markdown(
            """
            <div class="doc-card">
            The system generates:
            <ul>
                <li>A prioritised surveillance watchlist</li>
                <li>An alert queue for further review</li>
                <li>Top 100 high-risk entities</li>
                <li>Feature importance summaries</li>
                <li>Risk band summaries</li>
                <li>Entity-level drill-down outputs for analyst review</li>
            </ul>
            These outputs support investigation, supervision, escalation, and reporting workflows.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Operational Interpretation")
        st.markdown(
            """
            <div class="doc-card">
            This platform is intended as a <b>decision-support system</b> for:
            <ul>
                <li>Anti-Money Laundering (AML) surveillance</li>
                <li>Fraud risk identification</li>
                <li>Financial intelligence analysis</li>
                <li>Risk-based supervision</li>
                <li>Internal compliance monitoring</li>
            </ul>

            Its outputs should be interpreted as analytical indicators requiring human review,
            not as definitive proof of wrongdoing.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔷 Limitations")
        st.markdown(
            """
            <div class="doc-card">
            The effectiveness of the platform depends on:
            <ul>
                <li>Data quality, completeness, and consistency</li>
                <li>Availability of labelled suspicious cases</li>
                <li>Coverage of network and TBML information</li>
                <li>Appropriate parameterisation of alert thresholds and rule logic</li>
            </ul>

            As with all analytical risk engines, model outputs should be supplemented by
            professional judgment, investigative review, and institutional governance controls.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## ⚖️ Disclaimer")
        st.markdown(
            """
            <div class="doc-card">
            This application is a prototype analytical tool developed for research, demonstration,
            and decision-support purposes only.

            It does not constitute a production-ready financial crime detection system and should not be relied upon
            as the sole basis for regulatory, compliance, or legal decisions.

            All outputs generated by the system are indicative and require validation, interpretation,
            and confirmation by qualified professionals.

            The developer assumes no liability for any decisions made based on the outputs of this application.

            Users are responsible for ensuring compliance with applicable data protection,
            confidentiality, and regulatory requirements.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 👤 Author & Ownership")
        st.markdown(
            """
            <div class="doc-card">
            <b>Chirume Admire Tarisirayi</b><br>
            PhD Candidate | Econometrics | Statistics | Data Science<br><br>

            © 2026 All Rights Reserved<br>
            Contact: +263 773 369 884
            </div>
            """,
            unsafe_allow_html=True,
        )

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

st.divider()

st.markdown("### ⚖️ Disclaimer")
st.markdown(
    """
    This application is a prototype analytical tool developed for research, demonstration,
    and decision-support purposes only.

    It does not constitute a production-ready financial crime detection system and should not be relied upon
    as the sole basis for regulatory, compliance, or legal decisions.

    All outputs generated by the system are indicative and require validation, interpretation,
    and confirmation by qualified professionals.

    The developer assumes no liability for any decisions made based on the outputs of this application.

    Users are responsible for ensuring compliance with applicable data protection, confidentiality,
    and regulatory requirements.
    """
)

st.markdown("### 👤 Author & Ownership")
st.markdown(
    """
    **Chirume Admire Tarisirayi**  
    PhD Candidate | Econometrics | Statistics | Data Science  

    © 2026 All Rights Reserved  
    Contact: +263 773 369 884
    """
)
