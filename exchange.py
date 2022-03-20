from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict

import ccxt
from pydantic import BaseModel

from utils import get_logger

logger = get_logger(__name__)


class ExchangeConnectionError(Exception):
    """Custom Error that is raised when an exchange is not connected."""


class Exchange(ABC):
    """Basic Exchange Simulator"""

    def __init__(self) -> None:
        self.connected = False

    @abstractmethod
    def connect(self, credentials: Union[str]) -> None:
        """Connect to the exchange"""
        logger.info("Connecting to Crypto Exchange...")
        self.connected = True

    # @abstractmethod
    def check_connection(self) -> None:
        """Check if the exchange is connected."""
        if not self.connected:
            logger.error("No Exchange connected.")
            raise ExchangeConnectionError()

    # @abstractmethod
    def get_market_data(self, symbol: str) -> List[float]:
        self.check_connection()
        price_data = {
            "BTC/USD": [35842.0,
                        35873.0,
                        35923
                        ]
        }
        return price_data[symbol]

    # @abstractmethod
    def buy(self, symbol: str, amount: float) -> None:
        """Simulate buying an amount of a given symbol at the curren price."""
        self.check_connection()
        logger.info(f"Buying amount {amount} in market {symbol}.")

    # @abstractmethod
    def sell(self, symbol: str, amount: float) -> None:
        """Simulate selling an amount of a given symbol at the curren price."""
        self.check_connection()
        logger.info(f"Selling amount {amount} in market {symbol}.")


class Bitpanda(Exchange):

    def connect(self, credentials: str) -> bool:
        logger.info("Connecting to Bitpanda Crypto Exchange...")
        self.exchange = ccxt.bitpanda({
            "apiKey": credentials
        })
        if self.exchange.id == "bitpanda":

            logger.info("Connected to Bitpanda Crypto Exchange...")
            self.connected = True
            return True
        else:
            logger.info("Connection to Bitpanda Crypto Exchange failed.")
            self.connected = False
            return False

    def get_trades(self, symbol: str) -> List[Dict]:

        # todo write trading data to pandas dataframe and load
        trades = self.exchange.fetch_trades(symbol=symbol)

        return trades

    def get_market_data(self, symbol: str) -> List[float]:

        ticker = self.exchange.fetch_ticker(symbol=symbol)

        return ticker


class Ticker(BaseModel):
    average: Optional[float] = 0.0
    high: float
    low: float
    symbol: str
