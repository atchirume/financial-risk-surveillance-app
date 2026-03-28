from pathlib import Path
import pandas as pd

from config import BASE_DIR
from engine.helpers import try_parse_datetime

def read_csv_safe(path: Path, required=False):
    if path.exists():
        return pd.read_csv(path)
    if required:
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.DataFrame()

def load_data():
    customers = read_csv_safe(BASE_DIR / "customers.csv", required=True)
    accounts = read_csv_safe(BASE_DIR / "accounts.csv", required=True)
    transactions = read_csv_safe(BASE_DIR / "transactions.csv", required=True)
    cases = read_csv_safe(BASE_DIR / "cases.csv", required=True)
    customer_summary = read_csv_safe(BASE_DIR / "customer_transaction_summary.csv", required=True)
    customer_networks = read_csv_safe(BASE_DIR / "customer_networks.csv", required=False)
    corporate_links = read_csv_safe(BASE_DIR / "corporate_links.csv", required=False)
    tbml = read_csv_safe(BASE_DIR / "tbml_transactions.csv", required=False)

    customers = try_parse_datetime(customers, ["date_opened", "incorporation_date", "dob"])
    accounts = try_parse_datetime(accounts, ["account_open_date"])
    transactions = try_parse_datetime(transactions, ["txn_datetime"])
    cases = try_parse_datetime(cases, ["case_open_date", "case_close_date"])

    return {
        "customers": customers,
        "accounts": accounts,
        "transactions": transactions,
        "cases": cases,
        "customer_summary": customer_summary,
        "customer_networks": customer_networks,
        "corporate_links": corporate_links,
        "tbml": tbml,
    }
