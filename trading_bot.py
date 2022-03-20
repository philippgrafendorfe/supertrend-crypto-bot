from exchange import Exchange
from strategy import TradingStrategy
from utils import get_logger

logger = get_logger(__name__)


class TradingBot:
    """Trading bot that connects to a crypto exchange and performs a trade."""

    def __init__(self, exchange: Exchange, trading_strategy: TradingStrategy) -> None:
        self.exchange = exchange
        self.trading_strategy = trading_strategy

    def run(self, symbol: str) -> None:
        """Run the trading bot once for a particula symbol with a given strategy."""

        prices = self.exchange.get_market_data(symbol=symbol)
        should_buy = self.trading_strategy.should_buy(prices=prices)
        should_sell = self.trading_strategy.should_sell(prices=prices)

        if should_buy:
            self.exchange.buy(symbol=symbol, amount=10)
        elif should_sell:
            self.exchange.sell(symbol=symbol, amount=10)
        else:
            logger.info(f"No action needed for {symbol}.")
