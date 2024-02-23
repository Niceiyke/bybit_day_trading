import pandas as pd
import numpy as np
from keys import api, secret
from pybit.unified_trading import HTTP


session = HTTP(
    api_key=api,
    api_secret=secret)

def klines():
    try:
        resp = session.get_kline(
            category='linear',
            symbol='BTCUSDT',
            interval=1,
            limit=1500
        )['result']['list']
        resp = pd.DataFrame(resp)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        resp = resp.set_index('Time')
        resp = resp.astype(float)
        resp = resp[::-1]
        return resp
    except Exception as err:
        print(err)

import pandas as pd
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, min_periods=1, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, min_periods=1, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, min_periods=1, adjust=False).mean()
    return macd, signal_line

# Function to generate buy/sell signals with stop loss and take profit
def generate_signals(data, stop_loss_pct=0.02, take_profit_pct=0.05):
    buy_signal = (data['MACD'] > data['Signal']) & (data['Close'] > data['200_MA'])
    sell_signal = (data['MACD'] < data['Signal']) & (data['Close'] < data['200_MA'])
    
    # Implement stop loss and take profit
    for i in range(len(data)):
        if buy_signal[i]:
            stop_loss_price = data['Close'][i] * (1 - stop_loss_pct)
            take_profit_price = data['Close'][i] * (1 + take_profit_pct)
            for j in range(i+1, min(i+6, len(data))):  # Check next 5 days for stop loss/take profit
                if data['Close'][j] <= stop_loss_price:
                    buy_signal[i:j+1] = False
                    break
                elif data['Close'][j] >= take_profit_price:
                    sell_signal[i:j+1] = True
                    break
                    
    return buy_signal, sell_signal

# Function to backtest the trading strategy
def backtest_strategy(data):
    initial_capital = 10000  # Initial capital in USD
    capital = initial_capital
    position = 0  # 0: No position, 1: Long position, -1: Short position
    buy_price = 0
    sell_price = 0
    trades = []

    for i in range(1, len(data)):
        if data['Buy_Signal'][i] and position == 0:
            position = 1
            buy_price = data['Close'][i]
            capital -= buy_price
        elif data['Sell_Signal'][i] and position == 1:
            position = 0
            sell_price = data['Close'][i]
            capital += sell_price
            trades.append((buy_price, sell_price))

    # Calculate final capital and returns
    final_value = capital + (position * data['Close'].iloc[-1])
    returns = (final_value - initial_capital) / initial_capital * 100

    return final_value, returns, trades

# Load your crypto data (replace this with your actual data loading code)
# Example: data = pd.read_csv('crypto_data.csv')

# Assume data has 'Date', 'Close' columns
# Let's calculate 200-day Moving Average
data=klines()
data['200_MA'] = data['Close'].rolling(window=200).mean()

# Calculate MACD and Signal line
data['MACD'], data['Signal'] = calculate_macd(data)

# Generate buy/sell signals with stop loss and take profit
data['Buy_Signal'], data['Sell_Signal'] = generate_signals(data)

# Perform backtesting
final_value, returns, trades = backtest_strategy(data)

print("Final Portfolio Value: $", final_value)
print("Total Return: ", returns, "%")

# Plotting
plt.figure(figsize=(14,7))
plt.plot(data['Close'], label='Close Price', alpha=0.5)
plt.plot(data['200_MA'], label='200-day MA', alpha=0.5)
plt.scatter(data.index[data['Buy_Signal']], data['Close'][data['Buy_Signal']], marker='^', color='g', label='Buy Signal')
plt.scatter(data.index[data['Sell_Signal']], data['Close'][data['Sell_Signal']], marker='v', color='r', label='Sell Signal')
plt.title('Enhanced Crypto Trading Strategy with MACD, 200-day MA, Stop Loss, and Take Profit')
plt.legend()
plt.show()
