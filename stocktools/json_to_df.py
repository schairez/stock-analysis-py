import json
import pandas as pd


def json_to_df(file_name: str,
               path=None,
               columns=['Date', 'Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']):

    def read_json_file(file_name: str) -> dict:
        if path is None:
            path_to_file = f'../data/data_raw/{file_name}'
        else:
            path_to_file = path
        with open(path_to_file) as f:
            return json.load(f)

    def convert_response(d):
        for date, stock_data in d['Time Series (Daily)'].items():
            r = {'Date': date}
            r.update(stock_data)
            yield r

    df = pd.DataFrame(convert_response(read_json_file(file_name)))
    df.rename(columns={'1. open': 'Open',
                       '2. high': 'High',
                       '3. low': 'Low',
                       '4. close': 'Close',
                       '5. adjusted close': 'AdjClose',
                       '6. volume': 'Volume',
                       '7. dividend amount': 'DivAmount',
                       '8. split coefficient': 'SplitRatio'}, inplace=True)

    df['Date'] = pd.to_datetime(df['Date'])
    df[["Open", "High", "Low", "Close", "AdjClose"]] = df[[
        "Open", "High", "Low", "Close", "AdjClose"]].astype("float64")
    df["Volume"] = df["Volume"].astype("int64")
    df["AdjFactor"] = df["AdjClose"] / df["Close"]
    df["AdjOpen"] = df["Open"] * df["AdjFactor"]
    df["AdjHigh"] = df["High"] * df["AdjFactor"]
    df["AdjLow"] = df["Low"] * df["AdjFactor"]

    df.sort_values(by=['Date'], inplace=True)

    df['SMA_20day'] = df[['AdjClose']].rolling(window=20).mean()

    df['EMA_20day'] = df[['AdjClose']].ewm(
        span=20, min_periods=20, adjust=False).mean()

    # df.set_index('Date', inplace=True)
    # df.sort_index(inplace=True)
    # extract the default columns
    # df = df[columns]
    return df
