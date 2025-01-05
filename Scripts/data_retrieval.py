# data_retrieval.py

import databento as db
import pandas as pd

def get_data(
    api_key: str,
    start_time: str,
    end_time: str,
    symbols=None,
    dataset: str = 'XNAS.ITCH',
    schema: str = 'mbp-10'
) -> pd.DataFrame:
    """
    Fetch data from Databento for multiple symbols, return single DataFrame
    with a 'symbol' column distinguishing each symbol's data.

    :param api_key: Databento API key
    :param start_time: Start time (ISO 8601)
    :param end_time: End time (ISO 8601)
    :param symbols: List of symbols, e.g. ['AAPL','AMGN','TSLA','JPM','XOM']
    :param dataset: 'XNAS.ITCH' by default
    :param schema: 'mbp-10' by default
    :return: DataFrame containing all symbols' data stacked together
    """
    if symbols is None:
        symbols = ['AAPL', 'AMGN', 'TSLA', 'JPM', 'XOM']

    client = db.Historical(api_key)

    all_frames = []
    for sym in symbols:
        print(f"Retrieving data for {sym}...")
        data = client.timeseries.get_range(
            dataset=dataset,
            schema=schema,
            symbols=[sym],
            start=start_time,
            end=end_time
        )
        df_sym = data.to_df()
        df_sym['symbol'] = sym  # Tag each row with the symbol
        all_frames.append(df_sym)

    # Concatenate all data
    df_all = pd.concat(all_frames, axis=0)
    # Sort by time (if 'ts_event' is your timestamp column)
    df_all.sort_values(['ts_event', 'symbol'], inplace=True)
    return df_all
