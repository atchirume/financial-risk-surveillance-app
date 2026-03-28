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
            The system computes a composite risk score as a weighted aggregation of multiple detection layers. The weights applied in the risk fusion function are calibrated based on a hybrid
            design approach that reflects the relative reliability, coverage, and interpretability
            of each risk signal.

            Supervised machine learning receives the highest weight due to its ability to learn
            from historical labelled cases, while rule-based, anomaly, network, and TBML signals
            provide complementary perspectives capturing expert knowledge, outliers, structural
            relationships, and domain-specific risks.

            These weights may be further refined through empirical validation, backtesting,
            and institutional calibration.
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

The feature engineering layer translates raw transactional and customer data into 
behavioural, structural, and risk-sensitive indicators. Each variable is designed 
to capture a specific financial crime typology or deviation from expected economic behaviour.

---

### 🔹 1. Transaction Intensity Indicators

**Examples:**
- `txn_count`
- `total_txn_amount`

**Motivation:**
These variables measure the scale and frequency of activity. Financial crime often manifests 
through unusually high transaction volumes relative to the expected profile of an individual 
or entity. Sudden spikes in transaction intensity may indicate layering, integration, or 
rapid movement of illicit funds.

---

### 🔹 2. Turnover vs Expected Behaviour

**Example:**
- `turnover_vs_expected`

**Motivation:**
This variable compares observed transaction volumes against expected or declared activity 
(e.g., income, business turnover).

**Justification:**
\[
\text{Turnover Ratio} = \frac{\text{Observed Transactions}}{\text{Expected Activity}}
\]

Large deviations suggest:
- fronting or shell activity  
- misuse of accounts  
- hidden beneficial ownership  

This is a core indicator in risk-based AML supervision frameworks.

---

### 🔹 3. Cash Intensity Indicators

**Example:**
- `cash_ratio`

**Motivation:**
Cash-based transactions reduce traceability and are commonly used in:
- structuring
- placement stages of money laundering
- informal sector concealment

A high cash ratio signals reduced audit trail visibility and elevated risk.

---

### 🔹 4. Cross-Border Activity Indicators

**Examples:**
- `cross_border_ratio`
- `cross_border_count`

**Motivation:**
Cross-border transactions introduce jurisdictional complexity and are frequently associated with:
- illicit capital flows  
- trade misinvoicing  
- offshore concealment  

High cross-border intensity increases exposure to regulatory arbitrage and weak oversight environments.

---

### 🔹 5. Structuring and Round-Amount Behaviour

**Examples:**
- `round_amount_ratio`
- `structured_ratio`

**Motivation:**
Structured transactions (e.g., repeated amounts just below reporting thresholds) are a classic 
AML typology designed to evade detection systems.

Round-number dominance may indicate:
- artificial transaction splitting  
- non-economic transaction patterns  

---

### 🔹 6. Transaction Velocity and Rapid Movement

**Examples:**
- `rapid_movement_count`
- `rapid_movement_ratio`

**Motivation:**
Illicit funds are often moved quickly through multiple accounts to obscure origin 
(layering stage).

High velocity suggests:
- pass-through accounts  
- mule accounts  
- laundering chains  

---

### 🔹 7. Counterparty and Network Dispersion

**Examples:**
- `unique_counterparties`
- `counterparty_intensity`

**Motivation:**
Unusual dispersion of counterparties may indicate:
- synthetic transaction networks  
- circular trading  
- layering through multiple entities  

A high number of counterparties relative to activity can signal deliberate obfuscation.

---

### 🔹 8. Dormant Account Activation

**Examples:**
- `dormant_account_flag`
- `dormant_activation_count`

**Motivation:**
Dormant accounts that suddenly become active are high-risk because they:
- bypass behavioural baselines  
- may be repurposed for illicit use  

This is a well-documented financial crime trigger.

---

### 🔹 9. High-Risk Corridor and Jurisdiction Exposure

**Examples:**
- `high_risk_country_txn_count`
- `sanctioned_corridor_count`

**Motivation:**
Transactions involving high-risk jurisdictions or sanctioned corridors are strongly associated with:
- sanctions evasion  
- terrorist financing  
- illicit trade flows  

These indicators align with FATF risk-based frameworks.

---

### 🔹 10. Network (Graph) Risk Indicators

**Examples:**
- `graph_degree_centrality`
- `graph_betweenness`
- `graph_pagerank`
- `graph_clustering`

**Motivation:**
Financial crime networks often exhibit identifiable structural properties:
- central nodes coordinating flows  
- intermediaries acting as bridges  
- tightly connected clusters  

Graph metrics capture:
- influence  
- connectivity  
- systemic exposure  

These are critical for detecting hidden relationships not visible in individual transactions.

---

### 🔹 11. Trade-Based Money Laundering (TBML) Indicators

**Examples:**
- `tbml_over_invoicing_count`
- `tbml_under_invoicing_count`
- `tbml_avg_invoice_deviation_ratio`

**Motivation:**
TBML involves manipulation of trade invoices to move value across borders.

Indicators capture:
- price deviations from market benchmarks  
- abnormal trade flows  
- discrepancies in invoice values  

These are essential for detecting cross-border laundering schemes.

---

### 🔹 12. Historical Suspicion and Case Signals

**Examples:**
- `previous_sar_flag`
- `suspicious_flag`

**Motivation:**
Past suspicious activity is one of the strongest predictors of future risk due to:
- behavioural persistence  
- network continuity  
- repeated typologies  

---

### 🔹 Summary

The feature set is designed to capture:

- **Behavioural anomalies** (how transactions deviate from expected patterns)  
- **Structural risk** (network relationships and exposure)  
- **Regulatory signals** (rule-based triggers and typologies)  
- **Domain-specific risks** (e.g., TBML)  

Together, these indicators form a comprehensive representation of financial risk behaviour, 
supporting both statistical modelling and expert interpretation.

</div>
""", unsafe_allow_html=True)

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
