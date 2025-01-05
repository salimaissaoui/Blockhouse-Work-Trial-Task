# Import Necessary Libraries
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Compute OFI Metrics
def compute_ofi(df, levels=5):
    """
    Compute the Order Flow Imbalance (OFI) metric for multiple levels.
    """
    ofi_metrics = []
    for level in range(1, levels + 1):
        buy_delta = df[f'bid_size_{level}'].diff() * np.sign(df[f'bid_price_{level}'].diff())
        sell_delta = df[f'ask_size_{level}'].diff() * np.sign(df[f'ask_price_{level}'].diff())
        ofi = buy_delta - sell_delta
        ofi_metrics.append(ofi)

    ofi_df = pd.concat(ofi_metrics, axis=1)
    ofi_df.columns = [f'OFI_L{level}' for level in range(1, levels + 1)]
    return ofi_df

# Step 2: Integrate Multi-Level OFIs Using PCA
def integrate_ofi_with_pca(ofi_df):
    """
    Use PCA to integrate multi-level OFI metrics into a single metric.
    """
    pca = PCA(n_components=1)
    integrated_ofi = pca.fit_transform(ofi_df)
    ofi_df['Integrated_OFI'] = integrated_ofi
    return ofi_df, pca

# Step 3: Analyze Cross-Impact
def cross_impact_analysis(df, horizon_minutes=1):
    """
    Analyze contemporaneous and lagged cross-impact of OFI on price changes.
    """
    df['price_change'] = df['mid_price'].diff()
    df['lagged_ofi'] = df['Integrated_OFI'].shift(horizon_minutes)
    
    # Contemporaneous analysis
    contemporaneous_reg = LinearRegression()
    X_contemp = df[['Integrated_OFI']].dropna()
    y_contemp = df['price_change'].loc[X_contemp.index]
    contemporaneous_reg.fit(X_contemp, y_contemp)
    
    # Predictive power analysis
    lagged_reg = LinearRegression()
    X_lagged = df[['lagged_ofi']].dropna()
    y_lagged = df['price_change'].loc[X_lagged.index]
    lagged_reg.fit(X_lagged, y_lagged)
    
    return {
        'contemporaneous_r2': contemporaneous_reg.score(X_contemp, y_contemp),
        'predictive_r2': lagged_reg.score(X_lagged, y_lagged)
    }

# Step 4: Visualization
def plot_heatmap(df, title):
    """
    Generate a heatmap for cross-impact analysis.
    """
    corr = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(title)
    plt.show()

def plot_scatter(df, x_col, y_col, title):
    """
    Generate scatter plots for OFI trends.
    """
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=df[x_col], y=df[y_col])
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.show()

# Step 5: Execution Workflow
def main():
    # Load data
    import databento as db

    client = db.Historical('db-UYfWvmmU6YLwgy6FtCqYnfxHKvHvE')
    data = client.timeseries.get_range(
        dataset='XNAS.ITCH',
        schema='mbp-10',
        symbols=['AAPL', 'AMGN', 'TSLA', 'JPM', 'XOM'],  # Replace with desired symbols
        start='2024-12-31T00:00:00Z',  # Replace with desired start time
        end='2025-01-03T23:59:59Z'     # Replace with desired end time
    )

    df = data.to_df()
    
    # Compute mid-price
    df['mid_price'] = (df['bid_price_1'] + df['ask_price_1']) / 2

    # Step 1: Compute OFI metrics
    ofi_df = compute_ofi(df)

    # Step 2: Integrate OFIs using PCA
    ofi_df, pca_model = integrate_ofi_with_pca(ofi_df)
    df = pd.concat([df, ofi_df], axis=1)

    # Step 3: Analyze cross-impact
    results = cross_impact_analysis(df, horizon_minutes=1)
    print(f"Contemporaneous R2: {results['contemporaneous_r2']}")
    print(f"Predictive R2: {results['predictive_r2']}")

    # Step 4: Visualizations
    plot_heatmap(ofi_df.corr(), title="OFI Heatmap")
    plot_scatter(df, 'Integrated_OFI', 'price_change', "Integrated OFI vs. Price Change")

if __name__ == "__main__":
    main()
