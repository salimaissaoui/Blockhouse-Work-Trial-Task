# pca_integration.py

from typing import Tuple
import pandas as pd
from sklearn.decomposition import PCA

def integrate_ofi_per_symbol(df: pd.DataFrame, levels: int = 5) -> pd.DataFrame:
    """
    For each symbol, run PCA on the columns OFI_L0..OFI_L{levels-1} to get a single 'Integrated_OFI_<symbol>'.
    We'll return the full DF plus these integrated columns.
    """
    symbols = df["symbol"].unique()
    df_out = df.copy()

    for sym in symbols:
        # Filter rows for this symbol
        mask = (df_out["symbol"] == sym)
        df_sym = df_out.loc[mask]

        # Find columns OFI_L0..OFI_L4 (or up to levels-1)
        ofi_cols = [f"OFI_L{i}" for i in range(levels) if f"OFI_L{i}" in df_sym.columns]
        # Drop NaN
        df_sym_clean = df_sym.dropna(subset=ofi_cols)

        # If there's no data or not enough columns, skip
        if df_sym_clean.empty or len(ofi_cols) == 0:
            print(f"No valid OFI columns or data for symbol {sym}, skipping PCA.")
            continue

        # Fit PCA with n_components=1
        pca = PCA(n_components=1)
        principal_component = pca.fit_transform(df_sym_clean[ofi_cols])

        # Insert Integrated_OFI_<sym> into df_out
        col_name = f"Integrated_OFI_{sym}"
        df_out[col_name] = None  # Temporarily fill with None

        # Align by index
        df_out.loc[df_sym_clean.index, col_name] = principal_component.ravel()

    return df_out
