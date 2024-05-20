# ------------------------------------------------------------
# Auto generated test file `test_042_TestBancorV3ModeTwoHop.py`
# ------------------------------------------------------------
# source file   = NBTest_042_TestBancorV3ModeTwoHop.py
# test id       = 042
# test comment  = TestBancorV3ModeTwoHop
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.helpers import TxRouteHandler
from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.events.managers.manager import Manager
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
#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)



C = cfg = Config.new(config=Config.CONFIG_MAINNET)
cfg.DEFAULT_MIN_PROFIT_GAS_TOKEN = 0.00001
assert (C.NETWORK == C.NETWORK_MAINNET)
assert (C.PROVIDER == C.PROVIDER_ALCHEMY)
setup_bot = CarbonBot(ConfigObj=C)
pools = None
with open('fastlane_bot/tests/_data/latest_pool_data_testing.json') as f:
    pools = json.load(f)
pools = [pool for pool in pools]
pools[0]
static_pools = pools
state = pools
exchanges = list({ex['exchange_name'] for ex in state})
db = QueryInterface(state=state, ConfigObj=C, exchanges=exchanges)
setup_bot.db = db

static_pool_data_filename = "static_pool_data"

static_pool_data = pd.read_csv(f"fastlane_bot/data/{static_pool_data_filename}.csv", low_memory=False)
    
uniswap_v2_event_mappings = pd.read_csv("fastlane_bot/data/uniswap_v2_event_mappings.csv", low_memory=False)
        
tokens = pd.read_csv("fastlane_bot/data/tokens.csv", low_memory=False)
        
exchanges = "carbon_v1,bancor_v3,uniswap_v3,uniswap_v2,sushiswap_v2"

exchanges = exchanges.split(",")


alchemy_max_block_fetch = 20
static_pool_data["cid"] = [
        cfg.w3.keccak(text=f"{row['descr']}").hex()
        for index, row in static_pool_data.iterrows()
    ]
static_pool_data = [
    row for index, row in static_pool_data.iterrows()
    if row["exchange_name"] in exchanges
]

static_pool_data = pd.DataFrame(static_pool_data)
static_pool_data['exchange_name'].unique()
mgr = Manager(
    web3=cfg.w3,
    w3_async=cfg.w3_async,
    cfg=cfg,
    pool_data=static_pool_data.to_dict(orient="records"),
    SUPPORTED_EXCHANGES=exchanges,
    alchemy_max_block_fetch=alchemy_max_block_fetch,
    uniswap_v2_event_mappings=uniswap_v2_event_mappings,
    tokens=tokens.to_dict(orient="records"),
)

start_time = time.time()
Parallel(n_jobs=-1, backend="threading")(
    delayed(mgr.add_pool_to_exchange)(row) for row in mgr.pool_data
)
cfg.logger.info(f"Time taken to add initial pools: {time.time() - start_time}")

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
bot.db.remove_unmapped_uniswap_v2_pools()
bot.db.remove_zero_liquidity_pools()
bot.db.remove_unsupported_exchanges()
tokens = bot.db.get_tokens()
ADDRDEC = {t.address: (t.address, int(t.decimals)) for t in tokens if not math.isnan(t.decimals)}
flashloan_tokens = bot.RUN_FLASHLOAN_TOKENS
CCm = bot.get_curves()
pools = db.get_pool_data_with_tokens()


# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_min_profit
# ------------------------------------------------------------
def test_test_min_profit():
# ------------------------------------------------------------
    
    assert(cfg.DEFAULT_MIN_PROFIT_GAS_TOKEN <= 0.0001), f"[test_bancor_v3_two_hop], default_min_profit_gas_token must be <= 0.0001 for this Notebook to run, currently set to {cfg.DEFAULT_MIN_PROFIT_GAS_TOKEN}"
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_Trade_Merge
# ------------------------------------------------------------
def test_test_trade_merge():
# ------------------------------------------------------------
    
    arb_finder = bot.get_arb_finder("b3_two_hop", flashloan_tokens=flashloan_tokens, CCm=CCm)
    arb_opp = arb_finder.find_arb_opps()[0]

    src_token = arb_opp["src_token"]
    trade_instructions_dic = arb_opp["trade_instructions_dic"]

    ordered_trade_instructions_dct = bot._simple_ordering_by_src_token(trade_instructions_dic, src_token)

    ordered_scaled_dcts = bot._basic_scaling(ordered_trade_instructions_dct, src_token)
    # Convert the trade instructions
    ordered_trade_instructions_objects = bot._convert_trade_instructions(ordered_scaled_dcts)
    tx_route_handler = TxRouteHandler(trade_instructions=ordered_trade_instructions_objects)
    agg_trade_instructions = (
        tx_route_handler.aggregate_carbon_trades(ordered_trade_instructions_objects)
        if any(trade.is_carbon for trade in ordered_trade_instructions_objects)
        else ordered_trade_instructions_objects
    )
    # Calculate the trade instructions
    calculated_trade_instructions = tx_route_handler.calculate_trade_outputs(agg_trade_instructions)
    assert len(calculated_trade_instructions) == 3
    # Aggregate multiple Bancor V3 trades into a single trade
    calculated_trade_instructions = tx_route_handler.aggregate_bancor_v3_trades(calculated_trade_instructions)
    assert len(calculated_trade_instructions) == 2
    assert calculated_trade_instructions[0].tknin != "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    assert calculated_trade_instructions[0].tknout != "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_get_combos
# ------------------------------------------------------------
def test_test_get_combos():
# ------------------------------------------------------------
    
    arb_finder = bot.get_arb_finder(
        arb_mode = "b3_two_hop",
        flashloan_tokens = {
            "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "0x514910771AF9Ca656af840dff83E8264EcF986CA"
        },
        CCm = CCm
    )
    combos = arb_finder.get_combos()
    assert len(combos) >= 6, f"[test_bancor_v3_two_hop] Different data used for tests, expected 6 combos, found {len(combos)}"
