# ------------------------------------------------------------
# Auto generated test file `test_060_TestRoutehandlerCarbonPrecision.py`
# ------------------------------------------------------------
# source file   = NBTest_060_TestRoutehandlerCarbonPrecision.py
# test id       = 060
# test comment  = TestRoutehandlerCarbonPrecision
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
import decimal
import json
import math
from _decimal import Decimal
from typing import List, Dict

from joblib import Parallel, delayed

from fastlane_bot import Bot
from fastlane_bot.bot import CarbonBot
from fastlane_bot.config import Config
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.helpers import TxRouteHandler, TradeInstruction
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

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

C = cfg = Config.new(config=Config.CONFIG_MAINNET,) #blockchain="coinbase_base")
C.DEFAULT_MIN_PROFIT_GAS_TOKEN = 0.005

setup_bot = CarbonBot(ConfigObj=C)
pools = None

### 
"""
Put path to log file here >>>
"""
###

path = os.path.normpath("fastlane_bot/tests/_data/latest_pool_data_testing.json")
print(f"path={path}")
with open(path) as f:
    pools = json.load(f)




flashloan_tokens = ["0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C","0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2","0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48","0x514910771AF9Ca656af840dff83E8264EcF986CA"]
#flashloan_tokens = ["WETH-0006,USDC-2913"]

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
uniswap_v3_event_mappings = pd.read_csv("fastlane_bot/data/uniswap_v3_event_mappings.csv", low_memory=False)

tokens = pd.read_csv("fastlane_bot/data/tokens.csv", low_memory=False)
        
exchanges = "carbon_v1,pancakeswap_v2,pancakeswap_v3,uniswap_v2,uniswap_v3"

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
    #uniswap_v3_event_mappings=uniswap_v3_event_mappings,
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
#flashloan_tokens = bot.RUN_FLASHLOAN_TOKENS
#flashloan_tokens = ['WBTC-2c599', 'USDC-eB48', 'LINK-86CA', 'USDT-1ec7']


CCm = bot.get_curves()
pools = db.get_pool_data_with_tokens()





