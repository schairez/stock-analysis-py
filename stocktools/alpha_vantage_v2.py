
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

# TODO:
# For exchange rates, latest price for ticker
# only pull info if within the exchange rate window 6am PST - 2PM PST
# temp store the data and check within an interval
# there might be a decorator that handles these wrapped conditions


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
                 symbols=None, symbol=None, from_symbol=None, to_symbol=None,
                 from_currency=None, to_currency=None,
                 out_path='../data/data_raw/'):

        if api_key is None:
            api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        if not api_key or not isinstance(api_key, str):
            raise ValueError(
                'you need to provide a valid Alpha Vantage API key')

        self._data_feed_type = data_feed_type

        time_series: list = ["time_series_intraday", "time_series_daily",
                             "time_series_daily_adjusted", "time_series_weekly", "time_series_weekly_adjusted"]
        fx: list = ["fx_intraday", "fx_daily", "fx_weekly", "fx_monthly"]

        # if data_feed_type not in ["time_series", "currency_exchange_rate"]:
        #     raise ValueError("")

        if self._data_feed_type == "quote_endpoint":
            self._symbol = symbol
            if self._symbol is None:
                raise AttributeError(
                    "NoneType in symbol arg not allowed when data_feed_type is quote_endpoint")
            self._url = FetchAlphaVantage._get_quote_url(
                self._symbol) + f"&apikey={api_key}"

        elif self._data_feed_type == "currency_exchange_rate":
            self._from_currency = from_currency
            self._to_currency = to_currency
            if any(elem is None for elem in [self._from_currency, self._to_currency]):
                raise AttributeError(
                    "NoneType in from_currency or to_currency")
            self._url = FetchAlphaVantage._get_currency_exchange_rate_url(
                self._from_currency, self._to_currency) + f"&apikey={api_key}"

        elif self._data_feed_type in fx:
            self._from_symbol = from_symbol
            self._to_symbol = to_symbol
            if any(elem is None for elem in [self._from_symbol, self._to_symbol]):
                raise AttributeError(
                    "NoneType in from_symbol or to_symbol")

        # time series
        elif self._data_feed_type in time_series:
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
            self._loop.run_until_complete(self._fetch_all_historical())

        # elif data_feed_type in ["currency_exchange_rate"]:
        #     pass

    async def _fetch_all_historical(self):
        # API call frequency is 5 calls per minute and
        # 500 calls per day, so we need to rate limit our requests :/
        async with aiohttp.ClientSession(loop=self._loop) as session:
            await asyncio.gather(*[self._fetch_historical(session, stock_meta.symbol, stock_meta.url) for stock_meta in self._stocks_meta],
                                 return_exceptions=True)

    async def _fetch_historical(self, session, symbol, url):
        async with self._sema, session.get(url) as response:
            response.raise_for_status()
            log.info(
                "Got response [%s] for URL: %s with symbol: %s", response.status, url, symbol)
            data = await response.json()
            # print(data)
            FetchAlphaVantage._write_json_file(self._out_path, symbol, data)
            # 5 calls per minute are permitted by this API
            await asyncio.sleep(60)

    def fetch_quote(self):
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(
            self._fetch_quote(loop))
        return data

    async def _fetch_quote(self, loop):
        async with aiohttp.ClientSession(loop=loop) as client:
            async with client.get(self._url) as response:
                assert response.status == 200
                data = await response.json()
                return data

    @classmethod
    def _get_fx_rate_url(cls, fn_param, from_symbol, to_symbol):
        return cls._BASE_API_URL + f"{fn_param.upper()}" + f"&from_symbol={from_symbol}" \
            + f"to_symbol={to_symbol}"

    @classmethod
    def _get_currency_exchange_rate_url(cls, from_currency, to_currency):
        return cls._BASE_API_URL + "CURRENCY_EXCHANGE_RATE" + f"&from_currency={from_currency}" \
            + f"&to_currency={to_currency}"

    @classmethod
    def _get_quote_url(cls, symbol):
        return cls._BASE_API_URL + "GLOBAL_QUOTE" + \
            "&symbol" + f"={symbol}"

    @classmethod
    def _fx_weekly_url(cls, from_symbol: str, to_symbol: str):
        return cls._BASE_API_URL + "FX_WEEKLY" + \
            + f"&from_symbol={from_symbol}&to_symbol={to_symbol}"

    @classmethod
    def _fx_monthly_url(cls, from_symbol: str, to_symbol: str):
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
    # d = FetchAlphaVantage(data_feed_type="quote_endpoint",
    #                       symbol="ibm").fetch_quote()
    # d = FetchAlphaVantage(data_feed_type="currency_exchange_rate",
    #                       from_currency="usd", to_currency="jpy").fetch_quote()

    d = FetchAlphaVantage(data_feed_type="currency_exchange_rate",
                          from_currency="usd", to_currency="mxn").fetch_quote()
    print(d)
