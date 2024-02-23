from keys import api, secret
from pybit.unified_trading import HTTP
import pandas as pd
import ta
from time import sleep


session = HTTP(api_key=api, api_secret=secret)


# session = HTTP(testnet=False,api_key="...",api_secret="...",)

# Config:
tp = 1.03  # Take Profit +1.2%
sl = 0.99  # Stop Loss -0.9%
timeframe = 15  # 15 minutes
mode = 0  # 1 - Isolated, 0 - Cross
leverage = 20
qty = 200  # Amount of USDT for one order


# Getting balance on Bybit Derivatrives Asset (in USDT)
def get_balance():
    try:
        resp = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")["result"][
            "list"
        ][0]["coin"][0]["walletBalance"]
        resp = float(resp)
        print(resp)
        return resp
    except Exception as err:
        print("error occured")
        print(err)


print(f"Your balance: {get_balance()} USDT")


# Getting all available symbols from Derivatives market (like 'BTCUSDT', 'XRPUSDT', etc)
def get_tickers():
    try:
        resp = session.get_tickers(category="linear")["result"]["list"]
        symbols = []
        for elem in resp:
            if "USDT" in elem["symbol"] and not "USDC" in elem["symbol"]:
                if float(elem["turnover24h"]) > 100000000:
                    symbols.append(elem["symbol"])

        print(f"you have total of {len(symbols)} crypto to trade")
        return symbols
    except Exception as err:
        print(err)


# Klines is the candles of some symbol (up to 1500 candles). Dataframe, last elem has [-1] index
def klines(symbol):
    try:
        resp = session.get_kline(
            category="linear", symbol=symbol, interval=timeframe, limit=750
        )["result"]["list"]
        resp = pd.DataFrame(resp)
        resp.columns = ["Time", "Open", "High", "Low", "Close", "Volume", "Turnover"]
        resp = resp.set_index("Time")
        resp = resp.astype(float)
        resp = resp[::-1]
        return resp
    except Exception as err:
        print(err)


# Getting your current positions. It returns symbols list with opened positions
def get_positions():
    try:
        resp = session.get_positions(category="linear", settleCoin="USDT")["result"][
            "list"
        ]
        pos = []
        for elem in resp:
            pos.append(elem["symbol"])
        return pos
    except Exception as err:
        print(err)


# Getting last 50 PnL. I used it to check strategies performance
def get_pnl():
    try:
        resp = session.get_closed_pnl(category="linear", limit=50)["result"]["list"]
        pnl = 0
        for elem in resp:
            pnl += float(elem["closedPnl"])
        return pnl
    except Exception as err:
        print(err)


# Changing mode and leverage:
def set_mode(symbol):
    try:
        resp = session.switch_margin_mode(
            category="linear",
            symbol=symbol,
            tradeMode=mode,
            buyLeverage=leverage,
            sellLeverage=leverage,
        )
        print(resp)
    except Exception as err:
        print(err)


# Getting number of decimal digits for price and qty
def get_precisions(symbol):
    try:
        resp = session.get_instruments_info(category="linear", symbol=symbol)["result"][
            "list"
        ][0]
        price = resp["priceFilter"]["tickSize"]
        if "." in price:
            price = len(price.split(".")[1])
        else:
            price = 0
        qty = resp["lotSizeFilter"]["qtyStep"]
        if "." in qty:
            qty = len(qty.split(".")[1])
        else:
            qty = 0

        return price, qty
    except Exception as err:
        print(err)


# Placing order with Market price. Placing TP and SL as well
def place_order_market(symbol, side):
    price_precision = get_precisions(symbol)[0]
    qty_precision = get_precisions(symbol)[1]
    mark_price = session.get_tickers(category="linear", symbol=symbol)["result"][
        "list"
    ][0]["markPrice"]
    mark_price = float(mark_price)
    print(f"Placing {side} order for {symbol}. Mark price: {mark_price}")
    order_qty = round(qty / mark_price, qty_precision)
    sleep(1)
    if side == "buy":
        try:
            tp_price = round(mark_price * tp, price_precision)
            sl_price = round(mark_price * sl, price_precision)
            resp = session.place_order(
                category="linear",
                symbol=symbol,
                side="Buy",
                orderType="Market",
                qty=order_qty,
                takeProfit=tp_price,
                stopLoss=sl_price,
                tpTriggerBy="MarkPrice",
                slTriggerBy="MarkPrice",
            )
            print(resp)
        except Exception as err:
            print(err)

    if side == "sell":
        try:
            tp_price = round(mark_price - mark_price * tp, price_precision)
            sl_price = round(mark_price + mark_price * sl, price_precision)
            resp = session.place_order(
                category="linear",
                symbol=symbol,
                side="Sell",
                orderType="Market",
                qty=order_qty,
                takeProfit=tp_price,
                stopLoss=sl_price,
                tpTriggerBy="Market",
                slTriggerBy="Market",
            )
            print(resp)
        except Exception as err:
            print(err)


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
    if macd > signal and macd < 0 and signal < 0 and price < moving_average:
        strategy = "buy"
        return strategy

    # Check bearish signal short
    if macd < signal and macd > 0 and signal > 0 and moving_average < price:
        strategy = "sell"
        return strategy

    # Default case
    return strategy


def macd_signal(symbol):
    data = klines(symbol)
    return get_strategy(df=data)


max_pos = 5  # Max current orders
# symbols = get_tickers()  # getting all symbols from the Bybit Derivatives

symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "UNIUSDT",
    "XAIUSDT",
    "SCUSDT",
    "FLRUSDT",
    "FRONTUSDT",
    "COTIUSDT",
    "AMBUSDT",
]

# Infinite loop
while True:
    balance = get_balance()
    if balance == None:
        print("Cant connect to API")
    if balance != None:
        balance = float(balance)
        print(f"Balance: {balance}")
        pos = get_positions()
        print(f"You have {len(pos)} positions: {pos}")

        for symbol in symbols:
            pos = get_positions()
            print(symbol)
            signal = macd_signal(symbol)
            print(signal)

            # Signal to sell

            if symbol in pos and signal == "sell":
                if signal == "sell":
                    print(f"Found SELL signal for {symbol}")
                    set_mode(symbol)
                    sleep(2)
                    place_order_market(symbol, "sell")
                    sleep(5)

            # Signal to buy

            signal = macd_signal(symbol)
            if symbol in pos and signal == "buy":
                break
            if signal == "buy":
                if len(pos) >= max_pos:
                    break
                print(f"Found BUY signal for {symbol}")
                set_mode(symbol)
                sleep(2)
                place_order_market(symbol, "buy")
                sleep(5)

    print("Waiting 20 seconds")
    sleep(10)
