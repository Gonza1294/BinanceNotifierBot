import json
from binance import Client

def truncate_float(value):
    factor = 10 ** 2
    return int(value * factor) / factor

def getBalance(update, context, coin):
    try:
        client = setup_client()
        balance = float(client.get_asset_balance(str(coin))["free"])
        balance = truncate_float(balance)
        return balance
    except:
        return "ERROR"

def setup_client():
    with open(f"keys.json", "r", encoding="utf8") as f:
        account = json.loads(f.read())
    return Client(account["api_key"], account["api_secret"])
