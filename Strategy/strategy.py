import logging
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import pandas as pd
from ccxt import Exchange

log = logging.getLogger(__name__)


class TradingStrategy(ABC):

    @abstractmethod
    def should_buy(self, prices: List[float]) -> bool:
        """Whether you should buy this coin given the prices."""

    @abstractmethod
    def should_sell(self, prices: List[float]) -> bool:
        """Whether you should sell this coin given the prices."""


@dataclass
class AverageTradingStrategy(TradingStrategy):
    """Strategy based on price averages."""

    window_size: int

    def should_buy(self, prices: List[float]) -> bool:
        list_window = prices[-self.window_size:]
        return prices[-1] < statistics.mean(list_window)

    def should_sell(self, prices: List[float]) -> bool:
        list_window = prices[-self.window_size:]
        return prices[-1] > statistics.mean(list_window)


@dataclass
class MinMaxTradingStrategy(TradingStrategy):
    min_bound: int
    max_bound: int

    def should_buy(self, prices: List[float]) -> bool:
        return prices[-1] < self.min_bound

    def should_sell(self, prices: List[float]) -> bool:
        return prices[-1] > self.max_bound





@dataclass
class ArbitrageTradingStrategy(TradingStrategy):
    
    def should_sell(self, prices: List[float]) -> bool:
        pass

    def should_buy(self, prices: List[float]) -> bool:
        pass