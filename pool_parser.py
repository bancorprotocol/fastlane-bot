import json

import pandas as pd
from web3 import Web3
from joblib import parallel_backend, Parallel, delayed

import os
from dotenv import load_dotenv

load_dotenv()

UNI_V2_POOL_ABI = json.loads(
    """
    [{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"sync","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]
    """
)

ALCHEMY_API_KEY = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")
web3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY}"))

uni_v2_factory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
uni_v3_factory = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
sushi_v2_factory = '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'
sushi_v3_factory = '0xbACEB8eC6b9355Dfc0269C18bac9d6E2Bdc29C4F'

uni_check = "0xEBd17511F46A877199Ff08f0eA4f119c9b4Aea50"
sushi_check = "0xa99245eBAf606644B4674994717B3EfA098272FE"
uni_v3_check = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'
sushi_v3_check = '0x2214A42d8e2A1d20635c2cb0664422c528B6A432'

def get_exchange_for_pool(pool_address, exchange):
    """
    Checks the factory address of a pool to see if it's a Uni V2 pool or a Sushiswap pool
    returns a tuple with the name of the exchange + the address
    """
    if exchange not in ["uniswap_v2", "uniswap_v3", "sushiswap_v2", "sushiswap_v3"]:
        return exchange, pool_address
    pool_address = web3.toChecksumAddress(pool_address)
    try:
        pool = web3.eth.contract(address=pool_address, abi=UNI_V2_POOL_ABI)
        factory_address = pool.caller.factory()
    except Exception as e:
        print(f"unknown pool for address: {pool_address} - {e}")
        return "unknown"
    if factory_address == uni_v2_factory:
        return ("uniswap_v2", pool_address)
    elif factory_address == uni_v3_factory:
        return ("uniswap_v3", pool_address)
    elif factory_address == sushi_v2_factory:
        return ("sushiswap_v2", pool_address)
    elif factory_address == sushi_v3_factory:
        return ("sushiswap_v3", pool_address)
    else:
        return ("unknown", pool_address)


def get_exchanges_for_pools(pool_addresses):
    l = []
    for address, exchange in pool_addresses:
        l.append(get_exchange_for_pool(address, exchange))
    return l


# static_pool_data = pd.read_csv(
#     f"fastlane_bot/data/static_pool_data.csv", low_memory=False
# )
#
# static_pool_data_original = static_pool_data.copy()
#
# exchanges = get_exchanges_for_pools(static_pool_data[["address", "exchange_name"]].values)
# static_pool_data["exchange_name"] = [x[0] for x in exchanges]

# write to csv
# static_pool_data_original = pd.read_csv(
#     f"fastlane_bot/data/static_pool_data.csv", low_memory=False
# )

static_pool_data = pd.read_csv(
    f"fastlane_bot/data/static_pool_data_corrected.csv", low_memory=False
)
static_pool_data["exchange_name"] = static_pool_data["exchange"].values

# write to csv
static_pool_data.to_csv(
    f"fastlane_bot/data/static_pool_data.csv", index=False
)
#
# # print the number of exchanges that differ from the original
# print(
#     f"Number of exchanges that differ from the original: {len(static_pool_data[static_pool_data['exchange'] != static_pool_data_original['exchange_name']])}"
# )
#
# # select the rows that differ from the original
# diffs = static_pool_data[static_pool_data["exchange"] != static_pool_data_original["exchange_name"]]
#
# # print the pairs that differ from the original
# print(
#     f"Pairs that differ from the original: {diffs[['address', 'exchange', 'exchange_name']].values}"
# )
#
# # print the percent of rows that differ from the original
# print(
#     f"Percent of rows that differ from the original: {len(diffs) / len(static_pool_data) * 100}"
# )


