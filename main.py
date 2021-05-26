import schedule
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame

import config
# from supertrend import run_bot


# def start_bot():
#     schedule.every(2).seconds.do(run_bot)

def trade_stock():
    api = tradeapi.REST(key_id=config.ALPCACA_API_KEY
                        , secret_key=config.ALPACA_SECRET_KEY
                        , base_url=config.ALPACA_BASE_URL)
    result = api.get_bars("AAPL", TimeFrame.Hour, "2021-02-08", "2021-02-08", limit=100, adjustment='raw').df
    # api.submit_order(symbol='AAPL', qty=8, side="buy")
    return result

print(trade_stock())