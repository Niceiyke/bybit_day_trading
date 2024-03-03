from helper import get_price_difference
from ta import momentum


def calculate_macd(df):
    close_df = df["Close"]
    ema20 = close_df.ewm(span=20, adjust=False).mean()
    ema50 = close_df.ewm(span=50, adjust=False).mean()
    ema200 = close_df.ewm(span=200, adjust=False).mean()
    macd = ema20 - ema50
    signal = macd.ewm(span=9, adjust=False).mean()
    rsi = momentum.RSIIndicator(close_df).rsi()
    return ema20, ema50, ema200, macd, signal, rsi


def get_strategy(df):
    strategy = "none"
    ema20, ema50, ema200, macd, signal, rsi = calculate_macd(df)

    print("macd:", macd, "signal:", signal, "rsi:", rsi)

    # Check bullish signal long
    if (macd > signal) and (macd < 0) and (signal < 0) and (rsi < 60):
        strategy = "buy"
        return strategy

    # Check bearish signal short
    if (signal > macd) and (macd < 0) and (signal < 0) and (rsi < 50):

        strategy = "sell"
        return strategy

    # Default case
    return strategy
