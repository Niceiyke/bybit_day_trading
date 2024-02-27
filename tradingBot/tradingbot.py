import os
from pybit.unified_trading import HTTP
import pandas as pd
from macd_strategy import get_strategy
from helper import set_mode, get_pnl, get_positions, get_precisions
from time import sleep


class TradingBot:
    client = HTTP(
        api_key=os.environ.get("API_KEY"), api_secret=os.environ.get("API_SECRET")
    )
    LEVERAGE = 15
    TIMEFRAME = 1
    CANDLESIZE = 750
    AMOUNT = 20
    TAKE_PROFIT_MULTIPLIER = 3
    STOP_LOSS_MULTIPLIER = 2
    MARKET_SLEEP_TIME = 2
    MIN_SYMBOL_TURNOVER = 50000000
    MIN_SYMBOL_24H_PCNT=0

    def get_symbols(self):
        try:
            resp = self.client.get_tickers(category="linear")["result"]["list"]
            symbols = [
                elem["symbol"]
                for elem in resp
                if "USDT" in elem["symbol"]
                and "USDC" not in elem["symbol"]
                and float(elem["turnover24h"]) > self.MIN_SYMBOL_TURNOVER
                and float(elem['price24hPcnt'])>self.MIN_SYMBOL_24H_PCNT
            ]
            print(f"You have total of {len(symbols)} crypto to trade")
            return symbols
        except Exception as err:
            print("Error fetching symbols:", err)

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
            df = df.iloc[::-1]
            return df
        except Exception as err:
            print(f"Error fetching klines for {symbol}:", err)

    def place_order_market(self, symbol, side):
        try:
            price_precision, quantity_precision = get_precisions(symbol)
            sleep(self.MARKET_SLEEP_TIME)

            mark_price = float(
                self.client.get_tickers(category="linear", symbol=symbol)["result"][
                    "list"
                ][0]["markPrice"]
            )

            print(f"Placing {side} order for {symbol}. Mark price: {mark_price}")

            amount = self.AMOUNT * self.LEVERAGE
            order_quantity = round(amount / mark_price, quantity_precision)

            sleep(self.MARKET_SLEEP_TIME)

            tp_multiplier = (
                self.TAKE_PROFIT_MULTIPLIER
                if side == "buy"
                else -self.TAKE_PROFIT_MULTIPLIER
            )
            sl_multiplier = (
                -self.STOP_LOSS_MULTIPLIER
                if side == "buy"
                else self.STOP_LOSS_MULTIPLIER
            )

            tp_price = round(mark_price * tp_multiplier, price_precision)
            sl_price = round(mark_price * sl_multiplier, price_precision)

            resp = self.client.place_order(
                category="linear",
                symbol=symbol,
                side=side.capitalize(),  # Ensure capitalization
                orderType="Market",
                qty=order_quantity,
                takeProfit=tp_price,
                stopLoss=sl_price,
                tpTriggerBy="MarkPrice",
                slTriggerBy="MarkPrice",
            )
            print(resp)
        except Exception as err:
            print(f"Error placing {side} order for {symbol}:", err)

    def get_signal(self):
        try:
            symbols = self.get_symbols()
            if not symbols:
                print("No symbols available for trading.")
                return
            print(symbols)

            for symbol in symbols:
                df = self.get_klines(symbol=symbol)
                if df is None:
                    print(f"No dataframe available for {symbol}.")
                    continue

                strategy = get_strategy(df=df)
                if strategy == "none":
                    print(f"No strategy found for {symbol}.")
                    continue
                elif strategy == "buy":
                    self.place_dummy_order(side="buy",symbol=symbol)
                else:
                    self.place_dummy_order(side="sell",symbol=symbol)
        except Exception as err:
            print("Error in signal processing:", err)

    def place_dummy_order(self, side,symbol):
        if side == "buy":
            print(f"long order placed {symbol}")

        else:
            print(f"short order placed {symbol}")


if __name__ == "__main__":
    obj = TradingBot()
    while True:

        obj.get_signal()
