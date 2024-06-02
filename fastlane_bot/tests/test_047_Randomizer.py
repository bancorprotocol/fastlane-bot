# ------------------------------------------------------------
# Auto generated test file `test_047_Randomizer.py`
# ------------------------------------------------------------
# source file   = NBTest_047_Randomizer.py
# test id       = 047
# test comment  = Randomizer
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
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

arb_mode = "multi"


# ------------------------------------------------------------
# Test      047
# File      test_047_Randomizer.py
# Segment   Test_randomizer
# ------------------------------------------------------------
def test_test_randomizer():
# ------------------------------------------------------------
    
    # +
    arb_finder = bot._get_arb_finder("multi")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=arb_finder.AO_CANDIDATES,
                ConfigObj=bot.ConfigObj,
            )
    r = finder.find_arbitrage()
    
    #arb_opp = r[0]
    
    
    assert len(r) >= 26, f"[NB047 Randomizer], expected at least 26 arbs, found {len(r)}"
    
    
    arb_opp_0 = bot.randomize(arb_opps=r, randomizer=0)
    arb_opp_1 = bot.randomize(arb_opps=r, randomizer=1)
    arb_opp_2 = bot.randomize(arb_opps=r, randomizer=1)
    arb_opp_3 = bot.randomize(arb_opps=r, randomizer=1)
    arb_opp_25 = bot.randomize(arb_opps=r, randomizer=1)
    
    assert len(arb_opp_0) == 5, f"[NB047 Randomizer], expected 1 arb back from randomizer with length of 5, found length of {len(arb_opp_0)}"
    assert len(arb_opp_1) == 5, f"[NB047 Randomizer], expected 1 arb back from randomizer with length of 5, found length of {len(arb_opp_1)}"
    assert len(arb_opp_2) == 5, f"[NB047 Randomizer], expected 1 arb back from randomizer with length of 5, found length of {len(arb_opp_2)}"
    assert len(arb_opp_3) == 5, f"[NB047 Randomizer], expected 1 arb back from randomizer with length of 5, found length of {len(arb_opp_3)}"
    assert len(arb_opp_25) == 5, f"[NB047 Randomizer], expected 1 arb back from randomizer with length of 5, found length of {len(arb_opp_25)}"
    assert isinstance(np.float64(arb_opp_0[0]), np.floating), f"[NB047 Randomizer], expected first value back from randomizer to be of type np.float64, found type {type(arb_opp_0[0])}"
    assert isinstance(np.float64(arb_opp_1[0]), np.floating), f"[NB047 Randomizer], expected first value back from randomizer to be of type np.float64, found type {type(arb_opp_1[0])}"
    assert isinstance(np.float64(arb_opp_2[0]), np.floating), f"[NB047 Randomizer], expected first value back from randomizer to be of type np.float64, found type {type(arb_opp_2[0])}"
    # -
    
    assert isinstance(np.float64(arb_opp_3[0]), np.floating), f"[NB047 Randomizer], expected first value back from randomizer to be of type np.float64, found type {type(arb_opp_3[0])}"
    assert isinstance(np.float64(arb_opp_25[0]), np.floating), f"[NB047 Randomizer], expected first value back from randomizer to be of type np.float64, found type {type(arb_opp_25[0])}"
    
    assert type(arb_opp_0[2])  == tuple, f"[NB047 Randomizer], expected third value back from randomizer to be of type list, found type {type(arb_opp_0[2])}"
    assert type(arb_opp_1[2])  == tuple, f"[NB047 Randomizer], expected third value back from randomizer to be of type list, found type {type(arb_opp_1[2])}"
    assert type(arb_opp_2[2])  == tuple, f"[NB047 Randomizer], expected third value back from randomizer to be of type list, found type {type(arb_opp_2[2])}"
    assert type(arb_opp_3[2])  == tuple, f"[NB047 Randomizer], expected third value back from randomizer to be of type list, found type {type(arb_opp_3[2])}"
    assert type(arb_opp_25[2]) == tuple, f"[NB047 Randomizer], expected third value back from randomizer to be of type list, found type {type(arb_opp_25[2])}"
    

