from pybit.unified_trading import HTTP
from keys import api, secret
session = HTTP(
    testnet=True,
    api_key=api,
    api_secret=secret
)

try:
    print(session.place_order(
    category="spot",
    symbol="BTCUSDT",
    side="Buy",
    orderType="Limit",
    qty="0.1",
    price="50000",
    timeInForce="PostOnly",
    orderLinkId="spot-test-postonly",
    isLeverage=0,
    orderFilter="Order",
))
    print("done")
except Exception as err:
        print(err)

