from helper import get_price_difference
from ta import momentum


def calculate_macd(df):
    close_prices = df["Close"]
    ema_12 = close_prices.ewm(span=12, adjust=False).mean()
    ema_26 = close_prices.ewm(span=26, adjust=False).mean()
    ema_50 = close_prices.ewm(span=50, adjust=False).mean()
    ema_200 = close_prices.ewm(span=200, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    rsi = momentum.RSIIndicator(close_prices).rsi()
    return (
        macd_line,
        signal_line,
        rsi,
        ema_12.iloc[-1],
        ema_50.iloc[-1],
        ema_200.iloc[-1],
    )


def get_strategy(df):
    strategy = "hold"
    macd, signal, rsi, short_term_ema, mid_term_ema, long_term_ema = calculate_macd(df)
    macd = macd.iloc[-1]
    signal = signal.iloc[-1]
    rsi = rsi.iloc[-1]
    short_term_ema = short_term_ema
    mid_term_ema = mid_term_ema
    long_term_ema = long_term_ema

    print("macd:", macd, "signal:", signal, "rsi:", rsi)
    print("short:", short_term_ema, "mid:", mid_term_ema, "long:", long_term_ema)

    # Check bullish signal long
    if short_term_ema > mid_term_ema:
        print("buy 1")
        if mid_term_ema > long_term_ema:
            print("buy 2")
            if macd > signal:
                print("buy 3")
                if rsi < 60:
                    print("buy 4")
                    strategy = "buy"
                    return strategy

    # Check bearish signal short
    if short_term_ema < mid_term_ema:
        print("sell1")
        if mid_term_ema < long_term_ema:
            print("sell 2")
            if signal > macd:
                print("sell 3")
                if rsi < 50:
                    print("sell 4")
                    strategy = "sell"
                    return strategy

    # Default case
    return strategy
