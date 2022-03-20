
import hydra

from hydra.core.config_store import ConfigStore

from config.config import MinMaxTradingStrategyConfig
from exchange import Exchange
from strategy import MinMaxTradingStrategy
from trading_bot import TradingBot

cs = ConfigStore.instance()
cs.store(name="config_1", node=MinMaxTradingStrategyConfig)

# todo connect to bitpanda exchange and fetch data
# todo build an arbitrage trading bot


@hydra.main(config_path="config", config_name="config")
def main(cfg: MinMaxTradingStrategyConfig):
    exchange = Exchange()
    exchange.connect()

    trading_strategy = MinMaxTradingStrategy(min_bound=cfg.min_bound, max_bound=cfg.max_bound)

    bot = TradingBot(exchange=exchange, trading_strategy=trading_strategy)
    bot.run("BTC/USD")
    pass


if __name__ == "__main__":
    main()
