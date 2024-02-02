# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from fastlane_bot import Bot, Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *
import itertools as it
import collections as cl
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# # Mainnet Server [A010]

bot     = Bot()
CCm     = bot.get_curves()

pairs0  = CCm.pairs(standardize=False)
pairs   = CCm.pairs(standardize=True)
pairsc  = {c.pairo.primary for c in CCm if c.P("exchange")=="carbon_v1"}

# ## Overall market 

print(f"Total pairs:    {len(pairs0):4}")
print(f"Primary pairs:  {len(pairs):4}")
print(f"...carbon:      {len(pairsc):4}")
print(f"Tokens:         {len(CCm.tokens()):4}")
print(f"Curves:         {len(CCm):4}")

# ## By pair 

# ### All pairs

cbp0 = {pair: [c for c in CCm.bypairs(pair)] for pair in CCm.pairs()} # curves by (primary) pair
nbp0 = {pair: len(cc) for pair,cc in cbp0.items()}
assert len(cbp0) == len(CCm.pairs())
assert set(cbp0) == CCm.pairs()

# ### Only those with >1 curves

cbp = {pair: cc for pair, cc in cbp0.items() if len(cc)>1}
nbp = {pair: len(cc) for pair,cc in cbp.items()}
print(f"Pairs with >1 curves:  {len(cbp)}")
print(f"Curves in those:       {sum(nbp.values())}")
print(f"Average curves/pair:   {sum(nbp.values())/len(cbp):.1f}")

# ### x=0 or y=0

xis0 = {c.cid: (c.x, c.y) for c in CCm if c.x==0}
yis0 = {c.cid: (c.x, c.y) for c in CCm if c.y==0}
assert len(xis0) == 0 # set loglevel debug to see removal of curves
assert len(yis0) == 0

# ### Prices

# #### All

prices_da = {pair: 
             [(
                Pair.n(pair), c.primaryp(), c.cid, c.cid[-8:], c.P("exchange"), c.tvl(tkn=pair.split("/")[0]),
                "x" if c.itm(cc) else "", c.buysell(verbose=False), c.buysell(verbose=True, withprice=True)
              ) for c in cc 
             ] 
             for pair, cc in cbp.items()
            }
#prices_da

# #### Only for pairs that have at least on Carbon pair

prices_d = {pair: l for pair,l in prices_da.items() if pair in pairsc}
prices_l = list(it.chain(*prices_d.values()))

curves_by_pair = list(cl.Counter([r[0] for r in prices_l]).items())
curves_by_pair = sorted(curves_by_pair, key=lambda x: x[1], reverse=True)
curves_by_pair

# +
# for pair, _ in curves_by_pair:
#     print(f"# #### {pair}\n\npricedf.loc['{pair}']\n\n")
# -

# #### Dataframe

pricedf0 = pd.DataFrame(prices_l, columns="pair,price,cid,cid0,exchange,vl,itm,bs,bsv".split(","))
pricedf = pricedf0.drop('cid', axis=1).sort_values(by=["pair", "exchange", "cid0"])
pricedf = pricedf.set_index(["pair", "exchange", "cid0"])
pricedf

# ### Individual frames

# #### WETH/USDC

pricedf.loc['WETH/USDC']


# #### BNT/WETH

pricedf.loc['BNT/WETH']


# #### BNT/vBNT

pricedf.loc['BNT/vBNT']


# #### USDT/USDC

pricedf.loc['USDT/USDC']


# #### WBTC/WETH

pricedf.loc['WBTC/WETH']


# #### LINK/USDT

pricedf.loc['LINK/USDT']


# #### WBTC/USDT

pricedf.loc['WBTC/USDT']


# #### BNT/USDC

pricedf.loc['BNT/USDC']


# #### WETH/DAI

pricedf.loc['WETH/DAI']


# #### LINK/USDC

pricedf.loc['LINK/USDC']


# #### DAI/USDC

pricedf.loc['DAI/USDC']


# #### WETH/USDT

pricedf.loc['WETH/USDT']


# #### DAI/USDT

pricedf.loc['DAI/USDT']


# #### PEPE/WETH

pricedf.loc['PEPE/WETH']


# #### LYXe/USDC

pricedf.loc['LYXe/USDC']


# #### rETH/WETH

pricedf.loc['rETH/WETH']


# #### 0x0/WETH

pricedf.loc['0x0/WETH']


# #### WBTC/USDC

pricedf.loc['WBTC/USDC']


# #### ARB/MATIC

pricedf.loc['ARB/MATIC']


# #### TSUKA/USDC

pricedf.loc['TSUKA/USDC']


# #### stETH/WETH

pricedf.loc['stETH/WETH']


raise

# + active=""
#
# -

# ## Execution 

# ### Configuration
#
# - `flt`: flashloanable tokens
# - `loglevel`: `LL_DEBUG` , `LL_INFO` `LL_WARN` `LL_ERR`

flt = [T.USDC]
C = Config.new(config=Config.CONFIG_TENDERLY, loglevel=Config.LL_INFO)

bot = CarbonBot(ConfigObj=C)

# ### Database update [Tenderly specific]

# provided here for convenience; must be commented out for tests
bot.update(drop_tables=True, top_n=10, only_carbon=False)

# ### Execution

bot.run(flashloan_tokens=flt, mode=bot.RUN_SINGLE)

# ## Execution analysis 

CCm = bot.get_curves()

# ### Arbitrage opportunities

ops = bot._find_arbitrage(flashloan_tokens=flt, CCm=CCm)["r"]
ops

# ### Route struct

try:
    route_struct = bot._run(flashloan_tokens=flt, CCm=CCm)
except bot.NoArbAvailable as e:
    print(f"[NoArbAvailable] {e}")
    route_struct = None
route_struct

# ### Orderering info

try:
    ordinfo = bot._run(flashloan_tokens=flt, CCm=CCm)
    flashloan_amount = ordinfo[1]
    flashloan_token_address = ordinfo[2]
    print(f"Flashloan: {flashloan_amount} [{flashloan_token_address}]")
except bot.NoArbAvailable as e:
    print(f"[NoArbAvailable] {e}")
    ordinfo = None
ordinfo

# ## Market analysis 

# ### Overall market

exch0 = {c.P("exchange") for c in CCm}
print("Number of curves:", len(CCm))
print("Number of tokens:", len(CCm.tokens()))
#print("Exchanges:", exch0)
print("---")
for xc in exch0:
    print(f"{xc+':':16} {len(CCm.byparams(exchange=xc)):4}")

# ### Pair

pair = f"{T.ECO}/{T.USDC}"

CCp = CCm.bypairs(pair)
exch = {c.P("exchange") for c in CCp}
print("pair:           ", pair)
print("curves:         ", len(CCp))
print("exchanges:      ", exch)
for xc in exch:
    c = CCp.byparams(exchange=xc)[0]
    print(f"{xc+':':16} {c.p:.4f} {1/c.p:.4f}")

# ## Technical 

# ### Validation and assertions

assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "tenderly"
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.PROVIDER == C.PROVIDER_TENDERLY
assert str(type(bot.db)) == "<class 'fastlane_bot.db.manager.DatabaseManager'>"
assert C.w3.provider.endpoint_uri.startswith("https://rpc.tenderly.co/fork/")
assert bot.db.carbon_controller.address == '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1'

# ### Tenderly shell commands
#
# Run those commands in a shell if there are Tenderly connection issues

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
c1, c2 = C_nw.shellcommand().splitlines()
print(c1)
print(c2)
# !{c1}
# !{c2}




