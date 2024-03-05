import pandas as pd
from pybit.unified_trading import HTTP
from time import sleep
from helper import get_positions, get_precisions, get_tp_spl,set_mode
from strategy import get_strategy


class TradingBot:
    def __init__(self):
        self.client = HTTP(
            testnet=True,
            api_key="vHnoV1kQTgYsmhaY2s",
            api_secret="C5lVp013avzhEZgojyYxiT4TzwnZOX70gu8n",
        )
        self.LEVERAGE = 15
        self.MODE = 1  # 1 - Isolated, 0 - Cross
        self.TIMEFRAME = 15
        self.CANDLESIZE = 100
        self.AMOUNT = 100
        self.EXPECTED_PROFIT = 20
        self.TAKE_PROFIT_MULTIPLIER = 3
        self.STOP_LOSS_MULTIPLIER = 2
        self.MARKET_SLEEP_TIME = 2
        self.MIN_SYMBOL_TURNOVER = 5000000
        self.MIN_SYMBOL_24H_PCNT = 0
        self.MAX_OPEN_POSITION = 10

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
            print(f"You have a total of {len(symbols)} crypto to trade")
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

    def place_order_market(self, symbol, side):
        try:
            open_positions = get_positions(client=self.client)
            if len(open_positions) >= self.MAX_OPEN_POSITION:
                return

            if symbol in open_positions:
                return

            print("Open positions are", open_positions)
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

                strategy = get_strategy(df=df_5min)
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


if __name__ == "__main__":
    obj = TradingBot()
    while True:
        obj.get_signal()
        sleep(60)
