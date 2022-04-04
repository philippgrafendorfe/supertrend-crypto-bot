import logging
import ccxt
import hydra
import pandas as pd
from omegaconf import DictConfig
import datetime as dt
import matplotlib.pyplot as plt

log = logging.getLogger(__name__)


def prepare_trading_data(trading_data: list) -> pd.DataFrame:
    trading_df = pd.DataFrame(trading_data)
    trading_df = trading_df[["datetime", "price", "amount", "side", "cost"]]
    trading_df["datetime"] = pd.to_datetime(trading_df["datetime"])
    trading_df.set_index("datetime", inplace=True)
    return trading_df


@hydra.main(config_path="../config/exchange", config_name="bitpanda")
def main(cfg: DictConfig) -> None:
    exchange = ccxt.bitpanda({"apiKey": cfg.api_key})
    trading_data = exchange.fetch_trades("BTC/EUR", limit=1000)
    trading_df = prepare_trading_data(trading_data=trading_data)
    time_bars = trading_df.groupby(pd.Grouper(freq="5min")).agg({"price": "ohlc", "amount": "sum"})
    time_bars_price = time_bars.loc[:, "price"].dropna()
    print(time_bars_price)
    pass


if __name__ == "__main__":
    main()
