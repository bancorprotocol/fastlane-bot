# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonBot))
from fastlane_bot.testing import *
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)

# # Testing the _run functions on MOCK PairwiseArber_CarbonSingle_POC [NBTest015]

# ## Unittest Alchemy Configuration

# ### Set up the bot

C = Config.new(config=Config.CONFIG_UNITTEST)
assert C.DATABASE == C.DATABASE_UNITTEST
assert C.POSTGRES_DB == "unittest"
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_ALCHEMY
bot = CarbonBot(ConfigObj=C)
assert str(type(bot.db)) == "<class 'fastlane_bot.db.mock_model_managers.MockDatabaseManager'>"
assert bot.db.get_pools()[0].fee_float is not None, "Incorrect pools.csv file see MockPoolManager data"

# ### Set up the curves

cc1 = CPC.from_carbon(pair="WETH-6Cc2/USDC-eB48", tkny="WETH-6Cc2", yint=10, y=10, pa=1/2000, pb=1/2010, 
                      cid="1701411834604692317316873037158841057285-1", params={"exchange":'carbon_v1'})
assert iseq(1/2000, cc1.p, cc1.p_max)
assert iseq(1/2010, cc1.p_min)
assert cc1.p_convention() == 'WETH per USDC'
assert cc1.p_min < cc1.p_max
cc1

cid = cc1.cid
assert bot.db.get_pool(cid=cid.split('-')[0]).exchange_name == 'carbon_v1', "The cids are chosen as they are the correct pools in the test data pools.csv"

cu1 = CPC.from_univ3(pair="WETH-6Cc2/USDC-eB48", Pmarg=2100, uniPa=2000, uniPb=2200, 
                     uniL=200*m.sqrt(2100*2100), fee=0, cid="10548753374549092367364612830384814555378", descr="", params={"exchange":'uniswap_v3'})
assert iseq(cu1.p, 2100)
assert iseq(cu1.p_min, 2000)
assert iseq(cu1.p_max, 2200)
assert cu1.p_convention() == 'USDC per WETH'
assert cu1.p_min < cu1.p_max
cu1

cid = cu1.cid
assert bot.db.get_pool(cid=cid.split('-')[0]).exchange_name == 'uniswap_v3', "The cids are chosen as they are the correct pools in the test data pools.csv"

cu2 = CPC.from_univ3(pair="WETH-6Cc2/USDC-eB48", Pmarg=2100, uniPa=2000, uniPb=2200, 
                     uniL=200*m.sqrt(2100*2100), fee=0, cid="10548753374549092367364612830384814555378", descr="", params={"exchange":'uniswap_v3'})
assert iseq(cu2.p, 2100)
assert iseq(cu2.p_min, 2000)
assert iseq(cu2.p_max, 2200)
assert cu2.p_convention() == 'USDC per WETH'
assert cu2.p_min < cu2.p_max
cu2

cid = cu2.cid
assert bot.db.get_pool(cid=cid.split('-')[0]).exchange_name == 'uniswap_v3', "The cids are chosen as they are the correct pools in the test data pools.csv"

cu1.p, cu2.p, cc1.p

CCm = CPCContainer([cu1, cu2, cc1])
#CCm.plot()

# ### Run the BASE `_find_arbitrage_opportunities`

# #### AO_CANDIDATES [USDC]

flt = ['USDC-eB48']
r_base = bot._find_arbitrage_opportunities(flashloan_tokens=flt, CCm=CCm, result=bot.AO_CANDIDATES)
assert len(r_base) >= 1, "The candidates should be populated in this direction"
r_base0, r_base1, r_base2, r_base3, r_base4 = r_base[0]
assert r_base0 > 0, "The profit should be positive"

assert len(r_base2) == 3, "Operating in the base mode should find a 3-stage arb"

# ### Run the NEW `_find_arbitrage_opportunities_carbon_single_pairwise`

# #### AO_CANDIDATES [USDC]

flt = ['USDC-eB48']
r = bot._find_arbitrage_opportunities_carbon_single_pairwise(flashloan_tokens=flt, CCm=CCm, result=bot.AO_CANDIDATES)
assert len(r) >= 1, "The candidates should be populated in this direction"
r0, r1, r2, r3, r4 = r[0]
assert r0 > 0, "The profit should be positive"

assert r1.loc["TOTAL NET"]["WETH-6Cc2"] < 1e-5, "Net change for WETH should be approximately zero"
assert r1.loc["TOTAL NET"]["USDC-eB48"] < -100, "Arb value for USDC should be positive"
r1

assert len(r2) == 2, "When pair-wise carbon singles there should ONLY be two stages"
r2

assert r3 == flt[0], "The best_src_token should be the flashloan token"
r3

assert len(r4) == 2, "There should be two items in the trade instructions"
r4

