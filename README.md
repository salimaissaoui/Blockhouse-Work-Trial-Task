

# Cross-Impact Analysis of Order Flow Imbalance (OFI)

This repository demonstrates how to process high-frequency equity market data, compute multi-level Order Flow Imbalance (OFI), reduce dimensionality with PCA, and attempt a cross-impact analysis on short-term price changes.

## Table of Contents
- [Project Structure](#project-structure)
- [Data Requirements](#data-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Scripts Overview](#scripts-overview)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Project Structure

```
Blockhouse-Work-Trial-Task/
├── data/               # (Optional) placeholder or sample data
├── notebooks/          # Jupyter notebooks for exploratory analysis (not included)
├── scripts/            # Main Python scripts
│   ├── data_retrieval.py
│   ├── ofi.py
│   ├── pca_integration.py
│   ├── cross_impact.py
│   ├── visualization.py
│   └── main.py         # The primary entry point
├── results/            # Outputs (figures, logs, etc.)
├── report.tex          # LaTeX report (1-2 pages)
├── README.md           # This file
└── requirements.txt    # List of Python dependencies
```

1. **`data/`**: Optional directory for storing raw or sample data (no proprietary data should be committed).  
2. **`notebooks/`**: Use this folder for any Jupyter notebooks you create for exploratory data analysis or sanity checks.  
3. **`scripts/`**: Contains the modular scripts that implement data retrieval, OFI computation, PCA integration, cross-impact regression, and visualization.  
4. **`results/`**: For saving output figures (e.g., heatmaps, scatter plots) and logs.  
5. **`report.tex`**: LaTeX source for your short PDF report.  
6. **`README.md`**: You’re reading it now.  
7. **`requirements.txt`**: Lists Python dependencies.

---

## Data Requirements

- **Data Source**: Databento \(*Nasdaq TotalView–ITCH*, MBP-10 schema\).  
- **Symbols**: \(`AAPL`, `AMGN`, `TSLA`, `JPM`, `XOM`\).  
- **LOB Levels**: Up to 5 levels (L0–L4) of bids and asks.  
- **Time Period**: Ideally 1 week or 1 month, but for demonstration, you can retrieve less data due to memory constraints.  

If you have memory limitations, you may retrieve a shorter time window or fewer symbols. Ensure that your credentials and date ranges are properly set in `main.py`.

---

## Installation

1. **Clone This Repository**  
   ```bash
   git clone https://github.com/YourUser/Blockhouse-Work-Trial-Task.git
   cd Blockhouse-Work-Trial-Task
   ```

2. **Create a Virtual Environment (optional, but recommended)**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```

3. **Install Dependencies**  
   Make sure you have a reasonably up-to-date version of Python (3.8+). Then:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   This should install libraries such as `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, and `databento`.

4. **Set Up Databento API Key**  
   - Obtain your API key from [Databento](https://docs.databento.com/) and place it in `main.py` or in an environment variable.  
   - Example in `main.py`:
     ```python
     API_KEY = "db-YourDatabentoKeyHere"
     ```

---

## Usage

1. **Adjust Parameters** in `main.py`:
   - **`START_TIME`** and **`END_TIME`**  
   - **`SYMBOLS`** (default is `["AAPL","AMGN","TSLA","JPM","XOM"]`)  
   - **`LEVELS`** (default 5)  
   - **`LAG_STEPS`** if you want to test a specific lag

2. **Run the Main Script**:
   ```bash
   python scripts/main.py
   ```
   - The script will:
     1. Retrieve data from Databento (for each symbol) into a DataFrame.  
     2. Resample to 1-second (or 1-minute) intervals.  
     3. Compute multi-level OFI (up to `LEVELS` = 5).  
     4. Integrate these OFIs per symbol via PCA.  
     5. Attempt cross-impact regressions (both contemporaneous and lagged).  
     6. Generate correlation heatmaps and scatter plots (saved to `results/` or displayed).  

3. **Check Outputs**:
   - In the console, you’ll see the regression results (R², coefficients).  
   - In your `results/` folder or inline windows, you’ll see figures for correlation heatmaps, scatter plots, etc.  

4. **Compile the Report** (Optional):  
   - If you have a LaTeX environment, compile `report.tex`:
     ```bash
     pdflatex report.tex
     ```
   - This produces `report.pdf`.

---

## Scripts Overview

1. **`data_retrieval.py`**  
   - Contains `get_data(api_key, start_time, end_time, symbols, ...)`  
   - Communicates with Databento’s API to retrieve MBP-10 data for the specified symbols and date range.  

2. **`ofi.py`**  
   - Implements `compute_ofi_multi_symbol(...)` which calculates multi-level OFI for each symbol.  
   - Also includes a helper function for single-symbol OFI if needed.  

3. **`pca_integration.py`**  
   - Provides `integrate_ofi_per_symbol(...)` that applies PCA to OFI columns (e.g., `OFI_L0...OFI_L4`) for each symbol and generates an `Integrated_OFI_<symbol>` column.  

4. **`cross_impact.py`**  
   - Contains functions like `add_price_changes(...)` (computing `price_change`) and `cross_impact_regression(...)` for linear regressions using `Integrated_OFI_` columns.  

5. **`visualization.py`**  
   - Contains plotting helpers like `plot_heatmap(...)` and `plot_scatter(...)`.  

6. **`main.py`**  
   - Orchestrates the entire pipeline.  
   - Fetches data, resamples, computes mid-price, runs OFI + PCA, attempts cross-impact regressions, and generates visualizations.

---

## Troubleshooting

1. **Missing Columns**:  
   - If you see `KeyError: 'bid_px_00'`, confirm that MBP-10 data is actually returned.  
   - Adjust your resampling to ensure some data remains (`.last()`, `.first()`, or `.mean()`).  

2. **No Valid Rows in Regression**:  
   - Often due to heavy resampling or insufficient data coverage.  
   - Try **expanding** the date range or using a coarser time interval (e.g., 1-minute bars).  
   - If memory is limited, consider a narrower date range but ensure it contains enough intraday data.  

3. **Memory Errors**:  
   - If your environment can’t handle the full dataset, reduce the date range or the symbols.  
   - Alternatively, resample to a coarser interval to reduce row count.  

4. **Plot Freezing**:  
   - If the pivot for cross-correlation is too large, you can sample down to fewer rows before plotting.  

5. **API Key Issues**:  
   - Double-check you have the correct `db-xxxx` format key from [Databento](https://docs.databento.com/).  
   - If your free credits are used up, you may need to purchase more or reduce the requested data.

---


### Contact

If you have any questions or issues running the code, feel free to open an issue on this repository or reach out at:

```
Your Name
Your Contact Email
```

Happy Analyzing!
