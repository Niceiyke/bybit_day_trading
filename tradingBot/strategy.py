from ta import momentum
from ta import trend
import pandas as pd

def calculate_ema(df):
    close_df = df["Close"]
    ema9 = close_df.ewm(span=9, adjust=False).mean()
    ema14 = close_df.ewm(span=14, adjust=False).mean()
    ema21 = close_df.ewm(span=21, adjust=False).mean()
    ema26 = close_df.ewm(span=26, adjust=False).mean()
    ema50 = close_df.ewm(span=50, adjust=False).mean()
    ema200 = close_df.ewm(span=200, adjust=False).mean()

    return ema9.iloc[-1], ema14.iloc[-1], ema21.iloc[-1], ema26.iloc[-1], ema50.iloc[-1], ema200.iloc[-1], close_df.iloc[-1]


def three_moving_average_rsi_strategy(df):
    ema9, ema14, ema21, ema26, ema50, ema200, last_price = calculate_ema(df=df)
    rsi = momentum.rsi(close=df['Close'], window=14).iloc[-1]

    if (last_price > ema21) and (ema21 > ema50) and (ema50 > ema200) and (rsi < 50):
        return 'buy'
    
    elif (last_price < ema21) and (ema21 < ema50) and (ema50 < ema200) and (rsi > 50):
        return 'sell'
    else:
        return 'hold'
        




# Function to generate trading signals based on refined strategy
def trend_strategy(df5,df15):
    strategy ='hold'
    df5=df5['Close']
    df15=df15['Close']
    # Calculate EMAs for both timeframes
    ema9_5min = df5.ewm(span=9).mean()
    ema50_5min = df5.ewm(span=50).mean()
    ema100_5min = df5.ewm(span=100).mean()
    ema200_5min = df5.ewm(span=200).mean()

    ema9_15min = df15.ewm(span=9).mean()
    ema50_15min = df15.ewm(span=50).mean()
    ema100_15min = df15.ewm(span=100).mean()
    ema200_15min = df15.ewm(span=200).mean()

 
    # Calculate MACD for confirmation
    macd_5min = trend.MACD(close=df5).macd()
    macd_15min = trend.MACD(close=df15).macd()
    
    # Calculate RSI for confirmation
    rsi_5min = momentum.RSIIndicator(df5).rsi()
    rsi_15min = momentum.RSIIndicator(df15).rsi()


     # Long Entry (Buy Signal) with confirmation
    

    if (ema9_5min.iloc[-2] < ema50_5min.iloc[-2]) and (ema9_5min.iloc[-1] > ema50_5min.iloc[-1]):
        strategy ='buy'
        return strategy
    
    if (ema9_5min.iloc[-2] > ema50_5min.iloc[-2]) and (ema9_5min.iloc[-1] < ema50_5min.iloc[-1]):
            strategy ='sell'
            return strategy
    
    else:
         return 'hold'

        
   
        
    
    


    













    
    signals = pd.DataFrame(index=df.index)
    signals['Price'] = df
    signals['Signal'] ='hold'
    
    # Long Entry (Buy Signal) with confirmation
    signals['Signal'][(ema9_15min.shift(1) < ema50_15min.shift(1)) & (ema9_15min > ema50_15min) & 
                      (ema50_30min.shift(1) < ema100_30min.shift(1)) & (ema50_30min > ema100_30min) &
                      (macd > 0) & (rsi > 30)] = 'buy'
    
    # Short Entry (Sell Signal) with confirmation
    signals['Signal'][(ema9_15min.shift(1) > ema50_15min.shift(1)) & (ema9_15min < ema50_15min) & 
                      (ema50_30min.shift(1) > ema100_30min.shift(1)) & (ema50_30min < ema100_30min) &
                      (macd < 0) & (rsi < 70)] = 'sell'
    