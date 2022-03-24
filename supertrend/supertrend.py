import logging
import time

import ccxt
import hydra
from omegaconf import DictConfig

import pandas as pd
import schedule
from Depot.depot import Depot
from Strategy.SuperTrend import SuperTrendTradingStrategy
from Bot.trading_bot import SuperTrendBot

log = logging.getLogger(__name__)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)


@hydra.main(config_path="../config", config_name="config")
def main(cfg: DictConfig):
    exchange = ccxt.bitpanda({"apiKey": cfg.bitpanda_api_key})
    strategy = SuperTrendTradingStrategy(timeframe=cfg.timeframe,
                                         limit=cfg.limit,
                                         atr_period=cfg.atr_period,
                                         atr_multiplier=cfg.atr_multiplier,
                                         relative_gain=cfg.relative_gain)
    log.info(f"Initiating trading bot with trading strategy:")
    log.info(strategy)
    depot = Depot(start_value=cfg.position_bet_EUR, current_value=cfg.position_bet_EUR)
    log.info(f"Depot size: {depot.start_value}, depot currency: {depot.currency}.")
    bot = SuperTrendBot(exchange=exchange,
                        trading_strategy=strategy,
                        depot=depot,
                        symbol=cfg.symbol,
                        taker_fee=0.0015)

    log.info(f"Schedule with symbol {cfg.symbol}. Run period: {cfg.bot_run_period}. Timeframe: minutes.")
    bot.run()
    schedule.every(cfg.bot_run_period).minutes.do(bot.run)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()

# todo make bot running in production
# todo ich will mein Depot verfolgen können. Dafür könnte man den Bot in der Depot schreiben lassen.
# ein Depot kann sich entwickeln. dazu speichern wir immer den startwert und den aktuellen Wert.
# todo als Anleger möchte ich meine Ausgaben überblicken können. Es muss dazu eine komulierte Variable geben für die Ausgaben.
# todo get better and more informative bars by changing the smapling method
# todo check vectorBT for an easier implementation
# todo man kann den gesamten verlauf in einem dataframe mittracken und diesen vielleicht abspeichern.
# todo die config objektorientierter machen
# todo als Trader möchte ich das depot mit der exchange balance verbinden um sich eine manuelle Überprüfung der Deckung zu sparen.
# todo highlight logging with colors
