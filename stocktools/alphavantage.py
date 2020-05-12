
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
    _API_URL_TIME_SERIES_ADJ = _BASE_API_URL + \
        "TIME_SERIES_DAILY_ADJUSTED&symbol="
    _RATE_LIMIT = 5

    def __init__(self, api_key=None,
                 symbols: list = [],
                 out_path='../data/data_raw/'):

        if api_key is None:
            api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        if not api_key or not isinstance(api_key, str):
            raise ValueError(
                'you need to provide a valid Alpha Vantage API key')
        if not isinstance(symbols, list):
            raise ValueError('symbols parameter needs to be a list type')
        self._out_path = out_path
        StockInfo: tuple = namedtuple('Stock', ['symbol', 'url'])
        self._stocks_meta: list = [
            StockInfo(symbol,
                      FetchAlphaVantage._API_URL_TIME_SERIES_ADJ + symbol +
                      "&outputsize=full" + f"&apikey={api_key}")
            for symbol in symbols
        ]

        self._loop = asyncio.get_event_loop()
        self._loop.set_debug(True)
        self._sema = asyncio.Semaphore(FetchAlphaVantage._RATE_LIMIT)
        self._loop.run_until_complete(self._fetch_all())

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

    FetchAlphaVantage(symbols=symbols)
