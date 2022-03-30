import logging
import warnings
from dataclasses import dataclass
from typing import List, Union

import pandas as pd

log = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


@dataclass
class SuperTrendTradingStrategy:
    """This is a variant of supertrend where a buy signal is ussed if there is at least one
    positive position in the balance sheet and sold if a specific return was reached."""

    timeframe: str
    limit: int
    atr_period: int
    atr_multiplier: float
    relative_gain: float

    def check_buy_sell_signals(self
                               , df: pd.DataFrame
                               , position: bool
                               , last_base_price: float) -> str:

        log.info("checking for buy and sell signals")

        log.info(f"in position: {position}")

        if not position:
            should_buy = self.should_buy(prices=df)
            if should_buy:
                return "BUY"

        else:
            target_depot_price = last_base_price * (1 + self.relative_gain)
            should_sell = self.should_sell(prices=df, target_depot_price=target_depot_price)
            if should_sell:
                return "SELL"

        return "WAIT"

    @staticmethod
    def should_buy(prices: Union[pd.DataFrame, List[float]]) -> bool:

        return True
        last_row_index = len(prices.index) - 1
        previous_row_index = last_row_index - 1
        in_uptrend = not prices['in_uptrend'][previous_row_index] and prices['in_uptrend'][last_row_index]
        if in_uptrend:
            log.info("changed to uptrend, buy signal!")
            return True
        else:
            return False

    @staticmethod
    def should_sell(prices: Union[pd.DataFrame, List[float]], target_depot_price: float) -> bool:

        return True
        last_row_index = len(prices.index) - 1
        previous_row_index = last_row_index - 1
        in_downtrend = prices['in_uptrend'][previous_row_index] and not prices['in_uptrend'][last_row_index]
        if in_downtrend and prices['close'][last_row_index] >= target_depot_price:
            return True
        else:
            return False

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

    @staticmethod
    def tr(data):
        data['previous_close'] = data['close'].shift(1)
        data['high-low'] = abs(data['high'] - data['low'])
        data['high-pc'] = abs(data['high'] - data['previous_close'])
        data['low-pc'] = abs(data['low'] - data['previous_close'])

        tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

        return tr
