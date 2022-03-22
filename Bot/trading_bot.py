from datetime import datetime
import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass

import pandas as pd

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
    exchange: Exchange
    trading_strategy: SuperTrendTradingStrategy
    depot: Depot
    symbol: str
    in_position: bool = False

    def run(self) -> None:
        log.info(f"Fetching new bars for {datetime.now().isoformat()}")
        df = self.fetch_bars(self.symbol)

        supertrend_data = self.trading_strategy.supertrend(data=df)
        log.info(f"\n {supertrend_data.iloc[-2:].to_string()}")

        result = self.trading_strategy.check_buy_sell_signals(supertrend_data,
                                                              position=self.in_position,
                                                              actual_depot_price=self.depot.actual)

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
        if result == "Buy":
            log.info(f"Buy {self.symbol}!")
            # order = self.exchange.create_market_buy_order(self.symbol, 100)
            market_data = self.exchange.fetchTicke(symbol=self.symbol)
            log.info(f"Market data: {market_data}")
            self.in_position = True
        elif result == "Sell":
            log.info(f"Sell {self.symbol}")
            # order = self.exchange.create_market_sell_order(self.symbol, )
            market_data = self.exchange.fetchTicke(symbol=self.symbol)
            log.info(f"Market data: {market_data}")
            self.in_position = False
        else:
            log.info(f"Nothing to do.")
            market_data = self.exchange.fetchTicker(symbol=self.symbol)
            log.info(f"Market data: {market_data}")
