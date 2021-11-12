import ccxt
import config
import schedule
import pandas as pd
# import winsound
#
# duration = 1000  # milliseconds
# freq = 440  # Hz

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

import warnings

warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

exchange = ccxt.bitpanda({
    "apiKey": config.BITPANDA_API_KEY
})

MIN_WIN = 0.02
TRADE_INVESTMENT_ETH = 0.02
# hallo, ich bin omar

# Nummer 068120214591
def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr


def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr


def supertrend(df, period=14, atr_multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = atr(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]

    return df


IN_POSITION = False


def check_buy_sell_signals(df):
    global IN_POSITION
    print("checking for buy and sell signals")
    print(df.tail(5))

    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    ethereum_ticker = exchange.fetch_ticker('ETH/EUR')
    mid_price_euro = (float(ethereum_ticker['ask']) + float(ethereum_ticker['bid'])) / 2

    print(f"in position: {IN_POSITION}")

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print("changed to uptrend, buy")
        if not IN_POSITION:
            order = exchange.create_market_buy_order('ETH/EUR', TRADE_INVESTMENT_ETH)
            # winsound.Beep(freq, duration)
            print(order)
            IN_POSITION = True
            target_price_eur = mid_price_euro * (1 + MIN_WIN)
            print(f"In Trade!")
            print(f"Target price: {target_price_eur}")
        else:
            print("already in position, nothing to do")

    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        if IN_POSITION:
            if df['close'][last_row_index] >= target_price_eur:
                print("changed to downtrend, sell")
                order = exchange.create_market_sell_order('ETH/EUR', TRADE_INVESTMENT_ETH)
                # winsound.Beep(freq, duration)
                print(order)
                IN_POSITION = False
        else:
            print("You aren't in position, nothing to sell")
    last_trade = exchange.fetch_my_trades(symbol='ETH/EUR')[-1]
    print(f"last trade: {last_trade}")


def run_bot():
    print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv('ETH/EUR', timeframe='1m', limit=500)
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(bars[:-1], columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    supertrend_data = supertrend(df)

    check_buy_sell_signals(supertrend_data)


schedule.every(2).seconds.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)
