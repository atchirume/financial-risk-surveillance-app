import numpy as np
import pandas as pd

def minmax_scale(s):
    s = pd.Series(s).astype(float)
    if len(s) == 0:
        return s
    rng = s.max() - s.min()
    if pd.isna(rng) or rng == 0:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - s.min()) / (rng + 1e-9)

def safe_div(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    b = np.where((b == 0) | np.isnan(b), 1e-9, b)
    return a / b

def ensure_columns(df, columns, fill_value=0):
    for col in columns:
        if col not in df.columns:
            df[col] = fill_value
    return df

def try_parse_datetime(df, candidate_cols):
    for col in candidate_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
