# ------------------------------------------------------------
# Auto generated test file `test_058_BalancerIntegration.py`
# ------------------------------------------------------------
# source file   = NBTest_058_BalancerIntegration.py
# test id       = 058
# test comment  = BalancerIntegration
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.events.exchanges.balancer import Balancer
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers import TradeInstruction, TxRouteHandler
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
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Balancer))

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

pool_data_raw = [pool for pool in pools]
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

exchanges = "carbon_v1,bancor_v3,uniswap_v3,uniswap_v2,sushiswap_v2,bancor_pol,bancor_v2,balancer"

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
#bot.db.remove_unmapped_uniswap_v2_pools()
bot.db.remove_zero_liquidity_pools()
bot.db.remove_unsupported_exchanges()
tokens = bot.db.get_tokens()
ADDRDEC = {t.address: (t.address, int(t.decimals)) for t in tokens if not math.isnan(t.decimals)}
flashloan_tokens = bot.RUN_FLASHLOAN_TOKENS
CCm = bot.get_curves()
pools = db.get_pool_data_with_tokens()


# ------------------------------------------------------------
# Test      058
# File      test_058_BalancerIntegration.py
# Segment   Test_PoolAndTokens_Balancer
# ------------------------------------------------------------
def test_test_poolandtokens_balancer():
# ------------------------------------------------------------
    
    
    
    # +
    pool0 = [pool for pool in pool_data_raw if pool['cid'] == '0x157a028048d6012956119dab5126fc0507c03cfb67a9cb88f309d3380e2cab4c'][0]
    pool1 = [pool for pool in pool_data_raw if pool['cid'] == '0xba841adabcc7402bf7410b86b86d3941171b4178df699611eda851e12ed0fe10'][0]
    
    pool0_processed = db.create_pool_and_tokens(idx=0, record=pool0)
    pool1_processed = db.create_pool_and_tokens(idx=1, record=pool1)
    
    
    
    
    # Test PoolandToken creation
    assert pool0_processed.exchange_name == "balancer", f"[NB058 BalancerIntegration] wrong dataset, pool exchange_name expected to be balancer, found {pool0_processed.exchange_name}"
    assert len(pool0_processed.tokens) == 2, f"[NB058 BalancerIntegration] wrong dataset, expected pool to contain 2 tokens, found {len(pool0_processed.tokens)}"
    assert len(pool0_processed.token_weights) == 2, f"[NB058 BalancerIntegration] wrong dataset, expected pool to contain 2 token weights, found {len(pool0_processed.token_weights)}"
    assert len(pool0_processed.token_decimals) == len(pool0_processed.token_weights) and len(pool0_processed.tokens) == len(pool0_processed.token_weights) and len(pool0_processed.token_weights) == len(pool0_processed.token_balances), f"[NB058 BalancerIntegration] issue with pool creation, should have the same number of tokens, weights, decimals, and balances. Found {len(pool0_processed.token_decimals)}"
    
    assert pool1_processed.exchange_name == "balancer", f"[NB058 BalancerIntegration] wrong dataset, pool exchange_name expected to be balancer, found {pool1_processed.exchange_name}"
    assert len(pool1_processed.tokens) == 5, f"[NB058 BalancerIntegration] wrong dataset, expected pool to contain 5 tokens, found {len(pool1_processed.tokens)}"
    assert len(pool1_processed.token_weights) == 5, f"[NB058 BalancerIntegration] wrong dataset, expected pool to contain 5 token weights, found {len(pool1_processed.token_weights)}"
    
    assert len(pool1_processed.token_decimals) == len(pool1_processed.token_weights) and len(pool1_processed.tokens) == len(pool1_processed.token_weights) and len(pool1_processed.token_weights) == len(pool1_processed.token_balances), f"[NB058 BalancerIntegration] issue with pool creation, should have the same number of tokens, weights, decimals, and balances. Found {len(pool1_processed.token_decimals)}"
    
    assert type(pool1_processed.get_token_balance('0x5f98805A4E8be255a32880FDeC7F6728C6568bA0')) == float or int, f"[NB058 BalancerIntegration] wrong type for get_token_balance, expected float or int, found {type(pool1_processed.get_token_balance('0x5f98805A4E8be255a32880FDeC7F6728C6568bA0'))}"
    assert type(pool1_processed.get_token_weight('0x5f98805A4E8be255a32880FDeC7F6728C6568bA0')) == float, f"[NB058 BalancerIntegration] wrong type for get_token_weight, expected float, found  {type(pool1_processed.get_token_weight('0x5f98805A4E8be255a32880FDeC7F6728C6568bA0'))}"
    assert pool1_processed.get_token_decimals('0x5f98805A4E8be255a32880FDeC7F6728C6568bA0') == 18, f"[NB058 BalancerIntegration] wrong token weight found for 0x5f98805A4E8be255a32880FDeC7F6728C6568bA0, expected 18, found {pool1_processed.get_token_decimals('0x5f98805A4E8be255a32880FDeC7F6728C6568bA0')}"
    
    
    # -
    
    # ### Test_toCPC_Balancer
    
    # +
    pool0_to_cpc = pool0_processed.to_cpc()
    pool1_to_cpc = pool1_processed.to_cpc()
    
    assert len(pool0_to_cpc) == 1, f"[NB058 BalancerIntegration] wrong number of pools, expected pool CPC to produce 1 CPC curve, found {len(pool0_to_cpc)}"
    assert len(pool1_to_cpc) == 10, f"[NB058 BalancerIntegration] wrong number of pools, expected pool CPC to produce 10 CPC curves, found {len(pool1_to_cpc)}"
    
    assert pool0_to_cpc[0].constr == "xyal", f"[NB058 BalancerIntegration] wrong pool constraint, expected 'xyal', found {pool0_to_cpc[0].constr}"
    assert pool0_to_cpc[0].alpha < 1 and pool0_to_cpc[0].alpha > 0, f"[NB058 BalancerIntegration] pool alpha must be between 0 and 1, found {pool0_to_cpc[0].alpha}"
    for pool in pool1_to_cpc:
        assert pool.constr == "xyal", f"[NB058 BalancerIntegration] wrong pool constraint, expected 'xyal', found {pool.constr}"
        assert pool.alpha < 1 and pool.alpha > 0, f"[NB058 BalancerIntegration] pool alpha must be between 0 and 1, found {pool.alpha}"
    
    # -
    

