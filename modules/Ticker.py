from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TickerInfo:
    instrument_code: str
    sequence: str
    time: str
    state: str
    is_frozen: str
    quote_volume: str
    base_volume: str
    last_price: str
    best_bid: str
    best_ask: str
    price_change: str
    price_change_percentage: str
    high: str
    low: str


@dataclass_json
@dataclass
class Ticker:
    symbol: str
    timestamp: int
    datetime: str
    high: float
    low: float
    bid: float
    bidVolume: float
    ask: float
    askVolume: float
    vwap: float
    open: float
    close: float
    last: float
    previousClose: float
    change: float
    percentage: float
    average: float
    baseVolume: float
    quoteVolume: float
    info: TickerInfo
