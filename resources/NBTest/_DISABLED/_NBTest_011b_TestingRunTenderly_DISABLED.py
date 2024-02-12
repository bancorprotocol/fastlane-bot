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
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonBot))
from fastlane_bot.testing import *
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)

# # Testing the _run functions on TENDERLY [NBTest011b]

# ## TENDERLY Configuration

# + jupyter={"outputs_hidden": false}
ADDRDEC = dict(
    USDC=("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
    WETH=("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18),
)
# -

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
c1, c2 = C_nw.shellcommand().splitlines()
print(c1)
print(c2)
# !{c1}
# !{c2}

# ### Set up the bot and curves

C = Config.new(config=Config.CONFIG_TENDERLY)
bot = CarbonBot(ConfigObj=C)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "tenderly"
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.PROVIDER == C.PROVIDER_TENDERLY
assert C.w3.provider.endpoint_uri.startswith("https://rpc.tenderly.co/fork/")
assert len(bot.db.get_carbon_pairs()) > 10
assert bot.db.carbon_controller.address == '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1'
assert str(type(bot.db)) == "<class 'fastlane_bot.db.manager.DatabaseManager'>"

#provided here for convenience; must be commented out for tests
bot.update(drop_tables=True, only_carbon=False, top_n=100)

CCm = bot.get_curves()
CCc1 = CCm.byparams(exchange="carbon_v1")
CCb3 = CCm.byparams(exchange="bancor_v3")
CCu2 = CCm.byparams(exchange="uniswap_v2")
CCu3 = CCm.byparams(exchange="uniswap_v3")
exch = {c.P("exchange") for c in CCm}
b3_prices_l = [(c.pairo.tknq, c.p, c.p_convention()) for c in CCb3]
b3_prices_l[:5]
b3_prices = {r[0]:r[1] for r in b3_prices_l}
u2_prices_l = [(c.pairo.pair, c.p, c.p_convention()) for c in CCu2]
price = lambda tknq, tknb: b3_prices[tknb]/b3_prices[tknq]
print("Number of curves:", len(CCm), len(CCb3), len(CCu2), len(CCc1), len(CCu3))
print("Number of tokens:", len(CCm.tokens()))
# for pair in [(T.WBTC, T.USDC), (T.DAI, T.USDC)]:
#     print(f"Price {pair}:", price(*pair))
print("Exchanges:", exch)

assert {T.ETH, T.USDC, T.WBTC, T.DAI, T.BNT} - CCm.tokens() == set(), "Key tokens missing"
assert len(CCm) > 100, f"Not enough curves {len(CCm)}"
assert len(b3_prices_l) == len(CCb3)
assert price(T.WBTC, T.WBTC) == 1
assert price(T.USDC, T.USDC) == 1
assert price(T.WBTC, T.USDC) > 10000
assert price(T.USDC, T.WBTC) < 1/10000
assert np.all(r[1]>0 for r in b3_prices_l)
assert 'uniswap_v3' in exch, f"uni v3 not in exchanges {exch}"
assert 'carbon_v1' in exch, f"carbon not in exchanges {exch}"
assert len(exch) == 6, f"exchanges missing {exch}"

CCm = bot.get_curves()
len(CCm)

# +
#CCm.plot()
# -

# ### Run `_find_arbitrage_opportunities}`

# #### AO_TOKENS

flt = [T.ETH]
r=bot._find_arbitrage_opportunities(flashloan_tokens=flt, CCm=CCm, result=bot.AO_TOKENS)
#r
len(r[0]), len(r[1]), list(r[0])[0], list(r[1])[0]

assert len(r[0]) > 100
assert len(r[1]) > 100
# assert r[1] == [('WETH-6Cc2', 'USDC-eB48')]

# #### AO_CANDIDATES [USDC]

flt = [T.USDC]
r = bot._find_arbitrage_opportunities(flashloan_tokens=flt, CCm=CCm, result=bot.AO_CANDIDATES)
len(r)

# #### AO_CANDIDATES [WETH]

flt = [T.WETH]
r = bot._find_arbitrage_opportunities(flashloan_tokens=flt, CCm=CCm, result=bot.AO_CANDIDATES)
print("---\nlen(r)", len(r))
assert len(r) >= 1, "The candidates should be populated in this direction"
r0, r1, r2, r3, r4 = r[1]
# assert r0 > 0, "The profit should be positive"
r

tn = r1.loc["TOTAL NET"].to_dict()
tntkn = list(set(tn.keys()) - {flt[0]})
print("TOTAL NET", tn)
print("TOKENS", tntkn, flt[0])
r1

assert r1.loc["TOTAL NET"]["WETH-6Cc2"] < 1e-5, "Net change for WETH should be approximately zero"
assert abs(tn[tntkn[0]]) < 1e-5, f"{tntkn[0]} should be net zero {tn[tntkn[0]]}"
assert tn[flt[0]] < -0.00001, f"Arb value for {flt[0]} should be positive {-tn[flt[0]]}"
r1

assert len(r2) == 2, "There should be two items in the best_trade_instructions_dict"
r2

assert r3 == flt[0], "The best_src_token should be the flashloan token"
r3

assert len(r4) == 2, "There should be two items in the trade instructions"
r4

# #### Full

r = bot._find_arbitrage_opportunities(flashloan_tokens=flt, CCm=CCm)

assert r[0] != 0, f"This setup should find an arb {r}"
r

# ### Run `_run`

# #### XS_ARBOPPS

ops = bot._find_arbitrage(flashloan_tokens=flt, CCm=CCm)["r"]
ops

# +
# assert len(ops) == 5, "The best opportunity should populate correctly"
# assert ops[0] > 0, "There should be a profit"
# assert str(type(ops[1])) == "<class 'pandas.core.frame.DataFrame'>", "The df should be a df"
# assert type(ops[2]) == list, "The list of dicts should be a list"
# assert len(ops[2]) == 2, "In this example the list of dicts should have two items"
# assert type(ops[2][0]) == dict, "The the first item in the list of dicts should be a dict"
# assert len(ops[3].split('-')) == 2, "The best_src_token should be a token key"
# assert str(type(ops[4][0])) == "<class 'fastlane_bot.tools.optimizer.CPCArbOptimizer.TradeInstruction'>", "There should be trade instructions"
# -

# #### XS_ORDSCAL

ordscal = bot._run(flashloan_tokens=flt, CCm=CCm)
ordscal

# +
# assert ops[2] != ordscal, 'After reordering AND scaling the two dicts should not be alike'
# assert set([x['cid'] for x in ops[2]]) == set([x['cid'] for x in ordscal]), 'The cids in should be those out'
# assert sum([x['amtin'] for x in ordscal]) < sum([x['amtin'] for x in ops[2]]), "After scaling the total amtin should be decreased"
# -

# #### XS_TI

xsti = bot._run(flashloan_tokens=flt, CCm=CCm)
xsti

# +
# assert str(type(xsti[0])) == "<class 'fastlane_bot.helpers.tradeinstruction.TradeInstruction'>", "After processing to TI the item should have trade instructions"
# assert sum([1 if xsti[i]._is_carbon else 0 for i in range(len(xsti))]) == 1, "In this example there should be a carbon order present identifiable from the TI object"
# assert xsti[0].db is not None, "A db should be present"
# assert xsti[0].ConfigObj is not None, "A configobj should be present"
# -

# #### XS_AGGTI

agg = bot._run(flashloan_tokens=flt, CCm=CCm)
agg

# +
# assert agg[0].raw_txs != "[]", "In this case, the carbon order is first, when agg correctly the raw_txs should not be empty"
# assert agg[1].raw_txs == "[]", "In this case, the univ3 order is second, when agg correctly the raw_txs should be empty"
# -

# #### XS_ORDINFO

ordinfo = bot._run(flashloan_tokens=flt, CCm=CCm)
ordinfo

# +
# assert ordinfo[0] == agg, "The trade instructions should not have changed"
# assert ordinfo[1] > 0, "The flashloan amount should be greater than zero"
# assert ordinfo[2][:2] == '0x', "The flashloan address should start with 0x"
# -

# #### XS_ENCTI

enc = bot._run(flashloan_tokens=flt, CCm=CCm)
enc

# +
# assert len(enc[0].custom_data) >= 258, "In this example, the carbon order is first so the custom data should have been populated with at least one set of instructions"
# assert enc[1].custom_data == '0x', "In this case, the univ3 order is second so the custom data should be only 0x"
# -

# #### XS_ROUTE

route = bot._run(flashloan_tokens=flt, CCm=CCm)
route


# +
# assert len(route) ==2, 'In this example, there should be two parts to the route'
# assert type(route) == list, "The Route should be a list"
# assert type(route[0]) == dict, "Each instruction in the Route should be a dict"
# assert list(route[0].keys()) == ['exchangeId', 'targetToken', 'minTargetAmount', 'deadline', 'customAddress', 'customInt', 'customData'], "All keys should be present"
# assert list(route[1].keys()) == ['exchangeId', 'targetToken', 'minTargetAmount', 'deadline', 'customAddress', 'customInt', 'customData'], "All keys should be present"

# +
# assert type(route[0]['exchangeId']) == int, "Exchange ids should be ints"
# assert type(route[0]['targetToken']) == str, "targetToken should be str"
# assert type(route[0]['minTargetAmount']) == int, "minTargetAmount should be ints"
# assert type(route[0]['deadline']) == int, "deadline should be ints"
# assert type(route[0]['customAddress']) == str, "customAddress should be str"
# assert type(route[0]['customInt']) == int, "customInt should be ints"
# assert type(route[0]['customData']) == str, "customData should be str"
# -






