# Getting your current positions. It returns symbols list with opened positions
def get_positions(client):
    try:
        resp = client.get_positions(category="linear", settleCoin="USDT")["result"][
            "list"
        ]
        pos = []
        for elem in resp:
            pos.append(elem["symbol"])
        return pos
    except Exception as err:
        print(err)


# Getting last 50 PnL. I used it to check strategies performance
def get_pnl(client):
    try:
        resp = client.get_closed_pnl(category="linear", limit=50)["result"]["list"]
        pnl = 0
        for elem in resp:
            pnl += float(elem["closedPnl"])
        return pnl
    except Exception as err:
        print(err)


# Changing mode and leverage:
def set_mode(client, symbol, mode, leverage):
    try:
        resp = client.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=leverage,
            sellLeverage=leverage,
        )
        print(resp)
    except Exception as err:
        print(err)


# Getting number of decimal digits for price and qty
def get_precisions(client, symbol):
    try:
        resp = client.get_instruments_info(category="linear", symbol=symbol)["result"][
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


# pct_diff
def get_price_difference(side, current_price, moving_average_price):

    if side == "buy":
        price_diff = (moving_average_price - current_price) / current_price
        return round(price_diff * 100, 2)

    else:
        price_diff = (current_price - moving_average_price) / moving_average_price
        return round(price_diff * 100, 2)


def get_tp_spl(expected_profit, amount, price, side, precision):

    expected_loss = expected_profit / 3

    perct_increae = expected_profit / amount
    perct_decreae = expected_loss / amount

    ltp = round(price * (1 + perct_increae), precision)
    lsl = round(price * (1 - perct_decreae), precision)

    stp = round(price * (1 - perct_increae), precision)
    ssl = round(price * (1 + perct_decreae), precision)

    if side == "buy":
        return (ltp, lsl)

    else:
        return (stp, ssl)
