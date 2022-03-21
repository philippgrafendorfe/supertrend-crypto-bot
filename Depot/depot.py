import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class Depot:
    size: float
    currency: str = "EUR"


def main():
    pass


if __name__ == "__main__":
    main()
