import logging
import time
import telegram_send
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from ccxt import bitpanda

from modules.Depot.depot import Depot
from modules.Order.Order import Order
from modules.Strategy.SuperTrend import SuperTrendTradingStrategy
from modules.utils import catch_exceptions

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

    @catch_exceptions(cancel_on_failure=False)  # the scheduler will cancel the job if the function fails
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

    def process_result(self, result: dict, test=False) -> None:
        market_data = self.exchange.fetch_ticker(symbol=self.symbol)
        price = market_data["close"]
        log.info(f"Actual closing market closing price: {price} EUR.")

        base_value = self.depot.current_value / price

        if result in ("SELL", "BUY"):
            closed_order = self.process_order(side=result, amount=base_value, price=price, test=test)
            fee = closed_order["fee"]
            cost = fee["cost"]
            cost_currency = fee["currency"]

            # price: float = closed_order['price']
            # amount: float = last_closed_order['amount']

            if result == "BUY":
                self.depot.current_value = closed_order.net_value
                self.last_base_price = closed_order.price
                log_message = f"""BUY order filled at price {price} EUR.\n
                                            Cost: {closed_order.fee.cost} {closed_order.fee.currency}. \n
                                            Depot value: {self.depot.current_value} EUR.\n
                                            Target Sell Price: {closed_order.price * (1 + self.trading_strategy.relative_gain)} EUR."""
            else:
                self.depot.current_value = closed_order.net_value
                log_message = f"""SELL order filled at price {price} EUR.\n
                                            Cost: {cost} {cost_currency} = {cost * price} EUR. \n
                                            Depot value: {self.depot.current_value} EUR.\n"""

            log.warning(log_message)
            telegram_send.send(messages=[log_message])

            self.in_position = result == "BUY"

    def process_order(self, side: str, amount: float, price: float, test: bool = False) -> Order:

        if not test:
            order = Order.from_dict(
                self.exchange.create_order(
                    symbol=self.symbol,
                    type="limit",
                    side=side,
                    amount=amount,
                    price=price)
            )
            time.sleep(30)
            while self.exchange.fetch_order_status(id=order.id) != "closed":
                log.warning(f"Order with id {order.id} not yet closed.")
                time.sleep(30)

        last_closed_order = Order.from_dict(self.exchange.fetch_closed_orders(symbol=self.symbol)[-2])
        last_id = last_closed_order.id
        if not test:
            assert last_id == order.id

        return last_closed_order
