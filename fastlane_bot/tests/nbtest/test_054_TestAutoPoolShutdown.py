# ------------------------------------------------------------
# Auto generated test file `test_054_TestAutoPoolShutdown.py`
# ------------------------------------------------------------
# source file   = NBTest_054_TestAutoPoolShutdown.py
# test id       = 054
# test comment  = TestAutoPoolShutdown
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
from fastlane_bot.helpers import TradeInstruction, TxReceiptHandler, TxRouteHandler, TxSubmitHandler, TxHelpers, TxHelper
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.tools.pool_shutdown import AutomaticPoolShutdown
from joblib import Parallel, delayed
import pytest
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
C.DEFAULT_MIN_PROFIT_BNT = 0.02
C.DEFAULT_MIN_PROFIT = 0.02
cfg.DEFAULT_MIN_PROFIT_BNT = 0.02
cfg.DEFAULT_MIN_PROFIT = 0.02
assert (C.NETWORK == C.NETWORK_MAINNET)
assert (C.PROVIDER == C.PROVIDER_ALCHEMY)
setup_bot = CarbonBot(ConfigObj=C)
pools = None
with open('fastlane_bot/data/tests/latest_pool_data_testing_save.json') as f:
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



pool_shutdown = AutomaticPoolShutdown(mgr=mgr, polling_interval=12)


# ------------------------------------------------------------
# Test      054
# File      test_054_TestAutoPoolShutdown.py
# Segment   Test White List
# ------------------------------------------------------------
def test_test_white_list():
# ------------------------------------------------------------
    
    assert len(pool_shutdown.shutdown_whitelist) > 0, f"[NB054 Automatic Shutdown] failed to retrieve pool whitelist"
    

# ------------------------------------------------------------
# Test      054
# File      test_054_TestAutoPoolShutdown.py
# Segment   Test parse_active_pools
# ------------------------------------------------------------
def test_test_parse_active_pools():
# ------------------------------------------------------------
    
    # +
    pool_shutdown.parse_active_pools()
    
    for pool in pool_shutdown.active_pools:
        assert type(pool_shutdown.active_pools[pool]) == int
        assert pool_shutdown.active_pools[pool] >= 0
    # -
    

# ------------------------------------------------------------
# Test      054
# File      test_054_TestAutoPoolShutdown.py
# Segment   Test iterate_active_pools
# ------------------------------------------------------------
def test_test_iterate_active_pools():
# ------------------------------------------------------------
    
    # +
    ETH = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    pool_shutdown.active_pools = {}
    pool_shutdown.active_pools[ETH] = 100000000000000000
    tkn = pool_shutdown.iterate_active_pools()
    
    assert tkn == ETH
    # -
    

# ------------------------------------------------------------
# Test      054
# File      test_054_TestAutoPoolShutdown.py
# Segment   Test iterate_active_pools_two
# ------------------------------------------------------------
def test_test_iterate_active_pools_two():
# ------------------------------------------------------------
    
    # +
    ETH = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    pool_shutdown.active_pools = {}
    pool_shutdown.active_pools[ETH] = 100000000000000000000000
    tkn = pool_shutdown.iterate_active_pools()
    
    assert tkn == None
    # -
    
    