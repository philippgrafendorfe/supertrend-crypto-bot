import unittest
from abc import ABC, abstractmethod
from hydra import initialize, compose

from Exchange.exchange import Bitpanda


# cs = ConfigStore.instance()
# cs.store(name="test_exchange_config", node=TestExchangeConfig)


class TestExchangeBase(ABC):

    @abstractmethod
    def test_connect(self):
        pass

    @abstractmethod
    def test_buy(self):
        pass

    @abstractmethod
    def test_sell(self):
        pass

    @abstractmethod
    def test_get_market_data(self):
        pass


class TestCoinbaseExchange(unittest.TestCase, TestExchangeBase):

    def __init__(self, *args, **kwargs):
        super(TestCoinbaseExchange, self).__init__(*args, **kwargs)

    def test_connect(self):
        self.assertFalse()

    def test_buy(self):
        self.assertFalse()

    def test_sell(self):
        self.assertFalse()

    def test_get_market_data(self):
        self.assertFalse()


class TestBitpandaExchange(unittest.TestCase, TestExchangeBase):

    def __init__(self, *args, **kwargs):
        super(TestBitpandaExchange, self).__init__(*args, **kwargs)
        with initialize(config_path="../config"):
            # config is relative to a module
            self.cfg = compose(config_name="config")
        self.exchange = Bitpanda()
        self.symbol = "BTC/EUR"

    def test_connect(self):
        success = self.exchange.connect(credentials=self.cfg["credentials"]["bitpanda_api_key"])
        self.assertEqual(first=True, second=success)

    def test_get_market_data(self):
        self.exchange.connect(credentials=self.cfg["credentials"]["bitpanda_api_key"])
        data = self.exchange.get_market_data(symbol=self.symbol)

        self.assertEqual(data["symbol"], self.symbol)

    def test_get_trades(self):
        self.exchange.connect(credentials=self.cfg["credentials"]["bitpanda_api_key"])
        # last 30 days
        # since = self.exchange.milliseconds() - 2592000000
        trades = self.exchange.get_trades(symbol=self.symbol)

        self.assertEqual()

    def test_buy(self):
        self.assertFalse()

    def test_sell(self):
        self.assertFalse()
