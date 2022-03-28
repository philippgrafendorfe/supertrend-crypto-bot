import logging
import time
import telegram_send
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from ccxt import bitpanda

from Depot.depot import Depot
from Strategy.SuperTrend import SuperTrendTradingStrategy

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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
        last_closing_price = supertrend_data.close.tolist()[-1]
        log.info(f"Actual market closing price: {last_closing_price} EUR.")
        result = self.trading_strategy.check_buy_sell_signals(supertrend_data,
                                                              position=self.in_position,
                                                              last_base_price=self.last_base_price)
        telegram_send.send(messages=[f"{result} transaction occured!"])
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
            telegram_send.send(messages=[f"{result} transaction occured!"])
            amount = price * order['amount']
            net_amount = (1 - self.taker_fee) * amount
            log.warning(f"Last trade fee: {amount - net_amount} €.")
            self.depot.current_value = net_amount
            log.warning(f"Current Value of the depot: {self.depot.current_value} EUR.")
            self.last_base_price = price
            log.warning(f"Bought for {price} EUR; target price: {price * (1 + self.trading_strategy.relative_gain)}")
            self.in_position = result == "BUY"
