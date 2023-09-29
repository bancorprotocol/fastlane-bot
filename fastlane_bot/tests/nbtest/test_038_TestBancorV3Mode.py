# ------------------------------------------------------------
# Auto generated test file `test_038_TestBancorV3Mode.py`
# ------------------------------------------------------------
# source file   = NBTest_038_TestBancorV3Mode.py
# test id       = 038
# test comment  = TestBancorV3Mode
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, SushiswapV2, CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
from fastlane_bot.helpers import TradeInstruction, TxReceiptHandler, TxRouteHandler, TxSubmitHandler, TxHelpers, TxHelper
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.events.interface import QueryInterface
from joblib import Parallel, delayed
import pytest
import math
import json
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *
from fastlane_bot.modes import triangle_single_bancor3
#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)



C = cfg = Config.new(config=Config.CONFIG_MAINNET)
C.DEFAULT_MIN_PROFIT_BNT = 50
C.DEFAULT_MIN_PROFIT = 50
cfg.DEFAULT_MIN_PROFIT_BNT = 50
cfg.DEFAULT_MIN_PROFIT = 50
assert (C.NETWORK == C.NETWORK_MAINNET)
assert (C.PROVIDER == C.PROVIDER_ALCHEMY)
setup_bot = CarbonBot(ConfigObj=C)
pools = None
with open('fastlane_bot/data/tests/latest_pool_data_testing.json') as f:
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
bot = init_bot(mgr)
bot.db.handle_token_key_cleanup()
bot.db.remove_unmapped_uniswap_v2_pools()
bot.db.remove_zero_liquidity_pools()
bot.db.remove_unsupported_exchanges()
tokens = bot.db.get_tokens()
ADDRDEC = {t.key: (t.address, int(t.decimals)) for t in tokens if not math.isnan(t.decimals)}
flashloan_tokens = bot.setup_flashloan_tokens(None)
CCm = bot.setup_CCm(None)
pools = db.get_pool_data_with_tokens()

arb_mode = "bancor_v3"

#single = bot._run(flashloan_tokens=flashloan_tokens, CCm=CCm, arb_mode=arb_mode, data_validator=False, result="calc_trade_instr")

arb_finder = bot._get_arb_finder("bancor_v3")
finder = arb_finder(
            flashloan_tokens=flashloan_tokens,
            CCm=CCm,
            mode="bothin",
            result=False,
            ConfigObj=bot.ConfigObj,
        )
