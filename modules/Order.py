from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Fee:
    currency: str
    cost: float
    rate: float


@dataclass_json
@dataclass
class Order:
    id: str
    symbol: str
    timestamp: int
    datetime: str
    lastTradeTimestamp: int
    symbol: str
    type: str
    timeInForce: str
    postOnly: bool
    side: str
    price: float
    stopPrice: str
    amount: float
    cost: float
    average: float
    filled: float
    remaining: float
    status: str  # todo implement as enum
    fee: Fee

    @property
    def gross_value(self):
        return self.amount * self.price

    @property
    def net_value(self):
        return self.gross_value * (1 - self.fee.rate / 100)
