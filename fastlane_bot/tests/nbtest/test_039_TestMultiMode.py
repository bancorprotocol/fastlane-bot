# ------------------------------------------------------------
# Auto generated test file `test_039_TestMultiMode.py`
# ------------------------------------------------------------
# source file   = NBTest_039_TestMultiMode.py
# test id       = 039
# test comment  = TestMultiMode
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
C.DEFAULT_MIN_PROFIT_BNT = 0.02
C.DEFAULT_MIN_PROFIT = 0.02
cfg.DEFAULT_MIN_PROFIT_BNT = 0.02
cfg.DEFAULT_MIN_PROFIT = 0.02
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

arb_mode = "multi"


# ------------------------------------------------------------
# Test      039
# File      test_039_TestMultiMode.py
# Segment   Test_MIN_PROFIT
# ------------------------------------------------------------
def test_test_min_profit():
# ------------------------------------------------------------
    
    assert(cfg.DEFAULT_MIN_PROFIT_BNT <= 0.02), f"[TestMultiMode], DEFAULT_MIN_PROFIT_BNT must be <= 0.02 for this Notebook to run, currently set to {cfg.DEFAULT_MIN_PROFIT_BNT}"
    assert(C.DEFAULT_MIN_PROFIT_BNT <= 0.02), f"[TestMultiMode], DEFAULT_MIN_PROFIT_BNT must be <= 0.02 for this Notebook to run, currently set to {cfg.DEFAULT_MIN_PROFIT_BNT}"
    

# ------------------------------------------------------------
# Test      039
# File      test_039_TestMultiMode.py
# Segment   Test_get_arb_finder
# ------------------------------------------------------------
def test_test_get_arb_finder():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("multi")
    assert arb_finder.__name__ == "FindArbitrageMultiPairwise", f"[TestMultiMode] Expected arb_finder class name name = FindArbitrageMultiPairwise, found {arb_finder.__name__}"
    

# ------------------------------------------------------------
# Test      039
# File      test_039_TestMultiMode.py
# Segment   Test_Combos_and_Tokens
# ------------------------------------------------------------
def test_test_combos_and_tokens():
# ------------------------------------------------------------
    
    arb_finder = bot._get_arb_finder("multi")
    finder2 = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=bot.AO_TOKENS,
                ConfigObj=bot.ConfigObj,
            )
    all_tokens, combos = finder2.find_arbitrage()
    assert len(all_tokens) == 545, f"[TestMultiMode] Using wrong dataset, expected 545 tokens, found {len(all_tokens)}"
    assert len(combos) == 3264, f"[TestMultiMode] Using wrong dataset, expected 3264 tokens, found {len(combos)}"
    

# ------------------------------------------------------------
# Test      039
# File      test_039_TestMultiMode.py
# Segment   Test_Expected_Output
# ------------------------------------------------------------
def test_test_expected_output():
# ------------------------------------------------------------
    
    run_full = bot._run(flashloan_tokens=flashloan_tokens, CCm=CCm, arb_mode=arb_mode, data_validator=False, result=bot.XS_ARBOPPS)
    arb_finder = bot._get_arb_finder("multi")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=bot.AO_CANDIDATES,
                ConfigObj=bot.ConfigObj,
            )
    r = finder.find_arbitrage()
    assert len(r) == 30, f"[TestMultiMode] Expected 30 arbs, found {len(r)}"
    assert len(r) == len(run_full), f"[TestMultiMode] Expected arbs from .find_arbitrage - {len(r)} - to match _run - {len(run_full)}"
    

# ------------------------------------------------------------
# Test      039
# File      test_039_TestMultiMode.py
# Segment   Test_Multiple_Curves_Used
# ------------------------------------------------------------
def test_test_multiple_curves_used():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("multi")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=bot.AO_CANDIDATES,
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
        if len(best_trade_instructions_dic) > 2:
            multi_carbon_count += 1
    
    assert multi_carbon_count > 0, f"[TestMultiMode] Not finding arbs with multiple Carbon curves."
    # -
    

