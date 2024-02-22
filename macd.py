from keys import api, secret
from pybit.unified_trading import HTTP
import pandas as pd
import ta
from time import sleep



session = HTTP(
    api_key=api,
    api_secret=secret)


# Config:
tp = 0.012  # Take Profit +1.2%
sl = 0.009  # Stop Loss -0.9%
timeframe = 1  # 1 minutes
mode = 1  # 1 - Isolated, 0 - Cross
leverage = 10
candle_limit =720
qty = 10   # Amount of USDT for one order



def klines():
    try:
        resp = session.get_kline(
            category='linear',
            symbol="BTCUSDT",
            interval=timeframe,
            limit=candle_limit
        )['result']['list']
        resp = pd.DataFrame(resp)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        resp = resp.set_index('Time')
        resp = resp.astype(float)
        resp = resp[::-1]
        return resp
    except Exception as err:
        print(err)



def macd_calculation():
    df= klines()

    close_df=df['Close']
    low_df =df['Low']

    low =low_df.iloc[-5:].mean()
    
    print('low',low)

    cp =close_df.iloc[-1]

    ma9=close_df.ewm(span=12,adjust=False).mean()
    ma26=close_df.ewm(span=26,adjust=False).mean()
    ema200=close_df.ewm(span=200,adjust=False).mean()

    macd= ma9-ma26
    signal =macd.ewm(span=9,adjust=False).mean()



    return macd.iloc[-1],signal.iloc[-1],ema200.iloc[-1],cp





def buy_stratagy():
    print("buy")


def sell_stratagy():
    print("sell")

def active_trade():
    position =0
    
    return position

def main():
    macd,signal,ema200,cp =macd_calculation()

    diff =(macd)-(signal)

    active_buy_trade =active_trade()

    action =0

    print('cp:',cp)

    print('ma200:',ema200)

    print("MACD:",macd)
    print("SIGNAL:",signal)

    print('diff:',diff)


    if active_buy_trade==0:
        if cp<ema200:
                print("buy1")
                if macd < 0:
                    print("buy2")
                    if 3 <diff<15:
                        print("buy3")
                        action =1
                        buy_stratagy()

        else:
            if action == 0:
             print ("No Market")

    if active_trade==1:
        if cp>ema200:
            print("sell1")
            if macd > 0:
                print("sell2")
                if -15 <diff<0:
                    print("sell3")
                    action =2
                    sell_stratagy()
                    return

    

while True:
    main()
    sleep(5)
