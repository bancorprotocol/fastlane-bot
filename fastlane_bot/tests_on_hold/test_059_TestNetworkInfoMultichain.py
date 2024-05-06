# ------------------------------------------------------------
# Auto generated test file `test_059_TestNetworkInfoMultichain.py`
# ------------------------------------------------------------
# source file   = NBTest_059_TestNetworkInfoMultichain.py
# test id       = 059
# test comment  = TestNetworkInfoMultichain
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot import Bot, Config
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.testing import *
from fastlane_bot.config.network import *
from typing import Dict
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)



cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="coinbase_base")


# ------------------------------------------------------------
# Test      059
# File      test_059_TestNetworkInfoMultichain.py
# Segment   Config_Test_Multichain
# ------------------------------------------------------------
def test_config_test_multichain():
# ------------------------------------------------------------
    
    assert cfg.RPC_ENDPOINT in "https://base-mainnet.g.alchemy.com/v2/", f"[TestGenerateNetworkInfo] Wrong RPC endpoint for coinbase_base. Expected: https://base-mainnet.g.alchemy.com/v2/, found {cfg.RPC_ENDPOINT}"
    assert cfg.NATIVE_GAS_TOKEN_ADDRESS in "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", f"[TestGenerateNetworkInfo] NATIVE_GAS_TOKEN_KEY for coinbase_base. Expected: 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE, found {cfg.NATIVE_GAS_TOKEN_ADDRESS}"
    assert cfg.WRAPPED_GAS_TOKEN_ADDRESS in "0x4200000000000000000000000000000000000006", f"[TestGenerateNetworkInfo] WRAPPED_GAS_TOKEN_KEY for coinbase_base. Expected: 0x4200000000000000000000000000000000000006, found {cfg.WRAPPED_GAS_TOKEN_ADDRESS}"
    assert cfg.STABLECOIN_ADDRESS in "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", f"[TestGenerateNetworkInfo] STABLECOIN_ADDRESS for coinbase_base. Expected: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913, found {cfg.STABLECOIN_ADDRESS}"
    

# ------------------------------------------------------------
# Test      059
# File      test_059_TestNetworkInfoMultichain.py
# Segment   Multichain_Tests
# ------------------------------------------------------------
def test_multichain_tests():
# ------------------------------------------------------------
    
    # +
    exchange_df = get_multichain_addresses('coinbase_base')
    
    fork_map = get_fork_map(df=exchange_df, fork_name="uniswap_v3")
    
    
    assert 'uniswap_v3' in fork_map, f"[TestGenerateNetworkInfo] Could not find uniswap_v3 in fork_map."
    assert 'sushiswap_v3' in fork_map, f"[TestGenerateNetworkInfo] Could not find sushiswap_v3 in fork_map."
    assert 'pancakeswap_v3' in fork_map, f"[TestGenerateNetworkInfo] Could not find pancakeswap_v3 in fork_map."
    assert 'baseswap_v3' in fork_map, f"[TestGenerateNetworkInfo] Could not find baseswap_v3 in fork_map."
    assert type(fork_map['uniswap_v3']) == str
    
    addr_row = get_row_from_address(address="0xBA12222222228d8Ba445958a75a0704d566BF2C8", df=exchange_df)
    assert type(addr_row) == pd.DataFrame
    assert type(addr_row['router_address'].values[0]) == str
    
    exchange = get_exchange_from_address(address="0xBA12222222228d8Ba445958a75a0704d566BF2C8", df=exchange_df)
    assert type(exchange) == str
    
    items_to_get = ["router_address", "exchange_name"]
    get_items_test_1 = (get_items_from_exchange(item_names=items_to_get, exchange_name="aerodrome_v2", fork="solidly_v2", df=exchange_df))
    assert len(items_to_get) == len(get_items_test_1)
    
    items_to_get_2 = ["router_address"]
    get_items_test_2 = (get_items_from_exchange(item_names=["router_address"], exchange_name="aerodrome_v2", fork="solidly_v2", df=exchange_df))
    assert len(items_to_get_2) == len(get_items_test_2)
    assert type(get_items_test_2[0]) == str
    
    get_router_for_ex_test = get_router_address_for_exchange(exchange_name="aerodrome_v2", fork="solidly_v2", df=exchange_df)
    assert type(get_router_for_ex_test) == str
    # -
    

# ------------------------------------------------------------
# Test      059
# File      test_059_TestNetworkInfoMultichain.py
# Segment   Test_default_fees_uni_v2_forks
# ------------------------------------------------------------
def test_test_default_fees_uni_v2_forks():
# ------------------------------------------------------------
    
    # +
    multichain_address_path = os.path.normpath(
            "fastlane_bot/data/multichain_addresses.csv"
        )
    chain_addresses_df = pd.read_csv(multichain_address_path)
    
    for idx, row in chain_addresses_df.iterrows():
        exchange_name = row["exchange_name"]
        fork = row["fork"]
        fee = row["fee"]
        if exchange_name in ["uniswap_v2", "sushiswap_v2"]:
            assert float(fee) == 0.003, f"[NBTest_059_TestNetworkInfoMultichain] Wrong default set for {exchange_name}. Expected 0.003, found {fee}"
        elif exchange_name in ["pancakeswap_v2"]:
            assert float(fee) == 0.0025, f"[NBTest_059_TestNetworkInfoMultichain] Wrong default set for {exchange_name}. Expected 0.0025, found {fee}"    
    # -
    
    