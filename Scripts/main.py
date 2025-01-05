# main.py
import pandas as pd
import numpy as np

from data_retrieval import get_data
from ofi import compute_ofi_multi_symbol
from pca_integration import integrate_ofi_per_symbol
from cross_impact import add_price_changes, cross_impact_regression
from visualization import plot_heatmap, plot_scatter

def main():
    # -- Parameters --
    API_KEY = "db-UYfWvmmU6YLwgy6FtCqYnfxHKvHvE"  # your Databento key
    START_TIME = "2024-12-31T00:00:00Z"
    END_TIME   = "2025-01-03T23:59:59Z"
    SYMBOLS    = ["AAPL", "AMGN", "TSLA", "JPM", "XOM"]
    LEVELS     = 5   # e.g., 00..04
    LAG_STEPS  = 60  # if each row ~ 1 second, 60 => 1-minute lag for demonstration

    # 1. Retrieve multi-stock data
    df_all = get_data(API_KEY, START_TIME, END_TIME, SYMBOLS)
    print("All Data Columns:", df_all.columns.tolist())

    # Ensure ts_event is datetime for resampling
    df_all["ts_event"] = pd.to_datetime(df_all["ts_event"], utc=True)

    # 2. Resample to reduce row count
    df_all.set_index("ts_event", inplace=True)
    df_resampled = (
        df_all
        .groupby("symbol", group_keys=True)
        .resample("1S")            # 1-second interval
        .mean(numeric_only=True)   # or .last(), .first() if you prefer
    )
    df_resampled.reset_index(inplace=True)

    # 3. Compute mid_price from top-of-book
    if "bid_px_00" in df_resampled.columns and "ask_px_00" in df_resampled.columns:
        df_resampled["mid_price"] = (df_resampled["bid_px_00"] + df_resampled["ask_px_00"]) / 2
    else:
        raise ValueError("No 'bid_px_00'/'ask_px_00' columns found after resampling. Check data schema.")

    # 4. Compute multi-level OFI
    df_ofi = compute_ofi_multi_symbol(df_resampled, levels=LEVELS)
    print("After OFI, columns are:", df_ofi.columns.tolist())

    # 5. PCA integration per symbol
    df_pca = integrate_ofi_per_symbol(df_ofi, levels=LEVELS)
    print("After PCA, columns are:", df_pca.columns.tolist())

    # 6. Compute price changes per symbol
    df_final = add_price_changes(df_pca)
    print("Sample rows with price_change:\n", df_final.head(5))

    # 7. Contemporaneous cross-impact
    print("\n=== CONTEMPORANEOUS CROSS-IMPACT REGRESSION ===")
    result_contemp = cross_impact_regression(df_final, lag_steps=0)
    if result_contemp.empty:
        print("No valid rows for contemporaneous regression.")
    else:
        print("Contemporaneous Cross-Impact Results (R² and Coefficients):")
        print(result_contemp.to_string(index=False))

    # 8. Lagged cross-impact
    print(f"\n=== LAG-{LAG_STEPS} CROSS-IMPACT REGRESSION ===")
    result_lag = cross_impact_regression(df_final, lag_steps=LAG_STEPS)
    if result_lag.empty:
        print(f"No valid rows for lag-{LAG_STEPS} regression.")
    else:
        print(f"Lag-{LAG_STEPS} Cross-Impact Results (R² and Coefficients):")
        print(result_lag.to_string(index=False))

    # 9. Visualizations
    #    (A) Single-symbol correlation (pick AAPL)
    df_aapl = df_final[df_final["symbol"] == "AAPL"].dropna(subset=[f"OFI_L{i}" for i in range(LEVELS)])
    ofi_cols_aapl = [f"OFI_L{i}" for i in range(LEVELS)] + ["Integrated_OFI_AAPL"]

    if df_aapl.empty:
        print("AAPL data empty after dropping NaN, skipping single-symbol heatmap.")
    else:
        sub_aapl = df_aapl[ofi_cols_aapl].dropna()
        if sub_aapl.empty:
            print("No valid data for AAPL correlation heatmap.")
        else:
            plot_heatmap(sub_aapl, "AAPL OFI Features Correlation Heatmap")

    #    (B) Cross-symbol integrated OFI correlation heatmap
    integrated_cols = [col for col in df_final.columns if col.startswith("Integrated_OFI_")]
    if not integrated_cols:
        print("No integrated OFI columns found, skipping cross-symbol correlation.")
    else:
        pivot_int_ofi = df_final.pivot_table(
            index="ts_event",
            columns="symbol",
            values=integrated_cols
        )
        # Flatten columns
        pivot_int_ofi.columns = [f"{col[0]}_{col[1]}" for col in pivot_int_ofi.columns]
        pivot_int_ofi.dropna(how="all", inplace=True)

        if pivot_int_ofi.empty:
            print("Pivoted integrated OFI is empty, skipping cross-stock heatmap.")
        else:
            # If large, sample down
            if pivot_int_ofi.shape[0] > 5000:
                pivot_int_ofi = pivot_int_ofi.sample(n=5000, random_state=42)
            plot_heatmap(pivot_int_ofi, "Cross-Stock Integrated OFI Correlation")

    #    (C) Scatter: AAPL's integrated OFI vs. price change
    if "Integrated_OFI_AAPL" in df_aapl.columns:
        df_aapl_scatter = df_aapl.dropna(subset=["Integrated_OFI_AAPL", "price_change"])
        if not df_aapl_scatter.empty:
            plot_scatter(df_aapl_scatter, "Integrated_OFI_AAPL", "price_change",
                         "AAPL: Integrated OFI vs. Price Change")
        else:
            print("No valid AAPL rows for scatter plot.")
    else:
        print("No 'Integrated_OFI_AAPL' in df_aapl columns, skipping scatter.")

    print("Done.")

if __name__ == "__main__":
    main()
