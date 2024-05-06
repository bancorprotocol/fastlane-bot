# ------------------------------------------------------------
# Auto generated test file `test_901_TestMultiTriangleModeSlow.py`
# ------------------------------------------------------------
# source file   = NBTest_901_TestMultiTriangleModeSlow.py
# test id       = 901
# test comment  = TestMultiTriangleModeSlow
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
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

arb_mode = "multi_triangle"


# ------------------------------------------------------------
# Test      901
# File      test_901_TestMultiTriangleModeSlow.py
# Segment   Test_min_profit
# ------------------------------------------------------------
def test_test_min_profit():
# ------------------------------------------------------------
    
    assert(cfg.DEFAULT_MIN_PROFIT_GAS_TOKEN <= 0.0001), f"[TestMultiTriangleMode], default_min_profit_gas_token must be <= 0.0001 for this Notebook to run, currently set to {cfg.DEFAULT_MIN_PROFIT_GAS_TOKEN}"
    
    # ### Test_arb_mode_class
    
    arb_finder = bot._get_arb_finder("multi_triangle")
    assert arb_finder.__name__ == "ArbitrageFinderTriangleMulti", f"[TestMultiTriangleMode] Expected arb_finder class name name = FindArbitrageMultiPairwise, found {arb_finder.__name__}"
    

# ------------------------------------------------------------
# Test      901
# File      test_901_TestMultiTriangleModeSlow.py
# Segment   Test_combos
# ------------------------------------------------------------
def test_test_combos():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("multi_triangle")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=arb_finder.AO_TOKENS,
                ConfigObj=bot.ConfigObj,
            )
    combos = finder.get_combos(flashloan_tokens=flashloan_tokens, CCm=CCm, arb_mode="multi_triangle")
    assert len(combos) >= 1225, f"[TestMultiTriangleMode] Using wrong dataset, expected at least 1225 combos, found {len(combos)}"
    
    # +
    # print(len(combos))
    # for ex in exchanges:
    #     count = 0
    #     for pool in CCm:
    #         if ex in pool.descr:
    #             count +=1
    #     print(f"found {count} pools for {ex}")
    # -
    
    # ### Test_find_arbitrage_single
    
    # +
    arb_finder = bot._get_arb_finder("multi_triangle")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=arb_finder.AO_CANDIDATES,
                ConfigObj=bot.ConfigObj,
            )
    r = finder.find_arbitrage()
    multi_carbon_count = 0
    for arb in r:
        (
                best_profit,
                best_trade_instructions_df,
                best_trade_instructions_dic,
                best_src_token,
                best_trade_instructions,
            ) = arb
        if len(best_trade_instructions_dic) > 3:
            multi_carbon_count += 1
            tkn_in = None
            tkn_out = None
            # Find the first Carbon Curve to establish tknin and tknout
            for curve in best_trade_instructions_dic:
                if "-0" in curve['cid'] or "-1" in curve['cid']:
                    tkn_in = curve["tknin"]
                    tknout = curve["tknout"]
                    break
            for curve in best_trade_instructions_dic:
                if "-0" in curve['cid'] or "-1" in curve['cid']:
                    if curve["tknin"] in [tkn_in, tkn_out] and curve["tknout"] in [tkn_in, tkn_out]:
                        assert curve["tknin"] in tkn_in, f"[TestMultiTriangleMode] Finding Carbon curves in opposite directions - not supported in this mode."
                        assert curve["tknout"] in tkn_out, f"[TestMultiTriangleMode] Finding Carbon curves in opposite directions - not supported in this mode."
    
    assert multi_carbon_count > 0, f"[TestMultiTriangleMode] Not finding arbs with multiple Carbon curves."
    assert len(r) >= 58, f"[TestMultiTriangleMode] Expected at least 58 arbs, found {len(r)}"
    # -
    

# ------------------------------------------------------------
# Test      901
# File      test_901_TestMultiTriangleModeSlow.py
# Segment   Test Triangle Single
# ------------------------------------------------------------
def test_test_triangle_single():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("triangle")
    assert arb_finder.__name__ == "ArbitrageFinderTriangleSingle", f"[TestMultiTriangleMode] Expected arb_finder class name name = ArbitrageFinderTriangleSingle, found {arb_finder.__name__}"
    

# ------------------------------------------------------------
# Test      901
# File      test_901_TestMultiTriangleModeSlow.py
# Segment   Test_combos_triangle_single
# ------------------------------------------------------------
def test_test_combos_triangle_single():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("triangle")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=arb_finder.AO_TOKENS,
                ConfigObj=bot.ConfigObj,
            )
    combos = finder.get_combos(flashloan_tokens=flashloan_tokens, CCm=CCm, arb_mode="multi_triangle")
    assert len(combos) >= 1225, f"[TestMultiTriangleMode] Using wrong dataset, expected at least 1225 combos, found {len(combos)}"
    

# ------------------------------------------------------------
# Test      901
# File      test_901_TestMultiTriangleModeSlow.py
# Segment   Test_Find_Arbitrage_Single
# ------------------------------------------------------------
def test_test_find_arbitrage_single():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("triangle")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=arb_finder.AO_CANDIDATES,
                ConfigObj=bot.ConfigObj,
            )
    r = finder.find_arbitrage()
    multi_carbon_count = 0
    for arb in r:
        (
                best_profit,
                best_trade_instructions_df,
                best_trade_instructions_dic,
                best_src_token,
                best_trade_instructions,
            ) = arb
        if len(best_trade_instructions_dic) > 3:
            multi_carbon_count += 1
            tkn_in = None
            tkn_out = None
            # Find the first Carbon Curve to establish tknin and tknout
            for curve in best_trade_instructions_dic:
                if "-0" in curve['cid'] or "-1" in curve['cid']:
                    tkn_in = curve["tknin"]
                    tknout = curve["tknout"]
                    break
            for curve in best_trade_instructions_dic:
                if "-0" in curve['cid'] or "-1" in curve['cid']:
                    if curve["tknin"] in [tkn_in, tkn_out] and curve["tknout"] in [tkn_in, tkn_out]:
                        assert curve["tknin"] in tkn_in, f"[TestMultiTriangleMode] Finding Carbon curves in opposite directions - not supported in this mode."
                        assert curve["tknout"] in tkn_out, f"[TestMultiTriangleMode] Finding Carbon curves in opposite directions - not supported in this mode."
    
    assert multi_carbon_count == 0, f"[TestMultiTriangleMode] Expected 0 arbs with multiple Carbon curves for Triangle Single mode, found {multi_carbon_count}."
    assert len(r) >= 58, f"[TestMultiTriangleMode] Expected at least 58 arbs, found {len(r)}"
    # -
    
    