import logging
from dataclasses import dataclass


@dataclass
class Depot:
    start_value: float # in EUR
    current_value: float # in EUR
    currency: str = "EUR"
