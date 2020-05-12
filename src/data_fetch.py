import os
import json
import logging
import aiohttp
import asyncio
# import async_timeout
# import aiofiles
import sys
from collections import namedtuple

__author__ = 'Sergio Chairez'


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging


ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
BASE_API_URL = "https://www.alphavantage.co/query?function="
API_URL_TIME_SERIES_ADJ = BASE_API_URL + \
    "TIME_SERIES_DAILY_ADJUSTED&symbol="


async def fetch_all(stocks_meta, loop):
    # API call frequency is 5 calls per minute and
    # 500 calls per day, so we need to rate limit our requests :/
    rate_limit = 5
    sema = asyncio.Semaphore(rate_limit)
    async with aiohttp.ClientSession(loop=loop) as session:
        await asyncio.gather(*[fetch(sema, session, stock_meta.symbol, stock_meta.url)
                               for stock_meta in stocks_meta], return_exceptions=True)


async def fetch(sema, session, symbol, url):
    async with sema, session.get(url) as response:
        response.raise_for_status()
        log.info(
            "Got response [%s] for URL: %s with symbol: %s", response.status, url, symbol)
        data = await response.json()
        write_json_file(symbol, data)
        # 5 calls per minute are permitted by this API
        await asyncio.sleep(60)


def write_json_file(symbol, data):
    with open(f'../data/data_raw/data_{symbol}.json', "w") as write_json:
        json.dump(data, write_json, indent=2, sort_keys=False)

    log.info("Wrote results for symbol: %s", symbol)


# +"datatype=csv"

# TODO
# maybe compress the json with gzip and use apache arrow (pyarrow) to decompress the json.gz
# use aws data wrangler, pyarrow,Amazon Redshift, AWS Glue, Amazon Athena, Amazon EMR
# prepare and process data with amazon sagemaker

# calculate 52WkLow, 52WkHigh

if __name__ == "__main__":
    StockInfo: tuple = namedtuple('Stock', ['symbol', 'url'])

    symbols: list = ['aapl', 'abt', 'adbe', 'amd', 'amzn', 'baba', 'brkb', 'c', 'cmcsa',
                     'cost', 'crm', 'dell', 'f', 'fb', 'googl', 'ibm', 'intc', 'intu', 'jnj',
                     'jpm', 'msft', 'mu', 'nflx', 'nke', 'nvda', 'orcl', 'pfe', 'pg',
                     'pypl', 'sbux', 't', 'tsla', 'twtr', 'unh', 'v', 'vz', 'wfc', 'wmt'
                     ]

    print(sorted(symbols))

    stocks_meta: list = [StockInfo(symbol,
                                   API_URL_TIME_SERIES_ADJ + symbol + "&outputsize=full" +
                                   f"&apikey={ALPHA_VANTAGE_API_KEY}")
                         for symbol in symbols]

    print(ALPHA_VANTAGE_API_KEY)
    # print(stocks_meta)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(fetch_all(stocks_meta,  loop))
