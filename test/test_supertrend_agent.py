import unittest

import ccxt
from hydra import initialize, compose

from modules.Agent.SupertrendAgent import SuperTrendAgent
from modules.Depot.depot import Depot
from modules.Strategy.SuperTrend import SuperTrendTradingStrategy


class TestSupertrendAgent(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSupertrendAgent, self).__init__(*args, **kwargs)

        with initialize(config_path="../config"):
            cfg = compose(config_name="supertrend_test", overrides=[])
        exchange = ccxt.bitpanda({"apiKey": cfg.exchange.api_key})
        strategy = SuperTrendTradingStrategy(**cfg.strategy)
        depot = Depot(start_value=cfg.position_bet_EUR, current_value=cfg.position_bet_EUR)
        self.bot = SuperTrendAgent(exchange=exchange,
                                   trading_strategy=strategy,
                                   depot=depot,
                                   symbol=cfg.symbol,
                                   taker_fee=0.0015)

    def test_process_result(self):
        result = "BUY"
        self.bot.process_result(result=result, test = True)
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
