# ------------------------------------------------------------
# Auto generated test file `test_059_PoolAndTokens.py`
# ------------------------------------------------------------
# source file   = NBTest_059_PoolAndTokens.py
# test id       = 059
# test comment  = PoolAndTokens
# ------------------------------------------------------------


"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Config
from fastlane_bot.helpers.poolandtokens import PoolAndTokens

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(PoolAndTokens))

from json import loads, dumps
from fastlane_bot.testing import *

from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

cfg = Config.new(config=Config.CONFIG_MAINNET)

# ------------------------------------------------------------
# Test      059
# File      test_059_PoolAndTokens.py
# Segment   Test_PoolAndTokens_Carbon
# ------------------------------------------------------------
def test_test_poolandtokens_carbon():
# ------------------------------------------------------------
    with open("fastlane_bot/tests/_data/test_strategies.json", "r") as f:
        for strategy in loads(f.read()):
            pool_and_tokens = PoolAndTokens(
                ConfigObj=cfg,
                id=0,
                cid="",
                strategy_id=0,
                last_updated="",
                last_updated_block=0,
                descr="",
                pair_name="tkn0/tkn1",
                exchange_name="",
                fee=Decimal(0),
                fee_float=0,
                tkn0_balance=Decimal(0),
                tkn1_balance=Decimal(0),
                y_0=strategy["orders"][0]["y"],
                z_0=strategy["orders"][0]["z"],
                A_0=strategy["orders"][0]["A"],
                B_0=strategy["orders"][0]["B"],
                y_1=strategy["orders"][1]["y"],
                z_1=strategy["orders"][1]["z"],
                A_1=strategy["orders"][1]["A"],
                B_1=strategy["orders"][1]["B"],
                sqrt_price_q96=Decimal(0),
                tick=0,
                tick_spacing=0,
                liquidity=Decimal(0),
                address="",
                anchor="",
                tkn0="",
                tkn1="",
                tkn0_address="",
                tkn1_address="",
                tkn0_decimals=strategy["tkn0_decimals"],
                tkn1_decimals=strategy["tkn1_decimals"],
            )
            cpc_dict = pool_and_tokens._carbon_to_cpc_dict()
            for key in ["pm_within_range", "no_limit_orders", "prices_overlap"]:
                assert cpc_dict[key] == strategy[key], f"expected {key}={strategy[key]}, got {key}={cpc_dict[key]}: {dumps(strategy, indent=4)}"
