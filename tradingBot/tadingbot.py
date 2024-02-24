import os
from pybit.unified_trading import HTTP
import pandas as pd
from macd_strategy import get_strategy
from helper import set_mode, get_pnl, get_positions, get_precisions


class TradingBot:
    client = HTTP(
        api_key=os.environ.get("API_KEY"), api_secret=os.environ.get("API_SECRET")
    )
    LEVERAGE = 10
    TIMEFRAME = 1
    CANDLESIZE = 750

    def get_symbols(self):
        try:
            resp = self.client.get_tickers(category="linear")["result"]["list"]
            symbols = []
            for elem in resp:
                if "USDT" in elem["symbol"] and not "USDC" in elem["symbol"]:
                    if float(elem["turnover24h"]) > 100000000:
                        symbols.append(elem["symbol"])

            print(f"you have total of {len(symbols)} crypto to trade")
            return symbols
        except Exception as err:
            print(err)

    def get_klines(self, symbol):
        try:
            resp = self.client.get_kline(
                category="linear",
                symbol=symbol,
                interval=self.TIMEFRAME,
                limit=self.CANDLESIZE,
            )["result"]["list"]
            df = pd.DataFrame(resp)
            df.columns = ["Time", "Open", "High", "Low", "Close", "Volume", "Turnover"]
            df = df.set_index("Time")
            df = df.astype(float)
            df = df[::-1]
            return df
        except Exception as err:
            print(err)

    def get_signal(self, symbol):
        data = self.get_klines(symbol)
        print("data", data)
        strategy = get_strategy(df=data)
        print("running", strategy)

        return strategy


if __name__ == "__main__":
    obj = TradingBot()
    obj.get_signal("BTCUSDT")