r = finder.find_arbitrage()
(
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = r
(
ordered_trade_instructions_dct,
tx_in_count,
) = bot._simple_ordering_by_src_token(
best_trade_instructions_dic, best_src_token
)


arb_finder = bot._get_arb_finder("bancor_v3")
finder = arb_finder(
            flashloan_tokens=flashloan_tokens,
            CCm=CCm,
            mode="bothin",
            result=False,
            ConfigObj=bot.ConfigObj,
        )
r = finder.find_arbitrage()
(
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = r
(
ordered_trade_instructions_dct,
tx_in_count,
) = bot._simple_ordering_by_src_token(
best_trade_instructions_dic, best_src_token
)
pool_cids = [curve['cid'] for curve in ordered_trade_instructions_dct]
first_check_pools = finder.get_exact_pools(pool_cids)

assert(len(first_check_pools) == 3), f"[test_bancor_v3] Validation expected 3 pools, got {len(first_check_pools)}"
for pool in first_check_pools:
    assert type(pool) == ConstantProductCurve, f"[test_bancor_v3] Validation pool type mismatch, got {type(pool)} expected ConstantProductCurve"
    assert pool.cid in pool_cids, f"[test_bancor_v3] Validation missing pool.cid {pool.cid} in {pool_cids}"
optimal_arb = finder.get_optimal_arb_trade_amts(pool_cids, 'BNT-FF1C')
assert type(optimal_arb) == float, f"[test_bancor_v3] Optimal arb calculation type is {type(optimal_arb)} not float"
assert iseq(optimal_arb, 4051.1611717583105), f"[test_bancor_v3] Optimal arb calculation type is {optimal_arb}, expected 4051.1611717583105"

# ------------------------------------------------------------
# Test      038
# File      test_038_TestBancorV3Mode.py
# Segment   Test_max_arb_trade_in_constant_product
# ------------------------------------------------------------
def test_test_max_arb_trade_in_constant_product():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("bancor_v3")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=False,
                ConfigObj=bot.ConfigObj,
            )
    r = finder.find_arbitrage()
    (
                best_profit,
                best_trade_instructions_df,
                best_trade_instructions_dic,
                best_src_token,
                best_trade_instructions,
            ) = r
    (
    ordered_trade_instructions_dct,
    tx_in_count,
    ) = bot._simple_ordering_by_src_token(
    best_trade_instructions_dic, best_src_token
    )
    pool_cids = [curve['cid'] for curve in ordered_trade_instructions_dct]
    first_check_pools = finder.get_exact_pools(pool_cids)
    
    flt='BNT-FF1C'
    
    tkn0 = finder.get_tkn(pool=first_check_pools[0], tkn_num=0)
    tkn1 = finder.get_tkn(pool=first_check_pools[0], tkn_num=1)
    tkn2 = finder.get_tkn(pool=first_check_pools[1], tkn_num=0)
    tkn5 = finder.get_tkn(pool=first_check_pools[2], tkn_num=0)
    p0t0 = first_check_pools[0].x_act if tkn0 == flt else first_check_pools[0].y_act
    p0t1 = first_check_pools[0].y_act if tkn0 == flt else first_check_pools[0].x_act
    p2t1 = first_check_pools[2].x_act if tkn5 == flt else first_check_pools[2].y_act
    p2t0 = first_check_pools[2].y_act if tkn5 == flt else first_check_pools[2].x_act
    p1t0 = first_check_pools[1].x if tkn1 == tkn2 else first_check_pools[1].y
    p1t1 = first_check_pools[1].y if tkn1 == tkn2 else first_check_pools[1].x
    fee0 = finder.get_fee_safe(first_check_pools[0].fee)
    fee1 = finder.get_fee_safe(first_check_pools[1].fee)
    fee2 = finder.get_fee_safe(first_check_pools[2].fee)
    optimal_arb_low_level_check = finder.max_arb_trade_in_constant_product(p0t0=p0t0, p0t1=p0t1, p1t0=p1t0, p1t1=p1t1, p2t0=p2t0, p2t1=p2t1,fee0=fee0, fee1=fee1, fee2=fee2)
    optimal_arb = finder.get_optimal_arb_trade_amts(pool_cids, flt)
    assert iseq(optimal_arb, optimal_arb_low_level_check), f"[test_bancor_v3] Arb calculation result mismatch, pools likely ordered incorrectly"
    # -
    

# ------------------------------------------------------------
# Test      038
# File      test_038_TestBancorV3Mode.py
# Segment   Test_get_fee_safe
# ------------------------------------------------------------
def test_test_get_fee_safe():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("bancor_v3")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=False,
                ConfigObj=bot.ConfigObj,
            )
    ext_fee = finder.get_fee_safe(first_check_pools[1].fee)
    assert type(ext_fee) == float, f"[test_bancor_v3] Testing external pool, fee type is {type(ext_fee)} not float"
    assert iseq(ext_fee, 0.0005), f"[test_bancor_v3] Testing external pool, fee amt is {ext_fee} not 0.0005"
    

# ------------------------------------------------------------
# Test      038
# File      test_038_TestBancorV3Mode.py
# Segment   Test_combos
# ------------------------------------------------------------
def test_test_combos():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("bancor_v3")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=False,
                ConfigObj=bot.ConfigObj,
            )
    flt = {'MKR-79A2', 'TRAC-0A6F', 'MONA-412A', 'WBTC-C599', 'WOO-5D4B', 'MATIC-eBB0', 'BAT-87EF', 'UOS-5C8c', 'LRC-EafD', 'NMR-6671', 'DIP-cD83', 'TEMP-1aB9', 'ICHI-A881', 'USDC-eB48', 'ENS-9D72', 'vBNT-7f94', 'ANKR-EDD4', 'UNI-F984', 'REQ-938a', 'WETH-6Cc2', 'AAVE-DaE9', 'ENJ-3B9c', 'MANA-C942', 'wNXM-2bDE', 'QNT-4675', 'RLC-7375', 'CROWN-E0fa', 'CHZ-b4AF', 'USDT-1ec7', 'DAI-1d0F', 'RPL-A51f', 'HOT-26E2', 'LINK-86CA', 'wstETH-2Ca0'}
    
    combos = finder.get_combos(flashloan_tokens=flt, CCm=CCm, arb_mode="bancor_v3")
    assert len(combos) == 1122, "[test_bancor_v3] Different data used for tests, expected 1122 combos"
    # -
    