for i in range(len(r)):
    assert len(r[i][2])==2, "Every candidate should be constrained to 2-stage"

# #### Full

r = bot._find_arbitrage_opportunities_carbon_single_pairwise(flashloan_tokens=flt, CCm=CCm)

assert r is not None, "This setup should find an arb"
r

# ### Run `_run`

# #### XS_ARBOPPS

ops = bot._find_arbitrage(flashloan_tokens=flt, CCm=CCm, arb_mode=bot.AM_SINGLE)["r"]
ops

assert len(ops) == 5, "The best opportunity should populate correctly"
assert ops[0] > 0, "There should be a profit"
assert str(type(ops[1])) == "<class 'pandas.core.frame.DataFrame'>", "The df should be a df"
assert type(ops[2]) == list, "The list of dicts should be a list"
assert len(ops[2]) == 2, "In this example the list of dicts should have two items"
assert type(ops[2][0]) == dict, "The the first item in the list of dicts should be a dict"
assert len(ops[3].split('-')) == 2, "The best_src_token should be a token key"
assert str(type(ops[4][0])) == "<class 'fastlane_bot.tools.optimizer.CPCArbOptimizer.TradeInstruction'>", "There should be trade instructions"

# #### XS_ORDSCAL

ordscal = bot._run(flashloan_tokens=flt, CCm=CCm, arb_mode=bot.AM_SINGLE)
ordscal

assert ops[2] != ordscal, 'After reordering AND scaling the two dicts should not be alike'
assert set([x['cid'] for x in ops[2]]) == set([x['cid'] for x in ordscal]), 'The cids in should be those out'
assert sum([x['amtin'] for x in ordscal]) < sum([x['amtin'] for x in ops[2]]), "After scaling the total amtin should be decreased"

# #### XS_TI

xsti = bot._run(flashloan_tokens=flt, CCm=CCm, arb_mode=bot.AM_SINGLE)
xsti

assert str(type(xsti[0])) == "<class 'fastlane_bot.helpers.tradeinstruction.TradeInstruction'>", "After processing to TI the item should have trade instructions"
assert sum([1 if xsti[i]._is_carbon else 0 for i in range(len(xsti))]) == 1, "In this example there should be a carbon order present identifiable from the TI object"
assert xsti[0].db is not None, "A db should be present"
assert xsti[0].ConfigObj is not None, "A configobj should be present"

# #### XS_AGGTI

agg = bot._run(flashloan_tokens=flt, CCm=CCm, arb_mode=bot.AM_SINGLE)
agg

assert agg[0].raw_txs != "[]", "In this case, the carbon order is first, when agg correctly the raw_txs should not be empty"
assert agg[1].raw_txs == "[]", "In this case, the univ3 order is second, when agg correctly the raw_txs should be empty"

# #### XS_ORDINFO

ordinfo = bot._run(flashloan_tokens=flt, CCm=CCm, arb_mode=bot.AM_SINGLE)
ordinfo

assert ordinfo[0] == agg, "The trade instructions should not have changed"
assert ordinfo[1] > 0, "The flashloan amount should be greater than zero"
assert ordinfo[2][:2] == '0x', "The flashloan address should start with 0x"

# #### XS_ENCTI

enc = bot._run(flashloan_tokens=flt, CCm=CCm, arb_mode=bot.AM_SINGLE)
enc

assert len(enc[0].custom_data) >= 258, "In this example, the carbon order is first so the custom data should have been populated with at least one set of instructions"
assert enc[1].custom_data == '0x', "In this case, the univ3 order is second so the custom data should be only 0x"

# #### XS_ROUTE

route = bot._run(flashloan_tokens=flt, CCm=CCm, arb_mode=bot.AM_SINGLE)
route


assert len(route) ==2, 'In this example, there should be two parts to the route'
assert type(route) == list, "The Route should be a list"
assert type(route[0]) == dict, "Each instruction in the Route should be a dict"
assert list(route[0].keys()) == ['exchangeId', 'targetToken', 'minTargetAmount', 'deadline', 'customAddress', 'customInt', 'customData'], "All keys should be present"
assert list(route[1].keys()) == ['exchangeId', 'targetToken', 'minTargetAmount', 'deadline', 'customAddress', 'customInt', 'customData'], "All keys should be present"

assert type(route[0]['exchangeId']) == int, "Exchange ids should be ints"
assert type(route[0]['targetToken']) == str, "targetToken should be str"
assert type(route[0]['minTargetAmount']) == int, "minTargetAmount should be ints"
assert type(route[0]['deadline']) == int, "deadline should be ints"
assert type(route[0]['customAddress']) == str, "customAddress should be str"
assert type(route[0]['customInt']) == int, "customInt should be ints"
assert type(route[0]['customData']) == str, "customData should be str"
