import logging
import time
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from ccxt import bitpanda

from Depot.depot import Depot
from Strategy.SuperTrend import SuperTrendTradingStrategy

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@dataclass
class SuperTrendAgent:
    exchange: bitpanda
    trading_strategy: SuperTrendTradingStrategy
    depot: Depot
    symbol: str
    taker_fee: float
    last_base_price: float = 0.0
    in_position: bool = False

    def run(self) -> None:
        log.info(f"Fetching new bars for {datetime.now().isoformat()}")
        df = self.fetch_bars(self.symbol)

        supertrend_data = self.trading_strategy.supertrend(data=df)
        log.info(f"\n {supertrend_data.iloc[-2:].to_string()}")

        result = self.trading_strategy.check_buy_sell_signals(supertrend_data,
                                                              position=self.in_position,
                                                              last_base_price=self.last_base_price)

        self.process_result(result=result)

    def fetch_bars(self, symbol):
        bars = self.exchange.fetch_ohlcv(symbol,
                                         timeframe=self.trading_strategy.timeframe,
                                         limit=self.trading_strategy.limit
                                         )
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(bars[:-1], columns=columns)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def process_result(self, result):

        if result not in ("BUY", "SELL"):
            log.info(f"Nothing to do.")

        else:
            log.warning(f"{result} {self.symbol}!!!!!!")
            market_data = self.exchange.fetch_ticker(symbol=self.symbol)
            price = market_data["close"]
            amount = self.depot.current_value / price

            order = self.exchange.create_market_order(symbol=self.symbol
                                                      , side=result
                                                      , amount=amount
                                                      , price=price
                                                      )
            time.sleep(30)
            while self.exchange.fetch_order_status(id=order["id"]) != "closed":
                log.info(f"Order with id {order['id']} not yet closed.")
                time.sleep(30)
            log.warning(f"{result} {order['amount']} of {self.symbol} for {price}: \n {order}")
            amount = price * order['amount']
            net_amount = (1 - self.taker_fee) * amount
            log.info(f"Last trade fee: {amount - net_amount} €.")
            self.depot.current_value = net_amount
            self.last_base_price = price
            self.in_position = result == "BUY"
