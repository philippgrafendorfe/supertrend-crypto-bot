import ccxt
import config
import pprint

class Test:
    def __init__(self, **kwargs):
        self.test = kwargs["test"]


config = {"test": 1}

test = Test(**config)


# exchange_id = 'binance'
# exchange_class = getattr(ccxt, exchange_id)
# exchange = exchange_class({
#     'apiKey': config.BINANCE_API_KEY,
#     'secret': config.BINANCE_SECRET_KEY,
# })


exchange_bitpanda = ccxt.bitpanda({
    "apiKey": config.BITPANDA_API_KEY
})

SYMBOL = 'ETH/BTC'

exchange_binance = ccxt.binance({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_SECRET_KEY,
})
# exchange_binance.set_sandbox_mode(True)
# markets = exchange_binance.load_markets()
#
# for market in markets:
#     print(market)

ticker = exchange_binance.fetch_ticker(SYMBOL)
pprint.pprint(ticker)

fees = exchange_binance.fetch_fees()
pass
#
# ohlcv = exchange_binance.fetch_ohlcv(symbol=SYMBOL, timeframe='1m', limit=1)
# for candle in ohlcv:
#     print(candle)
#
# order_book = exchange_binance.fetch_order_book(symbol=SYMBOL, limit=5)
# print(order_book)

# balance = exchange_binance.fetch_balance()
# pprint.pprint(balance)


