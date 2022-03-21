import logging
from dataclasses import dataclass
from typing import List

import pandas as pd
from ccxt import Exchange

from Strategy.strategy import TradingStrategy

log = logging.getLogger(__name__)

import warnings

warnings.filterwarnings('ignore')


@dataclass
class SuperTrendTradingStrategy(TradingStrategy):
    """This is a variant of supertrend where a buy signal is ussed if there is at least one
    positive position in the balance sheet and sold if a specific return was reached."""

    timeframe: str
    limit: int
    atr_period: int
    atr_multiplier: float
    relative_gain: float

    def should_buy(self, prices: List[float]) -> bool:

        pass

    def should_sell(self, prices: List[float]) -> bool:

        pass

    def supertrend(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        hl2 = (df['high'] + df['low']) / 2
        df['atr'] = self.atr(df, self.atr_period)
        df['upperband'] = hl2 + (self.atr_multiplier * df['atr'])
        df['lowerband'] = hl2 - (self.atr_multiplier * df['atr'])
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

    def atr(self, data, period):
        data['tr'] = self.tr(data)
        atr = data['tr'].rolling(period).mean()

        return atr

    def tr(self, data):
        data['previous_close'] = data['close'].shift(1)
        data['high-low'] = abs(data['high'] - data['low'])
        data['high-pc'] = abs(data['high'] - data['previous_close'])
        data['low-pc'] = abs(data['low'] - data['previous_close'])

        tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

        return tr

    def check_buy_sell_signals(self, df: pd.DataFrame, exchange: Exchange, position: bool) -> bool:

        log.info("checking for buy and sell signals")
        # log.info(df.tail(5))

        last_row_index = len(df.index) - 1
        previous_row_index = last_row_index - 1

        # ethereum_ticker = exchange.fetch_ticker('ETH/EUR')
        # mid_price_euro = (float(ethereum_ticker['ask']) + float(ethereum_ticker['bid'])) / 2

        log.info(f"in position: {position}")

        if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
            log.info("changed to uptrend, buy")
            if not position:
                log.info(f"Buy BTC for 100 bugs.")
                # order = exchange.create_market_buy_order("BTC/EUR", 100)
                # log.info(order)
                position = True
                log.info(f"In Trade!")
            else:
                log.info("already in position, nothing to do")

        if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
            if position:
                # if df['close'][last_row_index] >= target_price_eur:
                log.info("changed to downtrend, sell")
                # order = exchange.create_market_sell_order('ETH/EUR', 100)
                # log.info(order)
                position = False
            else:
                log.info("You aren't in position, nothing to sell")

        return position
