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




def macd_calculation(df):
    try:
        close_df = df['Close']
        low_df = df['Low']

        low = low_df.iloc[-5:].mean()

        cp = close_df.iloc[-1]

        ma9 = close_df.ewm(span=12, adjust=False).mean()
        ma26 = close_df.ewm(span=26, adjust=False).mean()
        ema200 = close_df.ewm(span=200, adjust=False).mean()

        macd = ma9 - ma26
        signal = macd.ewm(span=9, adjust=False).mean()

        return macd.iloc[-1], signal.iloc[-1], ema200.iloc[-1], cp
    except Exception as e:
        print("Error in MACD calculation:", e)
        return None, None, None, None
    

def buy_strategy():
    print("Buy")


def sell_strategy():
    print("Sell")


def active_trade():
    return 1  # Placeholder for active trade logic

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


def main():
    try:
        df = get_klines()
        if df is not None:
            macd, signal, ema200, cp = macd_calculation(df)

            if macd is not None:
                diff = macd - signal

                active_buy_trade = active_trade()
                action = 0

                print('cp:', cp)
                print('ma200:', ema200)
                print("MACD:", macd)
                print("SIGNAL:", signal)
                print('diff:', diff)

                if active_buy_trade == 0:
                    if cp < ema200:
                        print("buy1")
                        if macd < 0:
                            print("buy2")
                            if 3 < diff < 15:
                                print("buy3")
                                action = 1
                                buy_strategy()
                    else:
                        if action == 0:
                            print("No Market")

                if active_trade == 1:
                    if cp > ema200:
                        print("sell1")
                        if macd > 0:
                            print("sell2")
                            if -15 < diff < 0:
                                print("sell3")
                                action = 2
                                sell_strategy()
                                return
    except Exception as e:
        print("Error in main function:", e)

while True:
    main()
    sleep(2)
