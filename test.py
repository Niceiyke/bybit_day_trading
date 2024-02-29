import pandas as pd
from ta.trend import MACD
from ta.momentum import RSIIndicator

# Function to generate trading signals based on refined strategy
def generate_signals(close_prices):
    # Calculate EMAs for both timeframes
    ema9_15min = close_prices.ewm(span=9).mean()
    ema50_15min = close_prices.ewm(span=50).mean()
    ema50_30min = close_prices.resample('30T').apply(lambda x: x.ewm(span=50).mean())
    ema100_30min = close_prices.resample('30T').apply(lambda x: x.ewm(span=100).mean())
    
    # Calculate MACD for confirmation
    macd = MACD(close=close_prices).macd()
    
    # Calculate RSI for confirmation
    rsi = RSIIndicator(close_prices).rsi()
    
    signals = pd.DataFrame(index=close_prices.index)
    signals['Price'] = close_prices
    signals['Signal'] = 0.0
    
    # Long Entry (Buy Signal) with confirmation
    signals['Signal'][(ema9_15min.shift(1) < ema50_15min.shift(1)) & (ema9_15min > ema50_15min) & 
                      (ema50_30min.shift(1) < ema100_30min.shift(1)) & (ema50_30min > ema100_30min) &
                      (macd > 0) & (rsi > 30)] = 1.0
    
    # Short Entry (Sell Signal) with confirmation
    signals['Signal'][(ema9_15min.shift(1) > ema50_15min.shift(1)) & (ema9_15min < ema50_15min) & 
                      (ema50_30min.shift(1) > ema100_30min.shift(1)) & (ema50_30min < ema100_30min) &
                      (macd < 0) & (rsi < 70)] = -1.0
    
    # Exit long positions
    signals['Signal'][(ema9_15min.shift(1) > ema50_15min.shift(1)) & (ema9_15min < ema50_15min)] = 0.0
    
    # Exit short positions
    signals['Signal'][(ema9_15min.shift(1) < ema50_15min.shift(1)) & (ema9_15min > ema50_15min)] = 0.0
    
    return signals

# Main function to run the refined trading strategy
def main():
    # Assuming you have fetched historical price data for the desired cryptocurrency pair
    close_prices = pd.Series()  # Replace this with actual data
    signals = generate_signals(close_prices)
    print(signals)


main()
