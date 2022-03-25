from typing import Optional

import ccxt
from pydantic import BaseModel

import config

EXCHANGE_BITPANDA = ccxt.bitpanda({
    "apiKey": config.BITPANDA_API_KEY
})

EXCHANGE_BINANCE = ccxt.binance({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_SECRET_KEY,
})

# SYMBOL1 = 'ETH/EUR'
SYMBOL1 = 'BTC/EUR'
SYMBOL2 = 'ETH/BTC'
SYMBOL3 = 'EUR/ETH'
SYMBOL4 = 'ETH/EUR'
SYMBOL5 = 'EUR/BTC'


class Ticker(BaseModel):
    average: Optional[float] = None
    high: float
    low: float
    symbol: str


def arbitrage_possibility():
    ticker_eth_eur = Ticker.parse_obj(EXCHANGE_BITPANDA.fetch_ticker(SYMBOL4))
    ticker_eur_btc = Ticker.parse_obj(EXCHANGE_BITPANDA.fetch_ticker(SYMBOL5))
    eq_exchange_avg = ticker_eth_eur.average * ticker_eur_btc.average

    actual_exchange_avg = Ticker.parse_obj(EXCHANGE_BITPANDA.fetch_ticker(SYMBOL2)).average

    result = eq_exchange_avg > actual_exchange_avg
    diff = eq_exchange_avg - actual_exchange_avg
    if result:
        print(f"arbitrage possibility with spread of {diff / actual_exchange_avg * 100}%")

    return result


def main():
    arbitrage_possible = arbitrage_possibility()
    # ticker1_exc = EXCHANGE_BITPANDA.fetch_ticker(symbol=SYMBOL)
    # ticker2_exc = EXCHANGE_BINANCE.fetch_ticker(symbol=SYMBOL)
    #
    # ticker1 = Ticker.parse_obj(ticker1_exc)
    # ticker2 = Ticker.parse_obj(ticker2_exc)
    #
    # if not ticker2.average:
    #     ticker2.average = (ticker2.high + ticker2.low) / 2
    #
    # absolute_diff = abs(ticker1.average - ticker2.average)
    #
    # market = EXCHANGE_BITPANDA.market(symbol=SYMBOL)
    # fetch_order_book = EXCHANGE_BITPANDA.fetch_order_book(symbol=SYMBOL)
    # ohlcv = EXCHANGE_BITPANDA.fetch_ohlcv(symbol=SYMBOL)

    pass


if __name__ == "__main__":
    main()
