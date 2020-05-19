
"""
License: MIT
Copyright (c) 2020 - Sergio Chairez 
"""


import os
import json
import logging
import aiohttp
import asyncio
import sys
from collections import namedtuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging


class FetchAlphaVantage(object):
    _BASE_API_URL = "https://www.alphavantage.co/query?function="
    _API_URL_TIME_SERIES_DAILY_ADJ = _BASE_API_URL + \
        "TIME_SERIES_DAILY_ADJUSTED&symbol="
    _API_URL_TIME_SERIES_WEEKLY_ADJ = _BASE_API_URL + \
        "TIME_SERIES_WEEKLY_ADJUSTED&symbol="
    _API_URL_FOREX_DAILY = _BASE_API_URL + "FX_DAILY"
    _API_URL_FOREX_WEEKLY = _BASE_API_URL + "FX_WEEKLY"

    _RATE_LIMIT = 5

    def __init__(self, api_key=None, data_feed_type: str = "time_series_weekly_adjusted",
                 symbols=None, symbol=None, from_ticker=None, to_ticker=None,
                 out_path='../data/data_raw/'):

        if api_key is None:
            api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        if not api_key or not isinstance(api_key, str):
            raise ValueError(
                'you need to provide a valid Alpha Vantage API key')

        time_series: list = ["time_series_intraday", "time_series_daily",
                             "time_series_daily_adjusted", "time_series_weekly", "time_series_weekly_adjusted"]
        currency_exchange: list = [
            "currency_exchange_rate", "fx_intraday", "fx_daily", "fx_weekly", "fx_monthly"]

        # if data_feed_type not in ["time_series", "currency_exchange_rate"]:
        #     raise ValueError("")

        if data_feed_type == "quote_endpoint":
            self._symbol = symbol
            if self._symbol is None:
                raise AttributeError("NoneType in symbol arg not allowed")
            print(FetchAlphaVantage._quote_url(self._symbol))


        # time series
        elif data_feed_type in time_series:
            self._symbols = symbols or []
            if not self._symbols:
                raise ValueError("symbols arg is an empty sequence")
            self._out_path = out_path
            StockInfo: tuple = namedtuple('Stock', ['symbol', 'url'])
            self._stocks_meta: list = [
                StockInfo(symbol,
                          FetchAlphaVantage._API_URL_TIME_SERIES_DAILY_ADJ + symbol +
                          "&outputsize=full" + f"&apikey={api_key}")
                for symbol in self._symbols
            ]
            self._loop = asyncio.get_event_loop()
            self._loop.set_debug(True)
            self._sema = asyncio.Semaphore(FetchAlphaVantage._RATE_LIMIT)
            self._loop.run_until_complete(self._fetch_all())
        # currency exchanges
        elif data_feed_type in currency_exchange:
            pass

        # elif data_feed_type in ["currency_exchange_rate"]:
        #     pass

    async def _fetch_all(self):
        # API call frequency is 5 calls per minute and
        # 500 calls per day, so we need to rate limit our requests :/
        async with aiohttp.ClientSession(loop=self._loop) as session:
            await asyncio.gather(*[self._fetch(session, stock_meta.symbol, stock_meta.url) for stock_meta in self._stocks_meta],
                                 return_exceptions=True)

    async def _fetch(self, session, symbol, url):
        async with self._sema, session.get(url) as response:
            response.raise_for_status()
            log.info(
                "Got response [%s] for URL: %s with symbol: %s", response.status, url, symbol)
            data = await response.json()
            # print(data)
            FetchAlphaVantage._write_json_file(self._out_path, symbol, data)
            await asyncio.sleep(60)
            # 5 calls per minute are permitted by this API

    @classmethod
    def _quote_url(cls, symbol):
        return cls._BASE_API_URL + "GLOBAL_QUOTE" + \
            "&symbol" + f"={symbol}"

    @classmethod
    def _fx_weekly_url(cls, from_ticker: str, to_ticker: str):
        return cls._BASE_API_URL + "FX_WEEKLY" + \
            + f"&from_symbol={from_ticker}&to_symbol={to_ticker}"

    @classmethod
    def _fx_monthly_url(cls, from_ticker: str, to_ticker: str):
        pass

    @staticmethod
    def _write_json_file(out_path, symbol, data):
        with open(f'../data/data_raw/data_{symbol}.json', "w") as write_json:
            json.dump(data, write_json, indent=2, sort_keys=False)

        log.info("Wrote results for symbol: %s", symbol)


if __name__ == "__main__":
    symbols: list = ['aapl', 'abt', 'adbe', 'amd', 'amzn', 'baba',
                     'brkb', 'c', 'cmcsa', 'cost', 'crm', 'dell', 'f', 'fb', 'googl', 'ibm', 'intc',
                     'intu', 'jnj', 'jpm', 'msft', 'mu', 'nflx', 'nke', 'nvda', 'orcl', 'pfe', 'pg',
                     'pypl', 'sbux', 't', 'tsla', 'twtr', 'unh', 'v', 'vz', 'wfc', 'wmt']

    # FetchAlphaVantage(symbols=symbols)
    FetchAlphaVantage(data_feed_type="quote_endpoint", symbol="ibm")