# ------------------------------------------------------------
# Test      058
# File      test_058_BalancerIntegration.py
# Segment   Test_TxRouteHandler_Balancer
# ------------------------------------------------------------
def test_test_txroutehandler_balancer():
# ------------------------------------------------------------
    
    # +
    pool0 = [pool for pool in pool_data_raw if pool['cid'] == '0x157a028048d6012956119dab5126fc0507c03cfb67a9cb88f309d3380e2cab4c'][0]
    pool1 = [pool for pool in pool_data_raw if pool['cid'] == '0xba841adabcc7402bf7410b86b86d3941171b4178df699611eda851e12ed0fe10'][0]
    
    pool0_processed = db.create_pool_and_tokens(idx=0, record=pool0)
    pool1_processed = db.create_pool_and_tokens(idx=1, record=pool1)
    
    pool0_to_cpc = pool0_processed.to_cpc()
    pool1_to_cpc = pool1_processed.to_cpc()
    
    ti1 = TradeInstruction(
        cid='0x157a028048d6012956119dab5126fc0507c03cfb67a9cb88f309d3380e2cab4c',
        tknin='0x5f98805A4E8be255a32880FDeC7F6728C6568bA0',
        amtin=100,
        tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtout=1,
        ConfigObj=cfg,
        db = db,
    )
    
    ti2 = TradeInstruction(
        cid='0xba841adabcc7402bf7410b86b86d3941171b4178df699611eda851e12ed0fe10',
        tknin='0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        amtin=1,
        tknout='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        amtout=5005,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  8,
        tknin_dec_override = 6,
        tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tknin_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'carbon_v1'
    )
    
    instructions = [ti1, ti2]
    
    
    route_handler = TxRouteHandler(instructions)
    
    
    assert not raises(route_handler._calc_balancer_output, curve=pool1_processed, tkn_in='0x5f98805A4E8be255a32880FDeC7F6728C6568bA0', tkn_out='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', amount_in=Decimal("10000")), f"[NB058 BalancerIntegration] should not raise an error"
    assert raises(route_handler._calc_balancer_output, curve=pool1_processed, tkn_in='0x5f98805A4E8be255a32880FDeC7F6728C6568bA0', tkn_out='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', amount_in=Decimal("100000000000")), f"[NB058 BalancerIntegration] expected BalancerInputTooLargeError error"
    # -
    
    
    