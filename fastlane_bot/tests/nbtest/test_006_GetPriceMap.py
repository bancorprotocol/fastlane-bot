# ------------------------------------------------------------
# Auto generated test file `test_006_GetPriceMap.py`
# ------------------------------------------------------------
# source file   = NBTest_006_GetPriceMap.py
# source path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# test id       = 006
# test comment  = GetPriceMap
# ------------------------------------------------------------



import time
import json
from fastlane_bot.bot import CarbonBot

import requests

def get_updated_price_in_bnt_units(token_symbol: str, rate_limit: int = 30) -> float:
    """
    Call the coingecko api to get the price of the token in BNT units.

    Parameters
    ----------
    token_symbol : str
        Ticker symbol of the token.

    Returns
    -------
    float
        The price of the token in BNT units.

    """
    try:
        # CoinGecko API base URL
        base_url = "https://api.coingecko.com/api/v3"

        # Get token and BNT IDs from CoinGecko API
        token_id_url = f"{base_url}/search?query={token_symbol}"
        bnt_id_url = f"{base_url}/search?query=BNT"
        token_id_response = requests.get(token_id_url)
        bnt_id_response = requests.get(bnt_id_url)

        # decode the Response object to a dict
        token_id_response = token_id_response.json()
        bnt_id_response = bnt_id_response.json()
        token_id = token_id_response['coins'][0]['id']
        bnt_id = bnt_id_response['coins'][0]['id']

        # Get token and BNT prices in USD
        price_url = f"{base_url}/simple/price?ids={token_id}%2C{bnt_id}&vs_currencies=usd"
        price_response = requests.get(price_url)

        # decode the Response object to a dict
        price_response = price_response.json()
        token_usd_price = price_response[token_id]['usd']
        bnt_usd_price = price_response[bnt_id]['usd']

        # Calculate the token price in BNT units
        token_bnt_price = token_usd_price / bnt_usd_price

        time.sleep(rate_limit)
        return token_bnt_price

    except Exception as e:
        print(f"Error getting price for {token_symbol}: {e}")
        return 0.0



from fastlane_bot.tools.cpc import CPCContainer

bot = CarbonBot()
bnt_price_map = bot.db.bnt_price_map
curves = bot.get_curves()
CCm = CPCContainer(curves)
tokens = CCm.tokens()
symbols = list(set([token.split('-')[0] for token in tokens]))
symbols = [symbol for symbol in symbols if symbol not in bnt_price_map.keys()]
symbols

price_dicts = {symbol: get_updated_price_in_bnt_units(symbol) for symbol in symbols}
price_dicts

assert len(price_dicts) > 0