# ------------------------------------------------------------
# Test      060
# File      test_060_TestRoutehandlerCarbonPrecision.py
# Segment   Test_Precision_Using_All_Tokens_In_Carbon
# ------------------------------------------------------------
def test_test_precision_using_all_tokens_in_carbon():
# ------------------------------------------------------------
    
    # +    
    arb_finder = bot._get_arb_finder("multi_pairwise_all")
    finder = arb_finder(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                mode="bothin",
                result=arb_finder.AO_CANDIDATES,
                ConfigObj=bot.ConfigObj,
            )
    r = finder.find_arbitrage()
    
    r = [arb for arb in r if len(arb[2]) >= 2]
    r.sort(key=lambda x: x[0], reverse=True)
    print(f"number of arbs found = {len(r)}")
    
    
    # -
    
    def calculate_trade_outputs(tx_route_handler: TxRouteHandler,
        trade_instructions: List[TradeInstruction]
    ) -> List[TradeInstruction]:
        """
        Refactored calculate trade outputs.
    
        Parameters
        ----------
        trade_instructions: List[Dict[str, Any]]
            The trade instructions.
    
        Returns
        -------
        List[Dict[str, Any]]
            The trade outputs.
        """
    
        next_amount_in = trade_instructions[0].amtin
        for idx, trade in enumerate(trade_instructions):
            raw_txs_lst = []
            # total_percent = 0
            if trade.amtin <=0:
                trade_instructions.pop(idx)
                continue
            if trade.raw_txs != "[]":
                data = eval(trade.raw_txs)
                total_out = 0
                total_in = 0
                total_in_wei = 0
                total_out_wei = 0
                expected_in = trade_instructions[idx].amtin
    
                remaining_tkn_in = Decimal(str(next_amount_in))
                tx_route_handler.ConfigObj.logger.info(f"\n\n")
    
                tx_route_handler.ConfigObj.logger.info(f"[calculate_trade_outputs Carbon] starting Carbon trade calculations, {len(data)} trades, remaining_tkn_in = {remaining_tkn_in}")
                for tx in data:
                    try:
                        tx["percent_in"] = Decimal(str(tx["amtin"]))/Decimal(str(expected_in))
                    except decimal.InvalidOperation:
                        tx["percent_in"] = 0
                        # total_percent += tx["amtin"]/expected_in
                        tx_route_handler.ConfigObj.logger.info(f"[calculate_trade_outputs] Invalid operation: {tx['amtin']}/{expected_in}")
    
                last_tx = len(data) - 1
    
                for _idx, tx in enumerate(data):
                    cid = tx["cid"]
                    cid = cid.split("-")[0]
                    tknin_key = tx["tknin"]
    
                    _next_amt_in = Decimal(str(next_amount_in)) * tx["percent_in"]
                    if _next_amt_in > remaining_tkn_in:
                        _next_amt_in = remaining_tkn_in
    
    
                    if _idx == last_tx:
                        if _next_amt_in < remaining_tkn_in:
                            _next_amt_in = remaining_tkn_in
    
                    curve = trade_instructions[idx].db.get_pool(cid=cid)
                    (
                        amount_in,
                        amount_out,
                        amount_in_wei,
                        amount_out_wei,
                    ) = tx_route_handler._solve_trade_output(
                        curve=curve, trade=trade, amount_in=_next_amt_in
                    )
    
                    remaining_tkn_in -= amount_in
                    tx_route_handler.ConfigObj.logger.info(f"[calculate_trade_outputs Carbon] calculated trade, {amount_in} {tknin_key} into trade, remaining={remaining_tkn_in}")
    
                    if amount_in_wei <= 0:
                        continue
                    raw_txs = {
                        "cid": cid,
                        "tknin": tx["tknin"],
                        "amtin": amount_in,
                        "_amtin_wei": amount_in_wei,
                        "tknout": tx["tknout"],
                        "amtout": amount_out,
                        "_amtout_wei": amount_out_wei,
                    }
                    raw_txs_lst.append(raw_txs)
                    total_in += amount_in
                    total_out += amount_out
                    total_in_wei += amount_in_wei
                    total_out_wei += amount_out_wei
    
                    remaining_tkn_in = TradeInstruction._quantize(amount=remaining_tkn_in, decimals=trade.tknin_decimals)
                    if _idx == last_tx and remaining_tkn_in > 0:
                        tx_route_handler.ConfigObj.logger.info(f"[calculate_trade_outputs Carbon] LAST trade going into Carbon but {remaining_tkn_in} remaining. Stuffing remainder into other orders:")
    
                        for __idx, _tx in enumerate(raw_txs_lst):
                            adjusted_next_amt_in = _tx["amtin"] + remaining_tkn_in
                            _curve = trade_instructions[idx].db.get_pool(cid=_tx["cid"])
                            (
                                _amount_in,
                                _amount_out,
                                _amount_in_wei,
                                _amount_out_wei,
                            ) = tx_route_handler._solve_trade_output(
                                curve=_curve, trade=trade, amount_in=adjusted_next_amt_in
                            )
    
                            test_remaining = remaining_tkn_in - _amount_in + _tx["amtin"]
                            remaining_tkn_in = TradeInstruction._quantize(amount=remaining_tkn_in,
                                                                            decimals=trade.tknin_decimals)
                            if test_remaining < 0:
                                tx_route_handler.ConfigObj.logger.info(
                                    f"[calculate_trade_outputs Carbon] Trade overflow, trying next order.")
                                continue
    
                            remaining_tkn_in = remaining_tkn_in + _tx["amtin"] - _amount_in
    
                            _raw_txs = {
                                "cid": _tx["cid"],
                                "tknin": _tx["tknin"],
                                "amtin": _amount_in,
                                "_amtin_wei": _amount_in_wei,
                                "tknout": _tx["tknout"],
                                "amtout": _amount_out,
                                "_amtout_wei": _amount_out_wei,
                            }
    
                            raw_txs_lst[__idx] = _raw_txs
    
                            if __idx == last_tx:
                                assert remaining_tkn_in == 0, f"Failed to use all tokens into Carbon trade after trying to put more tokens into every order, {remaining_tkn_in} remaining"
    
                            if remaining_tkn_in == 0:
                                tx_route_handler.ConfigObj.logger.info(
                                    f"[calculate_trade_outputs Carbon] Remaining tkns in == 0. Process complete")
                                break
                assert remaining_tkn_in == 0, f"Failed to use all tokens into Carbon trade, {remaining_tkn_in} remaining"
    
    
                amount_out = total_out
                trade_instructions[idx].amtin = total_in
                trade_instructions[idx].amtout = amount_out
                trade_instructions[idx]._amtin_wei = total_in_wei
                trade_instructions[idx]._amtout_wei = total_out_wei
                trade_instructions[idx].raw_txs = str(raw_txs_lst)
    
            else:
    
                curve_cid = trade.cid
                curve = trade_instructions[idx].db.get_pool(cid=curve_cid)
                (
                    amount_in,
                    amount_out,
                    amount_in_wei,
                    amount_out_wei,
                ) = tx_route_handler._solve_trade_output(
                    curve=curve, trade=trade, amount_in=next_amount_in
                )
                trade_instructions[idx].amtin = amount_in
                trade_instructions[idx].amtout = amount_out
                trade_instructions[idx]._amtin_wei = amount_in_wei
                trade_instructions[idx]._amtout_wei = amount_out_wei
    
            next_amount_in = amount_out
    
    
        return trade_instructions
    
    
    for arb in r:
    
        (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = arb
    
        # Order the trade instructions
        (
            ordered_trade_instructions_dct,
            tx_in_count,
        ) = bot._simple_ordering_by_src_token(
            best_trade_instructions_dic, best_src_token
        )
    
        # Scale the trade instructions
        ordered_scaled_dcts = bot._basic_scaling(
            ordered_trade_instructions_dct, best_src_token
        )
    
        # Convert the trade instructions
        ordered_trade_instructions_objects = bot._convert_trade_instructions(
            ordered_scaled_dcts
        )
    
        # Create the tx route handler
        tx_route_handler = TxRouteHandler(
            trade_instructions=ordered_trade_instructions_objects
        )
    
        # Aggregate the carbon trades
        agg_trade_instructions = (
            tx_route_handler.aggregate_carbon_trades(ordered_trade_instructions_objects)
            if bot._carbon_in_trade_route(ordered_trade_instructions_objects)
            else ordered_trade_instructions_objects
        )
    
        # Calculate the trade instructions
        #try:
        calculated_trade_instructions = calculate_trade_outputs(tx_route_handler=tx_route_handler,trade_instructions=agg_trade_instructions)
    
    
    
    