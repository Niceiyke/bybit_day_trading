from ta import momentum

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
        




