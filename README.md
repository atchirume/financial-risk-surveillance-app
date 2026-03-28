# Financial Risk Surveillance Enterprise App

A Streamlit-based financial risk surveillance platform prototype for banks and Financial Intelligence Units.

## Features
- End-to-end AML / financial risk surveillance pipeline
- Rules engine
- Graph/network risk features
- TBML features
- Supervised + anomaly models
- Capacity-based top-% alerting
- Dashboard
- Alert queue
- Entity detail page
- Export buttons

## Folder structure
- `app.py` — Streamlit entry point
- `config.py` — project configuration
- `engine/` — data loading, feature engineering, modelling, fusion, exports
- `ui/` — Streamlit views
- `requirements.txt` — Python dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Expected input files in your configured BASE_DIR
- customers.csv
- accounts.csv
- transactions.csv
- cases.csv
- customer_transaction_summary.csv
- customer_networks.csv (optional)
- corporate_links.csv (optional)
- tbml_transactions.csv (optional)
