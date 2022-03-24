import time
from datetime import datetime
import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass

import pandas as pd
from ccxt import bitpanda

from Depot.depot import Depot
from Strategy.SuperTrend import SuperTrendTradingStrategy
from Exchange.exchange import Exchange

log = logging.getLogger(__name__)


@dataclass
class TradingBot(ABC):
    """Trading bot that connects to a crypto exchange and performs a trade."""

    @abstractmethod
    def run(self, symbol: str) -> None:
        """Run the trading bot once for a particula symbol with a given strategy."""


@dataclass
class SuperTrendBot(TradingBot):
    exchange: bitpanda
    trading_strategy: SuperTrendTradingStrategy
    depot: Depot
    symbol: str
    position_amount: float = 0.0
    in_position: bool = False
    last_acquisition_price: float = 0.0
    last_base_amount: float = 0.0

    def run(self) -> None:
        log.info(f"Fetching new bars for {datetime.now().isoformat()}")
        df = self.fetch_bars(self.symbol)

        supertrend_data = self.trading_strategy.supertrend(data=df)
        log.info(f"\n {supertrend_data.iloc[-2:].to_string()}")

        result = self.trading_strategy.check_buy_sell_signals(supertrend_data,
                                                              position=self.in_position,
                                                              actual_depot_price=self.last_acquisition_price)

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
        if result == "BUY":
            log.info(f"{result} {self.symbol}!!!!!!")
            market_data = self.exchange.fetchTicker(symbol=self.symbol)
            price = market_data["close"]
            base_amount = self.depot.actual / price

            order = self.exchange.create_market_order(symbol=self.symbol
                                                      , side=result
                                                      , amount=base_amount
                                                      , price=price
                                                      )
            time.sleep(secs=30)
            while self.exchange.fetch_order_status(id=order["id"]) != "closed":
                log.info(f"Order with id {order['id']} not yet closed.")
                time.sleep(secs=30)
            log.info(f"Bought {self.position_amount} {self.symbol} for {price}: \n {order}")
            self.last_base_amount = order["amount"]
            self.last_acquisition_price = price

            self.in_position = True
        elif result == "SELL":
            log.info(f"{result} {self.symbol}!!!!!!")
            market_data = self.exchange.fetchTicker(symbol=self.symbol)
            price = market_data["close"]
            base_amount = self.depot.actual / price
            order = self.exchange.create_market_order(symbol=self.symbol
                                                      , side=result
                                                      , amount=base_amount
                                                      , price=price
                                                      )

            self.position_amount = 0.0
            log.info(f"Order {order} transaction filled.")
            self.depot.last_value = order["amount"]*order["price"]
            self.in_position = False
        else:
            log.info(f"Nothing to do.")
            # market_data = self.exchange.fetchTicker(symbol=self.symbol)
            # log.info(f"Market data: \n {market_data}")
