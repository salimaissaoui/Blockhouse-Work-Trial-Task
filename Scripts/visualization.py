# visualization.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_heatmap(df: pd.DataFrame, title: str = "Heatmap"):
    """
    Generate a heatmap from the correlation matrix of df.
    """
    if df.empty:
        print("Warning: Attempting to plot heatmap on an empty DataFrame.")
        return

    corr = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(title)
    plt.show()

def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, title: str):
    """
    Generate a scatter plot for two columns in df.
    """
    if df.empty:
        print("Warning: Attempting to plot scatter on an empty DataFrame.")
        return

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x=x_col, y=y_col, alpha=0.6)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.show()
