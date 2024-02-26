from helper import get_price_difference

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
    if macd>signal and macd < 0 and signal < 0 and  moving_average > price :

        pct_diff= get_price_difference(side='buy',current_price=price,moving_average_price=moving_average)

        if pct_diff > 5:
            return    
        strategy = "buy"
        return strategy

    # Check bearish signal short
    if signal>macd and macd > 0 and signal > 0 and moving_average < price:

        pct_diff= get_price_difference(side='sell',current_price=price,moving_average_price=moving_average)

        if pct_diff < 5:
            return  
        
        strategy = "sell"
        return strategy

    # Default case
    return strategy
