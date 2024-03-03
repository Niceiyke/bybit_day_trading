from helper import get_price_difference
from ta import momentum


def calculate_macd(df):
    close_prices = df["Close"]
    ema_12 = close_prices.ewm(span=12, adjust=False).mean()
    ema_26 = close_prices.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    rsi = momentum.RSIIndicator(close_prices).rsi()
    return macd_line, signal_line, rsi


def get_strategy(df):
    strategy = "none"
    macd, signal, rsi = calculate_macd(df)
    macd = macd.iloc[-1]
    signal = signal.iloc[-1]
    rsi = rsi.iloc[-1]

    print("macd:", macd, "signal:", signal, "rsi:", rsi)

    # Check bullish signal long
    if (macd > signal) and (rsi < 60):
        strategy = "buy"
        return strategy

    # Check bearish signal short
    if (signal > macd) and (rsi < 50):

        strategy = "sell"
        return strategy

    # Default case
    return strategy