# ------------------------------------------------------------
# Test      038
# File      test_038_TestBancorV3Mode.py
# Segment   Test_get_miniverse_combos
# ------------------------------------------------------------
def test_test_get_miniverse_combos():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("bancor_v3")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=False,
                ConfigObj=bot.ConfigObj,
            )
    flt = {'MKR-79A2', 'TRAC-0A6F', 'MONA-412A', 'WBTC-C599', 'WOO-5D4B', 'MATIC-eBB0', 'BAT-87EF', 'UOS-5C8c', 'LRC-EafD', 'NMR-6671', 'DIP-cD83', 'TEMP-1aB9', 'ICHI-A881', 'USDC-eB48', 'ENS-9D72', 'vBNT-7f94', 'ANKR-EDD4', 'UNI-F984', 'REQ-938a', 'WETH-6Cc2', 'AAVE-DaE9', 'ENJ-3B9c', 'MANA-C942', 'wNXM-2bDE', 'QNT-4675', 'RLC-7375', 'CROWN-E0fa', 'CHZ-b4AF', 'USDT-1ec7', 'DAI-1d0F', 'RPL-A51f', 'HOT-26E2', 'LINK-86CA', 'wstETH-2Ca0'}
    
    combos = finder.get_combos(flashloan_tokens=flt, CCm=CCm, arb_mode="bancor_v3")
    all_miniverses = finder.get_miniverse_combos(combos)
    assert len(all_miniverses) == 144, f"[test_bancor_v3] Different data used for tests, expected 144 miniverses, got {len(all_miniverses)}"
    # -
    

# ------------------------------------------------------------
# Test      038
# File      test_038_TestBancorV3Mode.py
# Segment   Test_get_mono_direction_carbon_curves
# ------------------------------------------------------------
def test_test_get_mono_direction_carbon_curves():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("bancor_v3")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=False,
                ConfigObj=bot.ConfigObj,
            )
    
    bancor_v3_curve_0 = (
                    finder.CCm.bypairs(f"BNT-FF1C/WETH-6Cc2")
                    .byparams(exchange="bancor_v3")
                    .curves
                )
    bancor_v3_curve_1 = (
                    finder.CCm.bypairs(f"BNT-FF1C/USDC-eB48")
                    .byparams(exchange="bancor_v3")
                    .curves
                )
    carbon_curves = finder.CCm.bypairs(f"USDC-eB48/WETH-6Cc2")
    carbon_curves = list(set(carbon_curves))
    carbon_curves = [
        curve
        for curve in carbon_curves
        if curve.params.get("exchange") == "carbon_v1"
    ]
    miniverse = [bancor_v3_curve_0 + bancor_v3_curve_1 + carbon_curves]
    max_arb_carbon = finder.run_main_flow(miniverse=miniverse[0], src_token="BNT-FF1C")
    (
    profit_src_0,
    trade_instructions_0,
    trade_instructions_df_0,
    trade_instructions_dic_0,
    ) = max_arb_carbon
    
    mono_carbon = finder.get_mono_direction_carbon_curves(miniverse[0], trade_instructions_df=trade_instructions_df_0, token_in=None)
    test_mono_carbon = finder.get_mono_direction_carbon_curves(miniverse[0], trade_instructions_df=trade_instructions_df_0, token_in='WETH-6Cc2')
    # Test that get_mono_direction_carbon_curves removed two curves
    assert len(test_mono_carbon) != len(mono_carbon), f"[test_bancor_v3] Issue with get_mono_direction_carbon_curves, should have removed one or more pools"
    # -
    
    
    
    
    
    