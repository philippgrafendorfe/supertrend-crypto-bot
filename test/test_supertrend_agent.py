import unittest
import pandas as pd
import ccxt
from hydra import initialize, compose

from modules.SupertrendAgent import SuperTrendAgent
from modules.Depot import Depot
from modules.Strategy.SuperTrend import SuperTrendTradingStrategy
from pathlib import Path


class TestSupertrendAgent(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSupertrendAgent, self).__init__(*args, **kwargs)

        with initialize(config_path="../config"):
            cfg = compose(config_name="supertrend_test", overrides=[])
        exchange = ccxt.bitpanda({"apiKey": cfg.exchange.api_key})
        self.strategy = SuperTrendTradingStrategy(**cfg.strategy)
        depot = Depot(start_value=cfg.position_bet_EUR, current_value=cfg.position_bet_EUR)
        self.bot = SuperTrendAgent(exchange=exchange,
                                   trading_strategy=self.strategy,
                                   depot=depot,
                                   symbol=cfg.symbol,
                                   taker_fee=0.0015)

    def test_buy_process_result(self):
        result = "BUY"
        self.bot.process_result(result=result, test=True)
        self.assertEqual(True, self.bot.in_position)  # add assertion here

    def test_sell_process_result(self):
        result = "SELL"
        self.bot.process_result(result=result, test=True)
        self.assertEqual(False, self.bot.in_position)  # add assertion here

    def test_supertrend_data(self):
        path_to_bars = Path(r"data\bars.tsv")
        bars = pd.read_csv(path_to_bars, sep="\t", index_col=None)
        supertrend_data = self.strategy.supertrend(data=bars)
        self.assertEqual(supertrend_data.in_uptrend[40], True)


if __name__ == '__main__':
    unittest.main()
