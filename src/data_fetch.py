import os
import json
import logging
import aiohttp
import asyncio
import async_timeout
import aiofiles
import sys
from collections import namedtuple

__author__ = 'Sergio Chairez'
__version__ = '1.1.0'


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging


ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
BASE_API_URL = "https://www.alphavantage.co/query?function="
API_URL_TIME_SERIES_ADJ = BASE_API_URL + \
    "TIME_SERIES_DAILY_ADJUSTED&symbol="


async def fetch_all(Stocks, loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        await asyncio.gather(*[fetch(session, stock_meta.symbol, stock_meta.url) for stock_meta in Stocks], return_exceptions=True)
        # print(f"results ARE {results}")
        # return results


async def fetch(session, symbol, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            response.raise_for_status()
            logger.info(
                "Got response [%s] for URL: %s with symbol: %s", response.status, url, symbol)
            data = await response.json()
            write_json_file(symbol, data)


def write_json_file(symbol, data):
    with open(f'../data/data_{symbol}.json', "w") as write_json:
        json.dump(data, write_json, indent=2, sort_keys=False)

    logger.info("Wrote results for symbol: %s", symbol)


# +"datatype=csv"

# call frequency is 5 calls per minute

if __name__ == "__main__":
    Stock = namedtuple('Stock', ['symbol', 'url'])
    symbols = ['ibm', 'aapl', 'tsla', 'msft', 'nflx', 'amzn']
    Stocks = [Stock(symbol, API_URL_TIME_SERIES_ADJ +
                    symbol + "&outputsize=full" + f"&apikey={ALPHA_VANTAGE_API_KEY}") for symbol in symbols]

    print(ALPHA_VANTAGE_API_KEY)
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(fetch_all(Stocks,  loop))
