from keys import api, secret
from pybit.unified_trading import HTTP
import pandas as pd
from time import sleep

API_KEY = api
API_SECRET = secret
SYMBOL = "VETUSDT"
TIMEFRAME = 1  # 1 minute
CANDLE_LIMIT = 720
QUANTITY = 10  # Amount of USDT for one order
TAKE_PROFIT = 1.3  # Take Profit +1.2%
STOP_LOSS = 0.1  # Stop Loss -0.9%
LEVERAGE = 10

session = HTTP(api_key=API_KEY, api_secret=API_SECRET)


def get_klines():
    try:
        resp = session.get_kline(
            category='linear',
            symbol=SYMBOL,
            interval=TIMEFRAME,
            limit=CANDLE_LIMIT
        )['result']['list']
        df = pd.DataFrame(resp)
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        df = df.set_index('Time').astype(float).iloc[::-1]
        return df
    except Exception as e:
        print(f"Error fetching klines: {e}")
        return None


def calculate_macd(df):
    close_df = df['Close']
    ma9 = close_df.ewm(span=12, adjust=False).mean()
    ma26 = close_df.ewm(span=26, adjust=False).mean()
    ema200 = close_df.ewm(span=200, adjust=False).mean()
    macd = ma9 - ma26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1], ema200.iloc[-1], close_df.iloc[-1]


def buy_strategy():
    print("Buy")


def sell_strategy():
    print("Sell")


def active_trade():
    return 1  # Placeholder for active trade logic


def main():
    df = get_klines()
    if df is None:
        return

    macd, signal, ema200, close_price = calculate_macd(df)
    diff = macd - signal
    active_trade_status = active_trade()

    print('Close Price:', close_price)
    print('EMA200:', ema200)
    print("MACD:", macd)
    print("Signal:", signal)
    print('Difference:', diff)

    action = 0

    if active_trade_status == 0:
        if close_price < ema200:
            print("Buy Condition 1")
            if macd < 0:
                print("Buy Condition 2")
                if 3 < diff < 15:
                    print("Buy Condition 3")
                    action = 1
                    buy_strategy()
        else:
            print("No Buy Condition Met")

    elif active_trade_status == 1:
        if close_price > ema200:
            print("Sell Condition 1")
            if macd > 0:
                print("Sell Condition 2")
                if -15 < diff < 0:
                    print("Sell Condition 3")
                    action = 2
                    sell_strategy()
    else:
        print("No Active Trade")

    # Perform action based on trade conditions
    # execute_trade(action)


while True:
    main()
    sleep(2)