# ------------------------------------------------------------
# Test      047
# File      test_047_Randomizer.py
# Segment   Test_sorted_by_profit
# ------------------------------------------------------------
def test_test_sorted_by_profit():
# ------------------------------------------------------------
    
    # +
    arb_opps = [(2.6927646232907136, [{'cid': '0xe37abfaee752c24a764955cbb2d10c3c9f88472263cbd2c00ca57facb0f128fe', 'tknin': 'WETH-6Cc2', 'amtin': 0.003982724863828224, 'tknout': 'BNT-FF1C', 'amtout': -19.27862435251882, 'error': None}, {'cid': '3743106036130323098097120681749450326076-0', 'tknin': 'BNT-FF1C', 'amtin': 16.585859729228105, 'tknout': 'WETH-6Cc2', 'amtout': -0.003982724874543209, 'error': None}]
    ), (2.5352758371554955, [{'cid': '0x748ab2bef0d97e5a044268626e6c9c104bab818605d44f650fdeaa03a3c742d2', 'tknin': 'WETH-6Cc2', 'amtin': 0.003982718826136988, 'tknout': 'BNT-FF1C', 'amtout': -19.1211355663836, 'error': None}, {'cid': '3743106036130323098097120681749450326076-0', 'tknin': 'BNT-FF1C', 'amtin': 16.585859729228105, 'tknout': 'WETH-6Cc2', 'amtout': -0.003982724874543209, 'error': None}]
    ), (1.9702345513100596, [{'cid': '0xc4771395e1389e2e3a12ec22efbb7aff5b1c04e5ce9c7596a82e9dc8fdec725b', 'tknin': 'BNT-FF1C', 'amtin': 750.6057364856824, 'tknout': 'USDC-eB48', 'amtout': -293.5068652469199, 'error': None}, {'cid': '2381976568446569244243622252022377480332-1', 'tknin': 'USDC-eB48', 'amtin': 292.73623752593994, 'tknout': 'BNT-FF1C', 'amtout': -750.6057367324829, 'error': None}]
    ), (2.67115241495777, [{'cid': '0xe37abfaee752c24a764955cbb2d10c3c9f88472263cbd2c00ca57facb0f128fe', 'tknin': 'WETH-6Cc2', 'amtin': 0.0034263543081607395, 'tknout': 'BNT-FF1C', 'amtout': -16.58585974665766, 'error': None}, {'cid': '3743106036130323098097120681749450326076-0', 'tknin': 'BNT-FF1C', 'amtin': 16.585859729228105, 'tknout': 'WETH-6Cc2', 'amtout': -0.003982724874543209, 'error': None}]
    ), (2.535310217715329, [{'cid': '0x748ab2bef0d97e5a044268626e6c9c104bab818605d44f650fdeaa03a3c742d2', 'tknin': 'WETH-6Cc2', 'amtin': 0.003454648687693407, 'tknout': 'BNT-FF1C', 'amtout': -16.58585971966386, 'error': None}, {'cid': '3743106036130323098097120681749450326076-0', 'tknin': 'BNT-FF1C', 'amtin': 16.585859729228105, 'tknout': 'WETH-6Cc2', 'amtout': -0.003982724874543209, 'error': None}]
    ), (5.438084583685771, [{'cid': '0x8f9771f2886aa12c1659c275b8e305f58c7c41ba82df03bb21c0bcac98ffde4b', 'tknin': 'WETH-6Cc2', 'amtin': 0.002847350733645726, 'tknout': 'HEX-eb39', 'amtout': -556.3312638401985, 'error': None}, {'cid': '14291859410679415465461733512134264881242-0', 'tknin': 'HEX-eb39', 'amtin': 556.3312644516602, 'tknout': 'WETH-6Cc2', 'amtout': -0.003980041696137606, 'error': None}]
    ), (5.400385044154462, [{'cid': '0x3a98798837e610ac07762e2d58f29f0cf96297a2528f86e0fe9b903b1e45a204', 'tknin': 'WETH-6Cc2', 'amtin': 0.0028413006787388895, 'tknout': 'HEX-eb39', 'amtout': -553.6187023743987, 'error': None}, {'cid': '14291859410679415465461733512134264881242-0', 'tknin': 'HEX-eb39', 'amtin': 553.6187027173414, 'tknout': 'WETH-6Cc2', 'amtout': -0.003966139257351835, 'error': None}]
    ), (1.9713220433332026, [{'cid': '0xc4771395e1389e2e3a12ec22efbb7aff5b1c04e5ce9c7596a82e9dc8fdec725b', 'tknin': 'BNT-FF1C', 'amtin': 748.6344146891497, 'tknout': 'USDC-eB48', 'amtout': -292.73623879346997, 'error': None}, {'cid': '2381976568446569244243622252022377480332-1', 'tknin': 'USDC-eB48', 'amtin': 292.73623752593994, 'tknout': 'BNT-FF1C', 'amtout': -750.6057367324829, 'error': None}]
    ), (8.465616944048316, [{'cid': '0x5b5f170977fe879c965a9fec9aeba4dfe29659f503cd5fe6e67349bdc3089295', 'tknin': '0x0-1AD5', 'amtin': 359.7323400862515, 'tknout': 'WETH-6Cc2', 'amtout': -0.0070300615800533706, 'error': None}, {'cid': '9868188640707215440437863615521278132277-1', 'tknin': 'WETH-6Cc2', 'amtin': 0.00526677017535393, 'tknout': '0x0-1AD5', 'amtout': -359.73234041399974, 'error': None}]
    ), (6.717558869249757, [{'cid': '0x1eda42a2cced5e9cfffe1b15d7c39253514267401c5bd2e9ca28287f8a996fde', 'tknin': 'rETH-6393', 'amtin': 0.2496827895520255, 'tknout': 'WETH-6Cc2', 'amtout': -0.26914170442614704, 'error': None}, {'cid': '3062541302288446171170371466885913903202-0', 'tknin': 'WETH-6Cc2', 'amtin': 0.267742513570596, 'tknout': 'rETH-6393', 'amtout': -0.2496827897163172, 'error': None}]
    )]
    
    ops = bot.randomize(arb_opps=arb_opps, randomizer=3)
    
    assert iseq(ops[0], 8.465616944048316) or iseq(ops[0], 6.717558869249757) or iseq(ops[0], 5.438084583685771), f"[NB047 Randomizer], expected randomizer to return top 3 most profitable arbs, but it did not!"
    # -
    
    