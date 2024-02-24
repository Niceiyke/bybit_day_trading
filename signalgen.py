from keys import api, secret
from pybit.unified_trading import HTTP
import pandas as pd
import ta
from time import sleep


session = HTTP(api_key=api, api_secret=secret)
timeframe = 1  # 15 minutes


# Getting all available symbols from Derivatives market (like 'BTCUSDT', 'XRPUSDT', etc)
def get_tickers():
    try:
        resp = session.get_tickers(category="linear")["result"]["list"]
        symbols = []
        for elem in resp:
            if "USDT" in elem["symbol"] and not "USDC" in elem["symbol"]:
                if float(elem["turnover24h"]) > 20000000:
                    symbols.append(elem["symbol"])

        print(f"you have total of {len(symbols)} crypto to trade")
        return symbols
    except Exception as err:
        print(err)


# Klines is the candles of some symbol (up to 1500 candles). Dataframe, last elem has [-1] index
def klines(symbol):
    try:
        resp = session.get_kline(
            category="linear", symbol=symbol, interval=timeframe, limit=750
        )["result"]["list"]
        resp = pd.DataFrame(resp)
        resp.columns = ["Time", "Open", "High", "Low", "Close", "Volume", "Turnover"]
        resp = resp.set_index("Time")
        resp = resp.astype(float)
        resp = resp[::-1]
        return resp
    except Exception as err:
        print(err)


def calculate_macd(df):
    close_df = df["Close"]
    ma9 = close_df.ewm(span=12, adjust=False).mean()
    ma26 = close_df.ewm(span=26, adjust=False).mean()
    ema200 = close_df.ewm(span=200, adjust=False).mean()
    macd = ma9 - ma26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1], ema200.iloc[-1], close_df.iloc[-1]


def get_strategy(df):
    strategy = "none"
    macd, signal, moving_average, price = calculate_macd(df)

    # Check bullish signal long
    if macd > signal and macd < 0 and signal < 0 and price < moving_average:
        strategy = "buy"
        return strategy

    # Check bearish signal short
    if macd < signal and macd > 0 and signal > 0 and moving_average < price:
        strategy = "sell"
        return strategy

    # Default case
    return strategy


def macd_signal(symbol):
    data = klines(symbol)
    return get_strategy(df=data)


symbols = get_tickers()


try:
    while True:
        active_signals = []

        for symbol in symbols:
            signal = macd_signal(symbol)
            active_signals.append((symbol, signal))

        print(active_signals)

        print("*" * 20)
        print("*" * 20)

        sleep(30)

except KeyboardInterrupt:
    print("Someone closed the program")
