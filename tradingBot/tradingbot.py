import os
from pybit.unified_trading import HTTP
import pandas as pd
from macd_strategy import get_strategy
from helper import set_mode, get_pnl, get_positions, get_precisions, get_tp_spl
from strategy import three_moving_average_rsi_strategy, trend_strategy
from time import sleep


class TradingBot:
    client = HTTP(
        testnet=True,
        api_key="vHnoV1kQTgYsmhaY2s",
        api_secret="C5lVp013avzhEZgojyYxiT4TzwnZOX70gu8n",
    )
    LEVERAGE = 15
    MODE = 1  # 1 - Isolated, 0 - Cross
    TIMEFRAME = 15
    CANDLESIZE = 100
    AMOUNT = 100
    EXPECTED_PROFIT = 20
    TAKE_PROFIT_MULTIPLIER = 3
    STOP_LOSS_MULTIPLIER = 2
    MARKET_SLEEP_TIME = 2
    MIN_SYMBOL_TURNOVER = 5000000
    MIN_SYMBOL_24H_PCNT = 0
    MAX_OPEN_POSITION = 10

    def get_symbols(self):
        try:
            resp = self.client.get_tickers(category="linear")["result"]["list"]
            symbols = [
                elem["symbol"]
                for elem in resp
                if "USDT" in elem["symbol"]
                and "USDC" not in elem["symbol"]
                and float(elem["turnover24h"]) > self.MIN_SYMBOL_TURNOVER
                and float(elem["price24hPcnt"]) > self.MIN_SYMBOL_24H_PCNT
            ]
            print(f"You have total of {len(symbols)} crypto to trade")
            return symbols
        except Exception as err:
            print("Error fetching symbols:", err)

    def get_klines(self, symbol, timeframe):
        try:
            resp = self.client.get_kline(
                category="linear",
                symbol=symbol,
                interval=timeframe,
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

    def place_order_market(
        self,
        symbol,
        side,
    ):
        try:
            open_position = get_positions(client=self.client)

            if len(open_position) == 5:
                return

            if symbol in open_position:
                return

            print("open position are", open_position)
            price_precision, quantity_precision = get_precisions(
                client=self.client, symbol=symbol
            )
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

            tp, sl = get_tp_spl(
                expected_profit=self.EXPECTED_PROFIT,
                amount=amount,
                price=mark_price,
                side=side,
                precision=price_precision,
            )

            resp = self.client.place_order(
                category="linear",
                symbol=symbol,
                side=side.capitalize(),  # Ensure capitalization
                orderType="Market",
                qty=order_quantity,
                takeProfit=tp,
                stopLoss=sl,
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
                df_5min = self.get_klines(symbol=symbol, timeframe=15)
                if df_5min is None:
                    print(f"No dataframe available for {symbol}.")
                    continue

                    # df_15min = self.get_klines(symbol=symbol, timeframe=30)
                    # if df_5min is None:
                    print(f"No dataframe available for {symbol}.")
                    continue

                strategy = get_strategy(df=df_5min)
                # strategy = three_moving_average_rsi_strategy(df=df_15min)
                # strategy =trend_strategy(df5=df_5min,df15=df_15min)

                if strategy == "hold":
                    print(f"No strategy found for {symbol}.")
                    continue
                if strategy == "buy":
                    sleep(1)
                    set_mode(
                        client=self.client,
                        symbol=symbol,
                        leverage=str(self.LEVERAGE),
                        mode=self.MODE,
                    )
                    sleep(1)

                    self.place_order_market(side="buy", symbol=symbol)
                if strategy == "sell":
                    set_mode(
                        client=self.client,
                        symbol=symbol,
                        leverage=str(self.LEVERAGE),
                        mode=self.MODE,
                    )
                    self.place_order_market(side="sell", symbol=symbol)
        except Exception as err:
            print("Error in signal processing:", err)

    def place_dummy_order(self, side, symbol):
        if side == "buy":
            print(f"long order placed {symbol}")

        else:
            print(f"short order placed {symbol}")


if __name__ == "__main__":
    obj = TradingBot()
    while True:

        obj.get_signal()
        sleep(60)
