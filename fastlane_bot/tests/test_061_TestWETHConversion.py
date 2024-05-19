# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# coding=utf-8
"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot
from fastlane_bot.bot import CarbonBot
from fastlane_bot.helpers import TxRouteHandler
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, CarbonV1, BancorV3

from fastlane_bot.utils import num_format
from fastlane_bot.helpers import add_wrap_or_unwrap_trades_to_route, split_carbon_trades
from fastlane_bot.events.managers.manager import Manager
from dataclasses import asdict
from fastlane_bot.config import Config
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.interface import QueryInterface
from joblib import Parallel, delayed
import math
import json

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

# plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12, 6]
from fastlane_bot import __VERSION__

require("3.0", __VERSION__)

# +
C = cfg = Config.new(config=Config.CONFIG_MAINNET, )  # blockchain="coinbase_base")
C.DEFAULT_MIN_PROFIT_GAS_TOKEN = 0.0001

setup_bot = CarbonBot(ConfigObj=C)
pools = None

###
"""
Put path to log file here >>>
"""
###

with open("fastlane_bot/tests/_data/latest_pool_data_testing.json") as f:
    pools = json.load(f)

flashloan_tokens = ["0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0x514910771AF9Ca656af840dff83E8264EcF986CA"]
# flashloan_tokens = ["WETH-0006,USDC-2913"]

pools = [pool for pool in pools]
static_pools = pools
state = pools
exchanges = list({ex['exchange_name'] for ex in state})
db = QueryInterface(state=state, ConfigObj=C, exchanges=exchanges)
setup_bot.db = db

static_pool_data_filename = "static_pool_data"

static_pool_data = pd.read_csv(f"fastlane_bot/data/{static_pool_data_filename}.csv", low_memory=False)

uniswap_v2_event_mappings = pd.read_csv("fastlane_bot/data/uniswap_v2_event_mappings.csv", low_memory=False)
uniswap_v3_event_mappings = pd.read_csv("fastlane_bot/data/uniswap_v3_event_mappings.csv", low_memory=False)

tokens = pd.read_csv("fastlane_bot/data/tokens.csv", low_memory=False)

exchanges = "carbon_v1,pancakeswap_v2,pancakeswap_v3,uniswap_v2,uniswap_v3"

exchanges = exchanges.split(",")

alchemy_max_block_fetch = 20
static_pool_data["cid"] = [
    cfg.w3.keccak(text=f"{row['descr']}").hex()
    for index, row in static_pool_data.iterrows()
]
# Filter out pools that are not in the supported exchanges
static_pool_data = [
    row for index, row in static_pool_data.iterrows()
    if row["exchange_name"] in exchanges
]

static_pool_data = pd.DataFrame(static_pool_data)
static_pool_data['exchange_name'].unique()
# Initialize data fetch manager
mgr = Manager(
    web3=cfg.w3,
    w3_async=cfg.w3_async,
    cfg=cfg,
    pool_data=static_pool_data.to_dict(orient="records"),
    SUPPORTED_EXCHANGES=exchanges,
    alchemy_max_block_fetch=alchemy_max_block_fetch,
    uniswap_v2_event_mappings=uniswap_v2_event_mappings,
    uniswap_v3_event_mappings=uniswap_v3_event_mappings,
    tokens=tokens.to_dict(orient="records"),
)

# Add initial pools for each row in the static_pool_data
start_time = time.time()
Parallel(n_jobs=-1, backend="threading")(
    delayed(mgr.add_pool_to_exchange)(row) for row in mgr.pool_data
)
cfg.logger.info(f"Time taken to add initial pools: {time.time() - start_time}")

# check if any duplicate cid's exist in the pool data
mgr.deduplicate_pool_data()
cids = [pool["cid"] for pool in mgr.pool_data]
assert len(cids) == len(set(cids)), "duplicate cid's exist in the pool data"


def init_bot(mgr: Manager) -> CarbonBot:
    """
    Initializes the bot.

    Parameters
    ----------
    mgr : Manager
        The manager object.

    Returns
    -------
    CarbonBot
        The bot object.
    """
    mgr.cfg.logger.info("Initializing the bot...")
    bot = CarbonBot(ConfigObj=mgr.cfg)
    bot.db = db
    bot.db.mgr = mgr
    assert isinstance(
        bot.db, QueryInterface
    ), "QueryInterface not initialized correctly"
    return bot


