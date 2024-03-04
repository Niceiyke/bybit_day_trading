from pybit.unified_trading import HTTP


client = HTTP(
        testnet=True,
        api_key="vHnoV1kQTgYsmhaY2s",
        api_secret="C5lVp013avzhEZgojyYxiT4TzwnZOX70gu8n",
    )



# Getting your current positions. It returns symbols list with opened positions
def get_positions():
    try:
        resp = client.get_positions(category="linear", settleCoin="USDT")["result"][
            "list"
        ]
        pos = []
        for elem in resp:

            pos.append(elem)
        return pos
    except Exception as err:
        print(err)


def close_position():
    positions =get_positions()
    profit_price =12
    for position in positions:
        print(position)
        unrealisedPnl=float(position["unrealisedPnl"])
        symbol=position["symbol"]
        side=position["side"]
        order_quantity =position["size"]
        leverage =int(position["leverage"])

        if unrealisedPnl >profit_price:
        
            if side =="Buy":

                sides="Sell"

                client.place_order(
                    category="linear",
                    symbol=symbol,
                        side=sides,
                        order_type="Market",
                        qty= order_quantity,
                        time_in_force="GoodTillCancel",
                        reduce_only=True,
                        close_on_trigger=False)
            
            if side =="Sell":
                sides == "Buy"
                client.place_order(
                    category="linear",
                    symbol=symbol,
                    side=sides,
                    order_type="Market",
                    qty= order_quantity,
                    time_in_force="GoodTillCancel",
                    reduce_only=True,
                    close_on_trigger=False)
        
if __name__ =="__main__":
    close_position()