# ------------------------------------------------------------
# Test      039
# File      test_039_TestMultiMode.py
# Segment   Test_Single_Direction_Carbon_Curves
# ------------------------------------------------------------
def test_test_single_direction_carbon_curves():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("multi")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=bot.AO_CANDIDATES,
                ConfigObj=bot.ConfigObj,
            )
    src_token="WBTC-C599" 
    wrong_direction_cids = ['4083388403051261561560495289181218537493-0', '4083388403051261561560495289181218537579-0', '4083388403051261561560495289181218537610-0', '4083388403051261561560495289181218537629-0', '4083388403051261561560495289181218537639-0', '4083388403051261561560495289181218537755-0']
    curves_before = [ConstantProductCurve(k=2290523503.4460173, x=273.1073125047371, x_act=0.07743961144774403, y_act=1814.6001096442342, pair='WBTC-C599/USDC-eB48', cid='0x8d7ac7e77704f3ac75534d5500159a7a4b7e6e23dbdca7d9a8085bdea0348d0c', fee=0.0005, descr='uniswap_v3 WBTC-C599/USDC-eB48 500', constr='pkpp', params={'exchange': 'uniswap_v3', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17675876, 'L': 47859.413948}), ConstantProductCurve(k=3675185.41145277, x=11.059038979187497, x_act=0, y_act=1385.267061, pair='WBTC-C599/USDC-eB48', cid='4083388403051261561560495289181218537493-0', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 1385.267061, 'yint': 1385.267061, 'A': 0.722593217276426, 'B': 172.62676501631972, 'pa': 30049.999999999647, 'pb': 29799.999999999665}), ConstantProductCurve(k=29672.782767383174, x=1.0315213950985431, x_act=0, y_act=3651.804716, pair='WBTC-C599/USDC-eB48', cid='4083388403051261561560495289181218537579-0', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 3651.804716, 'yint': 3651.804716, 'A': 21.199636119827687, 'B': 145.79437574886072, 'pa': 27886.999999999643, 'pb': 21255.999999999985}), ConstantProductCurve(k=6.863635116394053e+16, x=1525337.9097739116, x_act=0, y_act=4499.746836, pair='WBTC-C599/USDC-eB48', cid='4083388403051261561560495289181218537610-0', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 4499.746836, 'yint': 4499.746836, 'A': 0, 'B': 171.7556317853946, 'pa': 29499.99999999976, 'pb': 29499.99999999976}), ConstantProductCurve(k=143046.70577155304, x=2.1824671097293846, x_act=0, y_act=5742.51191, pair='WBTC-C599/USDC-eB48', cid='4083388403051261561560495289181218537629-0', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 5742.51191, 'yint': 6413.595264, 'A': 16.957530991696217, 'B': 158.11388300841884, 'pa': 30649.99999999968, 'pb': 24999.99999999996}), ConstantProductCurve(k=5459975.623181331, x=437148.88403306017, x_act=0, y_act=0.50315999, pair='USDC-eB48/WBTC-C599', cid='4083388403051261561560495289181218537629-1', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 0.50315999, 'yint': 0.50315999, 'A': 0.0002153330778227767, 'B': 0.005129891760425664, 'pa': 2.8571428571428076e-05, 'pb': 2.631578947368312e-05}), ConstantProductCurve(k=443607.9519434853, x=3.85826034424969, x_act=0, y_act=9876.976514, pair='WBTC-C599/USDC-eB48', cid='4083388403051261561560495289181218537639-0', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 9876.976514, 'yint': 9876.976514, 'A': 14.829426635724872, 'B': 157.79733838059485, 'pa': 29799.999999999665, 'pb': 24899.999999999953}), ConstantProductCurve(k=5324.625267368582, x=12680.839210183807, x_act=0, y_act=0.01198047, pair='USDC-eB48/WBTC-C599', cid='4083388403051261561560495289181218537639-1', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 0.01198047, 'yint': 0.01198047, 'A': 0.00016418343273514376, 'B': 0.0055901699437491455, 'pa': 3.311258278145614e-05, 'pb': 3.124999999999633e-05}), ConstantProductCurve(k=3316749913763783.5, x=331674.9583747572, x_act=0, y_act=1000.0, pair='WBTC-C599/USDC-eB48', cid='4083388403051261561560495289181218537755-0', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 1000.0, 'yint': 1000.0, 'A': 0, 'B': 173.63754485997586, 'pa': 30149.999999999825, 'pb': 30149.999999999825})]
    curves_expected_after = [ConstantProductCurve(k=2290523503.4460173, x=273.1073125047371, x_act=0.07743961144774403, y_act=1814.6001096442342, pair='WBTC-C599/USDC-eB48', cid='0x8d7ac7e77704f3ac75534d5500159a7a4b7e6e23dbdca7d9a8085bdea0348d0c', fee=0.0005, descr='uniswap_v3 WBTC-C599/USDC-eB48 500', constr='pkpp', params={'exchange': 'uniswap_v3', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17675876, 'L': 47859.413948}), ConstantProductCurve(k=5459975.623181331, x=437148.88403306017, x_act=0, y_act=0.50315999, pair='USDC-eB48/WBTC-C599', cid='4083388403051261561560495289181218537629-1', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 0.50315999, 'yint': 0.50315999, 'A': 0.0002153330778227767, 'B': 0.005129891760425664, 'pa': 2.8571428571428076e-05, 'pb': 2.631578947368312e-05}), ConstantProductCurve(k=5324.625267368582, x=12680.839210183807, x_act=0, y_act=0.01198047, pair='USDC-eB48/WBTC-C599', cid='4083388403051261561560495289181218537639-1', fee=0.002, descr='carbon_v1 WBTC-C599/USDC-eB48 0.002', constr='carb', params={'exchange': 'carbon_v1', 'tknx_dec': 8, 'tkny_dec': 6, 'tknx_addr': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'blocklud': 17674427, 'y': 0.01198047, 'yint': 0.01198047, 'A': 0.00016418343273514376, 'B': 0.0055901699437491455, 'pa': 3.311258278145614e-05, 'pb': 3.124999999999633e-05})]
    test_process_wrong_direction_pools = finder.process_wrong_direction_pools(curve_combo=curves_before, wrong_direction_cids=wrong_direction_cids)
    O, profit_src, r, trade_instructions_df = finder.run_main_flow(curves=curves_expected_after, src_token="WBTC-C599", tkn0="USDC-eB48", tkn1="WBTC-C599")
    
    assert len(curves_before) - len(wrong_direction_cids) == len(test_process_wrong_direction_pools), f"[TestMultiMode] Wrong direction CIDs not removed correctly, started with {len(curves_before)}, removing {len(wrong_direction_cids)}, expected {len(curves_before) - len(wrong_direction_cids)} got {len(test_process_wrong_direction_pools)}"
    for curve in test_process_wrong_direction_pools:
        assert curve.cid not in wrong_direction_cids, f"[TestMultiMode] Failed to remove curve {curve.cid} from list of wrong direction pools"
    assert iseq(profit_src, 2.905623487869935e-05)