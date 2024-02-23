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
PRICE =50
MODE =0

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


def enter_position(order_type):
    session.place_order(
    category="linear",
    symbol=SYMBOL,
    side=order_type,
    orderType="Limit",
    qty=QUANTITY,
    price=PRICE,
    timeInForce="PostOnly",
    orderLinkId="spot-test-postonly",
    isLeverage=LEVERAGE,
    orderFilter="Order",
)

def active_trade():
    return 1

def get_strategy():
    data =get_klines()
    macd,signal,moving_average,price = calculate_macd(data)

    active_position=active_trade()

    #Check bullish signal

    if (macd > signal) & ((macd & signal)<0) &(price<moving_average):

        if active_position == 0:
            enter_position(order_type='buy')

        
    if (macd < signal) & ((macd & signal)>0) &(price>moving_average):

        if active_position == 1:
            enter_position(order_type='sell')


     #Check bearish signal
    if (macd < signal) & ((macd & signal)<0) &(price*1.001 < moving_average):

        if active_position == 0:
            enter_position(order_type='buy')

        
    if (macd > signal) & ((macd & signal)>0) &(price*1.001>moving_average):

        if active_position == 1:
             enter_position(order_type='sell')








while True:
    main()
    sleep(2)
