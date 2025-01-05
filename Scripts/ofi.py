# ofi.py

import pandas as pd
import numpy as np

def compute_ofi_for_symbol(df: pd.DataFrame, levels: int = 5) -> pd.DataFrame:
    """
    Compute multi-level OFI for a single symbol's DataFrame.
    Expects columns like 'bid_px_00', 'ask_px_00', 'bid_sz_00', 'ask_sz_00'.
    """
    ofi_metrics = []
    for level in range(levels):
        level_str = f"{level:02d}"
        bid_px_col = f"bid_px_{level_str}"
        ask_px_col = f"ask_px_{level_str}"
        bid_sz_col = f"bid_sz_{level_str}"
        ask_sz_col = f"ask_sz_{level_str}"

        if any(col not in df.columns for col in [bid_px_col, ask_px_col, bid_sz_col, ask_sz_col]):
            print(f"Warning: Missing some columns for level {level_str}. Skipping.")
            continue

        # Buy delta
        buy_delta = df[bid_sz_col].diff() * np.sign(df[bid_px_col].diff())
        # Sell delta
        sell_delta = df[ask_sz_col].diff() * np.sign(df[ask_px_col].diff())
        # OFI
        ofi_level = buy_delta - sell_delta
        ofi_metrics.append(ofi_level)

    if not ofi_metrics:
        return pd.DataFrame()

    ofi_df = pd.concat(ofi_metrics, axis=1)
    ofi_df.columns = [f"OFI_L{i}" for i in range(levels)]
    return ofi_df

def compute_ofi_multi_symbol(df_all: pd.DataFrame, levels: int = 5) -> pd.DataFrame:
    """
    Compute multi-level OFI per symbol, then stitch results back together.
    :param df_all: DataFrame with multiple symbols, must have a 'symbol' column.
    :param levels: Number of levels to process.
    :return: Single DataFrame with the same rows, plus columns: OFI_L0..OFI_L4.
    """
    # We'll build an empty container for final results
    results = []
    # Group by symbol so each group is one symbol's data
    for symbol, df_sym in df_all.groupby("symbol"):
        # Sort by time within each symbol
        df_sym = df_sym.sort_values("ts_event").copy()
        ofi_df_sym = compute_ofi_for_symbol(df_sym, levels)
        # Merge
        df_sym_ofi = pd.concat([df_sym.reset_index(drop=True), ofi_df_sym.reset_index(drop=True)], axis=1)
        results.append(df_sym_ofi)

    # Concatenate all symbol frames back
    df_out = pd.concat(results, axis=0)
    # Sort by time and symbol again
    df_out.sort_values(["ts_event", "symbol"], inplace=True)
    df_out.reset_index(drop=True, inplace=True)
    return df_out
