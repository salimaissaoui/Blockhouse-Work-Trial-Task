# cross_impact.py

import pandas as pd
from sklearn.linear_model import LinearRegression

def add_price_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-symbol price change for each row. We'll define 'mid_price'
    = (bid_px_00 + ask_px_00)/2 or however you've done it, then store a new
    column price_change_<symbol>.
    """
    df_out = df.copy()
    # Group by symbol, compute .diff() of mid_price
    df_out["price_change"] = df_out.groupby("symbol")["mid_price"].diff()
    # We'll rename it below for each symbol, or keep a single column if we do group analysis.
    return df_out

def cross_impact_regression(df: pd.DataFrame, lag_steps=0) -> pd.DataFrame:
    """
    For each symbol's price_change, regress on integrated_OFI columns from all symbols.
    If lag_steps > 0, shift the integrated_OFI columns by that many steps for cross-predictive analysis.

    Returns a DataFrame summarizing regression coefficients & R^2 for each symbol.
    """
    # Identify which columns are "Integrated_OFI_<sym>"
    integrated_cols = [c for c in df.columns if c.startswith("Integrated_OFI_")]
    symbols = df["symbol"].unique()
    results = []

    # If we want lag, create shifted versions of each Integrated_OFI column
    if lag_steps > 0:
        for col in integrated_cols:
            df[col + f"_lag{lag_steps}"] = df[col].shift(lag_steps)
        # Then we update integrated_cols to be the lagged ones
        integrated_cols = [col + f"_lag{lag_steps}" for col in integrated_cols]

    # For each symbol, we do a regression:
    for sym in symbols:
        # Filter rows for that symbol
        df_sym = df[df["symbol"] == sym].copy()
        # We have a 'price_change' column
        df_sym = df_sym.dropna(subset=["price_change"] + integrated_cols)

        if df_sym.empty:
            print(f"No valid rows for symbol {sym} in regression.")
            continue

        X = df_sym[integrated_cols]
        y = df_sym["price_change"]
        if X.empty:
            continue

        model = LinearRegression()
        model.fit(X, y)
        r2 = model.score(X, y)
        coefs = model.coef_

        row_dict = {
            "symbol": sym,
            "r2": r2,
        }
        # Attach each integrated col’s coefficient
        for col_name, coef_val in zip(X.columns, coefs):
            row_dict[f"coef_{col_name}"] = coef_val

        results.append(row_dict)

    return pd.DataFrame(results)
