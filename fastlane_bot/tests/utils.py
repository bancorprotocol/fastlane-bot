import os
import random

from fastlane_bot.constants import ec
from fastlane_bot.networks import EthereumNetwork
from fastlane_bot.pools import LiquidityPool
from fastlane_bot.routes import Route
from fastlane_bot.token import ERC20Token
from fastlane_bot.ui import FastLaneArbBotUI

logger = ec.DEFAULT_LOGGER
supported_tokens = ec.SUPPORTED_TOKENS
supported_exchanges = ec.SUPPORTED_EXCHANGES
db = ec.DB

# # Valid Constant Product Params 1
# db1 = db[(db["exchange"] == "bancor_v2") & (db["symbol0"] == "BNT") & (db["symbol1"] != "ETH")]
# address1 = db1["address"].iloc[0]
# fee1 = db1["fee"].iloc[0]
# pair1 = db1["pair"].iloc[0]
# exchange1 = "uniswap_v3"
# tkn0_1 = db1["symbol0"].iloc[0]
# tkn1_1 = db1["symbol1"].iloc[0]
#
# # Valid Constant Product Params 2
# db2 = db[(db["exchange"] == "uniswap_v3") & (db["symbol0"] == tkn1_1)]
# address2 = db2["address"].iloc[0]
# fee2 = db2["fee"].iloc[0]
# pair2 = db2["pair"].iloc[0]
# exchange2 = "uniswap_v3"
# tkn0_2 = db2["symbol0"].iloc[0]
# tkn1_2 = db2["symbol1"].iloc[0]
#
# # Valid Constant Product Params 3
# db3 = db[(db["exchange"] == "bancor_v2") & (db["symbol1"] == "BNT") & (db["symbol0"] == tkn1_2)]
# address3 = db3["address"].iloc[0]
# fee3 = db3["fee"].iloc[0]
# pair3 = db3["pair"].iloc[0]
# exchange3 = "bancor_v2"
# tkn0_3 = db3["symbol0"].iloc[0]
# tkn1_3 = db3["symbol1"].iloc[0]

ntwk = EthereumNetwork(
    network_id=ec.TEST_NETWORK,
    network_name=ec.TEST_NETWORK_NAME,
    provider_url=ec.TENDERLY_FORK_RPC,
    fastlane_contract_address=ec.FASTLANE_CONTRACT_ADDRESS,
).connect_network()


def make_mock_constant_product_route():
    q = False
    while not q:
        try:
            p1 = make_mock_constant_product_pool(is_bnt=True)
            p2 = make_mock_constant_product_pool(is_match=p1.tkn1.symbol)
            p3 = make_mock_constant_product_pool(is_match=p2.tkn1.symbol, is_bnt=True)
            if p3.tkn0.symbol == "BNT":
                p3.reverse_tokens()
            q = True
        except Exception as e:
            continue
    trade_path = [p1, p2, p3]
    return Route(trade_path=trade_path)


def make_mock_constant_function_route():
    q = False
    while not q:
        try:
            p1 = make_mock_constant_product_pool(is_bnt=True)
            p2 = make_mock_constant_function_pool(is_match=p1.tkn1.symbol)
            p3 = make_mock_constant_product_pool(is_match=p2.tkn1.symbol, is_bnt=True)
            if p3.tkn0.symbol == "BNT":
                p3.reverse_tokens()
            q = True
        except Exception as e:
            continue
    trade_path = [p1, p2, p3]
    return Route(trade_path=trade_path)


def make_mock_constant_product_pool(is_bnt=False, is_match=None):
    df = db[~db["exchange"].isin(["uniswap_v3", "carbon_v1"])]
    if is_bnt:
        df = df[(df["symbol0"] == "BNT") | (df["symbol1"] == "BNT")]
    else:
        df = df[(df["symbol0"] != "BNT") & (df["symbol1"] != "BNT")]
    if is_match:
        df = df[((df["symbol0"] == is_match) | (df["symbol1"] == is_match))]
    random_route_idx = random.choice(list(df.index))
    random_route = db.loc[[random_route_idx]]
    return LiquidityPool(
        exchange=random_route["exchange"].values[0],
        tkn0=ERC20Token(
            symbol=random_route["symbol0"].values[0], amt=random.choice(range(1, 1000))
        ),
        tkn1=ERC20Token(
            symbol=random_route["symbol1"].values[0], amt=random.choice(range(1, 1000))
        ),
    )


def make_mock_constant_function_pool(is_match=None):
    df = db[db["exchange"].isin(["uniswap_v3"])]
    if is_match:
        if is_match == "ETH":
            is_match = "WETH"
        df = df[((df["symbol0"] == is_match) | (df["symbol1"] == is_match))]
    random_route_idx = random.choice(list(df.index))
    random_route = db.loc[[random_route_idx]]
    amt0 = random.choice(range(1, 1000))
    amt1 = random.choice(range(1, 1000))
    liquidity = amt0 * amt1
    sqrt_price_q96 = (amt0 * amt1) ** 2
    return LiquidityPool(
        init_liquidity=False,
        exchange=random_route["exchange"].values[0],
        tkn0=ERC20Token(symbol=random_route["symbol0"].values[0], amt=amt0),
        tkn1=ERC20Token(symbol=random_route["symbol1"].values[0], amt=amt1),
        liquidity=liquidity,
        sqrt_price_q96=sqrt_price_q96,
        fee=random_route["fee"].values[0],
        tick=0,
    )


def make_mock_bot_instance():
    ETH_PRIVATE_KEY = os.environ.get("ETH_PRIVATE_KEY_BE_CAREFUL")
    return FastLaneArbBotUI(web3=ntwk, _ETH_PRIVATE_KEY=ETH_PRIVATE_KEY)


def get_pool_test_info(exchange: str):
    db = ec.DB
    db = db[(db["exchange"] == exchange)]
    address = db["address"].iloc[0]
    fee = db["fee"].iloc[0]
    pair = db["pair"].iloc[0]
    tkn0 = db["symbol0"].iloc[0]
    tkn1 = db["symbol1"].iloc[0]
    tkn0 = ERC20Token(symbol=db["symbol0"].iloc[0])
    tkn1 = ERC20Token(symbol=db["symbol1"].iloc[0])
    return address, fee, pair, tkn0, tkn1