bot = init_bot(mgr)
# add data cleanup steps from main.py
# bot.db.remove_unmapped_uniswap_v2_pools()
bot.db.remove_zero_liquidity_pools()
# bot.db.remove_unsupported_exchanges()
tokens = bot.db.get_tokens()
ADDRDEC = {t.address: (t.address, int(t.decimals)) for t in tokens if not math.isnan(t.decimals)}
# flashloan_tokens = bot.RUN_FLASHLOAN_TOKENS
# flashloan_tokens = ['WBTC-2c599', 'USDC-eB48', 'LINK-86CA', 'USDT-1ec7']


CCm = bot.get_curves()
pools = db.get_pool_data_with_tokens()

# -

# # Test Native Gas Token Wrap Unwrap [NB061]

# ## Test_Wrap_Unwrap_Gas_Token_In_Route_Struct

# +
arb_mode = "multi_pairwise_all"

# -
def test_wrap_unwrap_original():
    arb_finder = bot._get_arb_finder(arb_mode)
    finder = arb_finder(flashloan_tokens=flashloan_tokens, CCm=CCm, ConfigObj=bot.ConfigObj)

    for arb_opp in finder.find_arb_opps():
        (
            profit,
            trade_instructions_df,
            trade_instructions_dic,
            src_token,
            trade_instructions
        ) = arb_opp

        # Order the trade instructions
        (
            ordered_trade_instructions_dct,
            tx_in_count
        ) = bot._simple_ordering_by_src_token(trade_instructions_dic, src_token)

        # Scale the trade instructions
        ordered_scaled_dcts = bot._basic_scaling(ordered_trade_instructions_dct, src_token)

        # Convert the trade instructions
        ordered_trade_instructions_objects = bot._convert_trade_instructions(ordered_scaled_dcts)

        # Create the tx route handler
        tx_route_handler = TxRouteHandler(trade_instructions=ordered_trade_instructions_objects)

        # Aggregate the carbon trades
        agg_trade_instructions = (
            tx_route_handler.aggregate_carbon_trades(ordered_trade_instructions_objects)
            if bot._carbon_in_trade_route(ordered_trade_instructions_objects)
            else ordered_trade_instructions_objects
        )

        # Calculate the trade instructions
        calculated_trade_instructions = tx_route_handler.calculate_trade_outputs(trade_instructions=agg_trade_instructions)

        # Aggregate multiple Bancor V3 trades into a single trade
        calculated_trade_instructions = tx_route_handler.aggregate_bancor_v3_trades(calculated_trade_instructions)
        flashloan_struct = tx_route_handler.generate_flashloan_struct(trade_instructions_objects=calculated_trade_instructions)

        # Get the flashloan token
        fl_token = calculated_trade_instructions[0].tknin_address
        fl_token_symbol = calculated_trade_instructions[0].tknin_symbol

        best_profit = flashloan_tkn_profit = tx_route_handler.calculate_trade_profit(calculated_trade_instructions)

        # Calculate the best profit
        best_profit_fl_token, best_profit_gastkn, best_profit_usd = bot.calculate_profit(CCm, best_profit, fl_token)

        # Log the best profit
        cfg.logger.info(f"Updated best_profit after calculating exact trade numbers: {num_format(best_profit_gastkn)}")

        # Calculate the arbitrage
        arb = bot.calculate_arb(
            arb_mode,
            best_profit_gastkn,
            best_profit_usd,
            flashloan_tkn_profit,
            calculated_trade_instructions,
            fl_token_symbol,
        )

        # Log the arbitrage
        cfg.logger.info(f"calculated arb: {arb}")

        # Get the flashloan amount
        flashloan_amount = int(calculated_trade_instructions[0].amtin_wei)

        # Log the flashloan amount
        cfg.logger.info(f"Flashloan amount: {flashloan_amount}")

        split_trades = split_carbon_trades(cfg, calculated_trade_instructions)

        # Encode the trade instructions
        encoded_trade_instructions = tx_route_handler.custom_data_encoder(
            split_trades
        )

        # Get the deadline
        deadline = bot._get_deadline(None)

        # Get the route struct
        route_struct = [
            asdict(rs)
            for rs in tx_route_handler.get_route_structs(
                encoded_trade_instructions, deadline
            )
        ]

        # Check if the result is None
        wrap_route_struct = add_wrap_or_unwrap_trades_to_route(cfg, flashloan_struct, route_struct, calculated_trade_instructions)

        assert flashloan_struct[0]["sourceTokens"][0] == wrap_route_struct[0]["sourceToken"]
        assert flashloan_struct[0]["sourceTokens"][0] == wrap_route_struct[-1]["targetToken"]

        for idx in range(1, len(wrap_route_struct)):
            assert wrap_route_struct[idx]["sourceToken"] == wrap_route_struct[idx - 1]["targetToken"]
