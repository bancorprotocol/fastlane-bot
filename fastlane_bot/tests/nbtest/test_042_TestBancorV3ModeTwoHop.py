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

arb_mode = "b3_two_hop"


# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_min_profit
# ------------------------------------------------------------
def test_test_min_profit():
# ------------------------------------------------------------
    
    assert C.DEFAULT_MIN_PROFIT_BNT == 50, f"[test_bancor_v3_two_hop] wrong DEFAULT_MIN_PROFIT_BNT for test, expected 50, got {C.DEFAULT_MIN_PROFIT_BNT}"
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_arb_mode_class
# ------------------------------------------------------------
def test_test_arb_mode_class():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("b3_two_hop")
    assert arb_finder.__name__ == "ArbitrageFinderTriangleBancor3TwoHop", f"[test_bancor_v3_two_hop] Wrong Arb Finder class, expected ArbitrageFinderTriangleBancor3TwoHop, got {arb_finder.__name__}"
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_Trade_Merge
# ------------------------------------------------------------
def test_test_trade_merge():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("b3_two_hop")
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
    ordered_scaled_dcts = bot._basic_scaling(
                ordered_trade_instructions_dct, best_src_token
            )
    # Convert the trade instructions
    ordered_trade_instructions_objects = bot._convert_trade_instructions(
        ordered_scaled_dcts)
    tx_route_handler = bot.TxRouteHandlerClass(
                trade_instructions=ordered_trade_instructions_objects
            )
    agg_trade_instructions = (
                tx_route_handler.aggregate_carbon_trades(ordered_trade_instructions_objects)
                if bot._carbon_in_trade_route(ordered_trade_instructions_objects)
                else ordered_trade_instructions_objects
            )
    # Calculate the trade instructions
    calculated_trade_instructions = tx_route_handler.calculate_trade_outputs(
        agg_trade_instructions
    )
    assert len(calculated_trade_instructions) == 3
    # Aggregate multiple Bancor V3 trades into a single trade
    calculated_trade_instructions = TxRouteHandler.aggregate_bancor_v3_trades(
        calculated_trade_instructions
    )
    assert len(calculated_trade_instructions) == 2
    assert calculated_trade_instructions[0].tknin != "BNT-FF1C"
    assert calculated_trade_instructions[0].tknout != "BNT-FF1C"
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_get_optimal_arb_trade_amts
# ------------------------------------------------------------
def test_test_get_optimal_arb_trade_amts():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("b3_two_hop")
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
    
    assert first_check_pools[0].cid == '0x7be3da0f8d0f70d8f7a84a08dd267beea4318ed1c9fb3d602b0f3a3c7bd1cf4a', f"[test_bancor_v3_two_hop] Validation, wrong first pool, expected CID: 0x7be3da0f8d0f70d8f7a84a08dd267beea4318ed1c9fb3d602b0f3a3c7bd1cf4a, got CID: {first_check_pools[0].cid}"
    assert first_check_pools[1].cid == '0x748ab2bef0d97e5a044268626e6c9c104bab818605d44f650fdeaa03a3c742d2', f"[test_bancor_v3_two_hop] Validation, wrong second pool, expected CID: 0x748ab2bef0d97e5a044268626e6c9c104bab818605d44f650fdeaa03a3c742d2, got CID: {first_check_pools[1].cid}"
    assert first_check_pools[2].cid == '0xb1d8cd62f75016872495dae3e19d96e364767e7d674488392029d15cdbcd7b34', f"[test_bancor_v3_two_hop] Validation, wrong third pool, expected CID: 0xb1d8cd62f75016872495dae3e19d96e364767e7d674488392029d15cdbcd7b34, got CID: {first_check_pools[2].cid}"
    assert(len(first_check_pools) == 3), f"[test_bancor_v3_two_hop] Validation expected 3 pools, got {len(first_check_pools)}"
    for pool in first_check_pools:
        assert type(pool) == ConstantProductCurve, f"[test_bancor_v3_two_hop] Validation pool type mismatch, got {type(pool)} expected ConstantProductCurve"
        assert pool.cid in pool_cids, f"[test_bancor_v3_two_hop] Validation missing pool.cid {pool.cid} in {pool_cids}"
    
    optimal_arb = finder.get_optimal_arb_trade_amts(pool_cids, 'DAI-1d0F')
    assert type(optimal_arb) == float, f"[test_bancor_v3_two_hop] Optimal arb calculation type is {type(optimal_arb)} not float"
    assert iseq(optimal_arb, 6179.168331968203), f"[test_bancor_v3_two_hop] Optimal arb calculation type is {optimal_arb}, expected 6179.168331968203"   
    # -
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_max_arb_trade_in_constant_product
# ------------------------------------------------------------
def test_test_max_arb_trade_in_constant_product():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("b3_two_hop")
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
    flt='DAI-1d0F'
    tkn0 = flt
    tkn1 = finder.get_tkn(pool=first_check_pools[0], tkn_num=1) if finder.get_tkn(pool=first_check_pools[0], tkn_num=1) != flt else finder.get_tkn(pool=first_check_pools[0], tkn_num=0)
    tkn2 = finder.get_tkn(pool=first_check_pools[1], tkn_num=0) if finder.get_tkn(pool=first_check_pools[1], tkn_num=0) == tkn1 else finder.get_tkn(pool=first_check_pools[1], tkn_num=1)
    tkn3 = finder.get_tkn(pool=first_check_pools[1], tkn_num=0) if finder.get_tkn(pool=first_check_pools[1], tkn_num=0) != tkn1 else finder.get_tkn(pool=first_check_pools[1], tkn_num=1)
    tkn5 = finder.get_tkn(pool=first_check_pools[2], tkn_num=1) if finder.get_tkn(pool=first_check_pools[2], tkn_num=1) == flt else finder.get_tkn(pool=first_check_pools[2], tkn_num=0)
    p0t0 = first_check_pools[0].x if finder.get_tkn(pool=first_check_pools[0], tkn_num=0) == flt else first_check_pools[0].y
    p0t1 = first_check_pools[0].y if finder.get_tkn(pool=first_check_pools[0], tkn_num=0) == flt else first_check_pools[0].x
    p1t0 = first_check_pools[1].x if tkn1 == finder.get_tkn(pool=first_check_pools[1], tkn_num=0) else first_check_pools[1].y
    p1t1 = first_check_pools[1].y if tkn1 == finder.get_tkn(pool=first_check_pools[1], tkn_num=0) else first_check_pools[1].x
    p2t0 = first_check_pools[2].x if finder.get_tkn(pool=first_check_pools[2], tkn_num=0) != flt else first_check_pools[2].y
    p2t1 = first_check_pools[2].y if finder.get_tkn(pool=first_check_pools[2], tkn_num=0) != flt else first_check_pools[2].x
    fee0 = finder.get_fee_safe(first_check_pools[0].fee)
    fee1 = finder.get_fee_safe(first_check_pools[1].fee)
    fee2 = finder.get_fee_safe(first_check_pools[2].fee)
    optimal_arb = finder.get_optimal_arb_trade_amts(pool_cids, 'DAI-1d0F')
    optimal_arb_low_level_check = finder.max_arb_trade_in_constant_product(p0t0=p0t0, p0t1=p0t1, p1t0=p1t0, p1t1=p1t1, p2t0=p2t0, p2t1=p2t1,fee0=fee0, fee1=fee1, fee2=fee2)
    assert iseq(optimal_arb, optimal_arb_low_level_check), f"[test_bancor_v3_two_hop] Arb calculation result mismatch, pools likely ordered incorrectly, previous calc: {optimal_arb}, this calc: {optimal_arb_low_level_check}"
    # max_arb_in = finder.max_arb_trade_in_constant_product(p0t0, p0t1, p1t0, p1t1, p2t0, p2t1, fee0=fee0, fee1=fee1, fee2=fee2)
    # finder.ConfigObj.logger.info(f"\n\nfirst_check_pools: {first_check_pools}\n\nValidating trade, max_arb_in= {max_arb_in} {tkn0} -> {tkn1} -> {tkn3} -> {tkn5}, token amts: {p0t0, p0t1, p1t0, p1t1, p2t0, p2t1}, fees: {fee0, fee1, fee2}")
    # -
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_get_fee_safe
# ------------------------------------------------------------
def test_test_get_fee_safe():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("b3_two_hop")
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
    ext_fee = finder.get_fee_safe(first_check_pools[2].fee)
    assert type(ext_fee) == float, f"[test_bancor_v3_two_hop] Testing external pool, fee type is {type(ext_fee)} not float"
    assert iseq(ext_fee, 0.0005), f"[test_bancor_v3_two_hop] Testing external pool, fee amt is {ext_fee} not 0.0005"
    
    # -
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_combos
# ------------------------------------------------------------
def test_test_combos():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("b3_two_hop")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=False,
                ConfigObj=bot.ConfigObj,
            )
    #test_2_pools = [ConstantProductCurve(k=2921921249910.464, x=2760126.9934445512, x_act=2760126.9934445512, y_act=1058618.410258, pair='BNT-FF1C/USDC-eB48', cid='0xc4771395e1389e2e3a12ec22efbb7aff5b1c04e5ce9c7596a82e9dc8fdec725b', fee=0.0, descr='bancor_v3 BNT-FF1C/USDC-eB48 0.000', constr='uv2', params={'exchange': 'bancor_v3', 'tknx_dec': 18, 'tkny_dec': 6, 'tknx_addr': '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17713739}), ConstantProductCurve(k=518129588.60853314, x=6351922.348885405, x_act=6351922.348885405, y_act=81.57051679, pair='BNT-FF1C/WBTC-C599', cid='0x3885d978c125e66686e3f678ab64d5b09e61f89bf6e87c9ff66e740fd06aeefa', fee=0.0, descr='bancor_v3 BNT-FF1C/WBTC-C599 0.000', constr='uv2', params={'exchange': 'bancor_v3', 'tknx_dec': 18, 'tkny_dec': 8, 'tknx_addr': '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', 'tkny_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'blocklud': 17713739}), ConstantProductCurve(k=787603837541.6204, x=5107.692365701484, x_act=4.159867948255851, y_act=336571.44633978605, pair='WBTC-C599/USDC-eB48', cid='0x49ed97db2c080b7eac91dfaa7d51d5e8ac34c4dcfbcd3e8f2ed326a2a527b959', fee=0.003, descr='uniswap_v3 WBTC-C599/USDC-eB48 3000', constr='pkpp', params={'exchange': 'uniswap_v3', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17713395, 'L': 887470.4713632})]
    flt = {'MKR-79A2', 'TRAC-0A6F', 'MONA-412A', 'WBTC-C599', 'WOO-5D4B', 'MATIC-eBB0', 'BAT-87EF', 'UOS-5C8c', 'LRC-EafD', 'NMR-6671', 'DIP-cD83', 'TEMP-1aB9', 'ICHI-A881', 'USDC-eB48', 'ENS-9D72', 'vBNT-7f94', 'ANKR-EDD4', 'UNI-F984', 'REQ-938a', 'WETH-6Cc2', 'AAVE-DaE9', 'ENJ-3B9c', 'MANA-C942', 'wNXM-2bDE', 'QNT-4675', 'RLC-7375', 'CROWN-E0fa', 'CHZ-b4AF', 'USDT-1ec7', 'DAI-1d0F', 'RPL-A51f', 'HOT-26E2', 'LINK-86CA', 'wstETH-2Ca0'}
    combos = finder.get_combos(flashloan_tokens=flt, CCm=CCm, arb_mode="b3_two_hop")
    assert len(combos) == 1122, "[test_bancor_v3_two_hop] Different data used for tests, expected 1122 combos"
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_get_miniverse_combos
# ------------------------------------------------------------
def test_test_get_miniverse_combos():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("b3_two_hop")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=False,
                ConfigObj=bot.ConfigObj,
            )
    flt = {'MKR-79A2', 'TRAC-0A6F', 'MONA-412A', 'WBTC-C599', 'WOO-5D4B', 'MATIC-eBB0', 'BAT-87EF', 'UOS-5C8c', 'LRC-EafD', 'NMR-6671', 'DIP-cD83', 'TEMP-1aB9', 'ICHI-A881', 'USDC-eB48', 'ENS-9D72', 'vBNT-7f94', 'ANKR-EDD4', 'UNI-F984', 'REQ-938a', 'WETH-6Cc2', 'AAVE-DaE9', 'ENJ-3B9c', 'MANA-C942', 'wNXM-2bDE', 'QNT-4675', 'RLC-7375', 'CROWN-E0fa', 'CHZ-b4AF', 'USDT-1ec7', 'DAI-1d0F', 'RPL-A51f', 'HOT-26E2', 'LINK-86CA', 'wstETH-2Ca0'}
    combos = finder.get_combos(flashloan_tokens=flt, CCm=CCm, arb_mode="b3_two_hop")
    all_miniverses = finder.get_miniverse_combos(combos)
    assert len(all_miniverses) == 144, f"[test_bancor_v3_two_hop] Different data used for tests, expected 146 miniverses, found {len(all_miniverses)}"
    

# ------------------------------------------------------------
# Test      042
# File      test_042_TestBancorV3ModeTwoHop.py
# Segment   Test_get_mono_direction_carbon_curves
# ------------------------------------------------------------
def test_test_get_mono_direction_carbon_curves():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("b3_two_hop")
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
    assert len(test_mono_carbon) != len(mono_carbon), f"[test_bancor_v3_two_hop] Issue with get_mono_direction_carbon_curves, should have removed one or more pools"