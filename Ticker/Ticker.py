from dataclasses import dataclass


@dataclass
class Ticker:
    average: float
    high: float
    low: float
    symbol: str
