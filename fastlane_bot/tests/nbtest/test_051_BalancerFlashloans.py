# ------------------------------------------------------------
# Auto generated test file `test_051_BalancerFlashloans.py`
# ------------------------------------------------------------
# source file   = NBTest_051_BalancerFlashloans.py
# test id       = 051
# test comment  = BalancerFlashloans
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
from joblib import Parallel, delayed
from dataclasses import dataclass, asdict, field
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

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)



C = cfg = Config.new(config=Config.CONFIG_MAINNET)
C.DEFAULT_MIN_PROFIT_BNT = 20
C.DEFAULT_MIN_PROFIT = 20
cfg.DEFAULT_MIN_PROFIT_BNT = 20
cfg.DEFAULT_MIN_PROFIT = 20
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

arb_mode = "multi_pairwise"


# ------------------------------------------------------------
# Test      051
# File      test_051_BalancerFlashloans.py
# Segment   Test_extract_flashloan_tokens
# ------------------------------------------------------------
def test_test_extract_flashloan_tokens():
# ------------------------------------------------------------
    
    # +
    ti1 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='USDC-eB48',
        amtin=5000,
        tknout='WBTC-2c599',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  6,
        tknout_dec_override = 8,
        tknin_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tknout_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'bancor_v3'
    )
    
    ti2 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='WBTC-2c599',
        amtin=1,
        tknout='USDC-eB48',
        amtout=5005,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  8,
        tknin_dec_override = 6,
        tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tknin_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'carbon_v1'
    )
    
    ti3 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='USDC-eB48',
        amtin=5000,
        tknout='WBTC-2c599',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  6,
        tknout_dec_override = 8,
        tknin_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tknout_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'bancor_v3'
    )
    
    ti4 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='WBTC-2c599',
        amtin=0.2,
        tknout='USDC-eB48',
        amtout=1000,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  8,
        tknin_dec_override = 6,
        tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tknin_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'carbon_v1'
    )
    ti5 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='WBTC-2c599',
        amtin=0.3,
        tknout='USDC-eB48',
        amtout=2000,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  8,
        tknin_dec_override = 6,
        tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tknin_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'carbon_v1'
    )
    
    ti6 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='WBTC-2c599',
        amtin=0.5,
        tknout='USDC-eB48',
        amtout=3005,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  8,
        tknin_dec_override = 6,
        tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tknin_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'carbon_v1'
    )
    
    ti7 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='USDT',
        amtin=2000,
        tknout='ETH-EEeE',
        amtout=1.5,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  6,
        tknout_dec_override = 18,
        tknin_addr_override = '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        tknout_addr_override = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        exchange_override = 'bancor_v3'
    )
    
    ti8 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='ETH-EEeE',
        amtin=1.5,
        tknout='USDT',
        amtout=3005,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  18,
        tknin_dec_override = 6,
        tknout_addr_override = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        tknin_addr_override = '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        exchange_override = 'carbon_v1'
    )
    
    ti9 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='ETH-EEeE',
        amtin=5,
        tknout='USDC',
        amtout=10000,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 6,
        tknin_addr_override = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        exchange_override = 'bancor_v3'
    )
    
    ti10 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='USDC',
        amtin=10000,
        tknout='ETH-EEeE',
        amtout=5.7,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  6,
        tknin_dec_override = 18,
        tknout_addr_override = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        tknin_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
        exchange_override = 'carbon_v1'
    )
    
    ti11 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='BNT-FF1C',
        amtin=50000,
        tknout='USDC',
        amtout=20000,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 6,
        tknin_addr_override = '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
        tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        exchange_override = 'bancor_v3'
    )
    
    ti12 = TradeInstruction(
        cid='4083388403051261561560495289181218537544',
        tknin='USDC',
        amtin=20000,
        tknout='BNT-FF1C',
        amtout=50115,
        ConfigObj=cfg,
        db = db,
        tknout_dec_override =  6,
        tknin_dec_override = 18,
        tknout_addr_override = '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
        tknin_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        exchange_override = 'carbon_v1'
    )
    instructions = [ti1, ti2]
    instructions2 = [ti3, ti4, ti5, ti6, ti7, ti8]
    instructions3 = [ti3, ti4, ti5, ti6, ti7, ti8, ti9, ti10, ti11, ti12]
    
    route_handler = TxRouteHandler(instructions)
    route_handler2 = TxRouteHandler(instructions2)
    route_handler3 = TxRouteHandler(instructions3)
    
    
    flashloan_tokens = route_handler._extract_flashloan_tokens(instructions)
    flashloan_tokens2 = route_handler._extract_flashloan_tokens(instructions2)
    flashloan_tokens3 = route_handler._extract_flashloan_tokens(instructions3)
    
    
    flashloan_struct = route_handler._get_flashloan_struct(instructions2)
    flashloan_struct2 = route_handler._get_flashloan_struct(instructions3)
    
    
    flash_struct3 = route_handler.generate_flashloan_struct(instructions3)
    
    assert len(flashloan_tokens2.keys()) == 2
    assert flashloan_tokens2['USDC-eB48']["flash_amt"] == 5000
    assert flashloan_tokens2['USDT']["flash_amt"] == 2000
    assert len(flash_struct3) == 4, f"[Advanced Routing NBTest044] wrong number of flash tokens length, expected 4, got {len(flash_struct3)}"
    assert flash_struct3[0]['platformId'] == 2, f"[Balancer Flashloan Support [NBTest049]] wrong platformId, expected 2, got {flash_struct3[0]['platformId']}"
    assert flash_struct3[1]['platformId'] == 2, f"[Balancer Flashloan Support [NBTest049]] wrong platformId, expected 2, got {flash_struct3[1]['platformId']}"
    assert flash_struct3[3]['platformId'] == 7, f"[Balancer Flashloan Support [NBTest049]] wrong platformId, expected 7, got {flash_struct3[2]['platformId']}"
    
    for flashloan in flash_struct3:
        assert len(flashloan['sourceTokens']) == len(flashloan['sourceAmounts']), f"[Balancer Flashloan Support [NBTest049]] number of source tokens does not match source amounts, tkns: {len(flashloan['sourceTokens'])} amts: {len(flashloan['sourceAmounts'])}"
    # -
    
    
    