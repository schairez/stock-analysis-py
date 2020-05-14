from stocktools.json_to_df import json_to_df
from dashboard.plot_ohlc import plot_dashboard


if __name__ == "__main__":

    aapl_df = json_to_df('data_aapl.json', path="data/data_raw/data_aapl.json")
    plot_dashboard(aapl_df, title="Apple Stock")
