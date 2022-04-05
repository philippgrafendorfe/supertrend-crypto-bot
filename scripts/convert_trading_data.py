import logging
import os

import ccxt
import hydra
import numpy as np
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


def get_time_bars(trading_df: pd.DataFrame) -> pd.DataFrame:
    time_bars = trading_df.groupby(pd.Grouper(freq="5min")).agg({"price": "ohlc", "amount": "sum"})
    file_name = "time_bars.tsv"
    return write_bars(bars=time_bars, file_name=file_name)


def bar(x, y):
    return np.int64(x / y) * y


def write_bars(bars: pd.DataFrame, file_name: str):
    bars_price = bars.loc[:, "price"].dropna()
    bars_price.to_csv(file_name, sep="\t")
    log.info(f"Written tick bars to file: {os.getcwd()}/{file_name}")
    return bars_price


def get_tick_bars(trading_df: pd.DataFrame, transactions: int):
    tick_bars = trading_df.groupby(bar(np.arange(len(trading_df)), transactions)).agg(
        {"price": "ohlc", "amount": "sum"})
    file_name = "tick_bars.tsv"
    return write_bars(bars=tick_bars, file_name=file_name)


def get_volumen_bars(trading_df: pd.DataFrame, traded_volume: float) -> pd.DataFrame:
    volume_bars = trading_df.groupby(bar(np.cumsum(trading_df["amount"]), traded_volume)).agg(
        {"price": "ohlc", "amount": "sum"})
    file_name = "volume_bars.tsv"
    return write_bars(bars=volume_bars, file_name=file_name)


def get_dollar_bars(trading_df: pd.DataFrame, market_value: float) -> pd.DataFrame:
    dollar_bars = trading_df.groupby(bar(np.cumsum(trading_df["cost"]), market_value)).agg(
        {"price": "ohlc", "amount": "sum"})
    file_name = "dollar_bars.tsv"
    return write_bars(bars=dollar_bars, file_name=file_name)


@hydra.main(config_path="../config/exchange", config_name="bitpanda")
def main(cfg: DictConfig) -> None:
    exchange = ccxt.bitpanda({"apiKey": cfg.api_key})
    trading_data = exchange.fetch_trades("BTC/EUR", limit=1000)
    trading_df = prepare_trading_data(trading_data=trading_data)

    time_bars = get_time_bars(trading_df=trading_df)
    tick_bars = get_tick_bars(trading_df=trading_df, transactions=20)
    volume_bars = get_volumen_bars(trading_df=trading_df, traded_volume=2000)
    dollar_bars = get_dollar_bars(trading_df=trading_df, market_value=100000)


if __name__ == "__main__":
    main()
