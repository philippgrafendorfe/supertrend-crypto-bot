import logging
import time
import telegram_send
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from ccxt import bitpanda

from modules.Depot import Depot
from modules.Order import Order
from modules.Strategy.SuperTrend import SuperTrendTradingStrategy
from modules.Ticker import Ticker
from modules.utils import catch_exceptions

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

    @catch_exceptions(cancel_on_failure=False)  # the scheduler will cancel the job if the function fails
    def run(self) -> None:

        df = self.fetch_bars(self.symbol)

        supertrend_data = self.trading_strategy.supertrend(data=df)
        log.debug(f"\n {supertrend_data.iloc[-2:].to_string()}")
        result = self.trading_strategy.check_buy_sell_signals(supertrend_data,
                                                              position=self.in_position,
                                                              last_base_price=self.last_base_price)

        self.process_result(result=result)

    def fetch_bars(self, symbol: str):
        log.debug(f"Fetching new bars for {datetime.now().isoformat()}")
        bars = self.exchange.fetch_ohlcv(symbol,
                                         timeframe=self.trading_strategy.timeframe,
                                         limit=self.trading_strategy.limit
                                         )
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(bars[:-1], columns=columns)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def process_result(self, result: str, test=False) -> None:
        ticker = Ticker.from_dict(
            self.exchange.fetch_ticker(
                symbol=self.symbol
            )
        )
        price = ticker.close
        log.info(f"Actual closing market closing price: {price} EUR.")

        base_value = self.depot.current_value / price

        if test:
            return None

        if result in ("SELL", "BUY"):
            closed_order = self.process_order(side=result, amount=base_value, price=price)

            if result == "BUY":
                self.depot.current_value = closed_order.net_value
                self.last_base_price = closed_order.price
                log_message = f"""
                BUY order filled at price {price} EUR.
                Cost: {closed_order.fee.cost} {closed_order.fee.currency}.
                Depot value: {self.depot.current_value} EUR.
                Target Sell Price: {closed_order.price * (1 + self.trading_strategy.relative_gain)} EUR."""
            else:
                self.depot.current_value = closed_order.net_value
                log_message = f"""
                SELL order filled at price {price} EUR.
                Cost: {closed_order.fee.cost} {closed_order.fee.currency} = {closed_order.fee.cost * closed_order.price} EUR.
                Depot value: {self.depot.current_value} EUR."""

            log.warning(log_message)
            telegram_send.send(messages=[log_message])

            self.in_position = result == "BUY"

    def process_order(self, side: str, amount: float, price: float) -> Order:

        order = self.exchange.create_order(
                symbol=self.symbol,
                type="limit",
                side=side,
                amount=amount,
                price=price
            )
        time.sleep(30)
        while self.exchange.fetch_order_status(id=order.get("id", None)) != "closed":
            log.warning(f"Order with id {order.get('id', None)} not yet closed.")
            time.sleep(30)

        closed_or_cancelled_orders = self.exchange.fetch_closed_orders(symbol=self.symbol)
        closed_orders = [_ for _ in closed_or_cancelled_orders if _["status"] == "closed"]
        last_closed_order = Order.from_dict(closed_orders[-1])

        last_id = last_closed_order.id
        assert last_id == order.get("id", None)

        return last_closed_order
