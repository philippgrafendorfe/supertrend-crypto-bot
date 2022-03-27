import logging
import time

import ccxt
import hydra
import pandas as pd
import schedule
from omegaconf import DictConfig

from Agent.SupertrendAgent import SuperTrendAgent
from Depot.depot import Depot
from Strategy.SuperTrend import SuperTrendTradingStrategy

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)


@hydra.main(config_path="../config", config_name="supertrend")
def main(cfg: DictConfig):
    exchange = ccxt.bitpanda({"apiKey": cfg.exchange.api_key})

    log.info(f"Initiating trading bot with trading strategy:")
    strategy = SuperTrendTradingStrategy(**cfg.strategy)
    log.info(strategy)
    depot = Depot(start_value=cfg.position_bet_EUR, current_value=cfg.position_bet_EUR)
    log.info(f"Depot size: {depot.start_value}, depot currency: {depot.currency}.")
    bot = SuperTrendAgent(exchange=exchange,
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

# todo ich will mein Depot verfolgen können. Dafür könnte man den Agent in der Depot schreiben lassen.
# ein Depot kann sich entwickeln. dazu speichern wir immer den startwert und den aktuellen Wert.
# todo als Anleger möchte ich meine Ausgaben überblicken können. Es muss dazu eine komulierte Variable geben für die Ausgaben.
# todo get better and more informative bars by changing the smapling method
# todo check vectorBT for an easier implementation
# todo man kann den gesamten verlauf in einem dataframe mittracken und diesen vielleicht abspeichern.
# todo als Trader möchte ich das depot mit der exchange balance verbinden um sich eine manuelle Überprüfung der Deckung zu sparen.
# todo run in docker container
