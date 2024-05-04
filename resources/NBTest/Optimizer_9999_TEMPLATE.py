# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
from tools.curves import ConstantProductCurve, CurveContainer, SimplePair
from tools.optimizer import CPCArbOptimizer, PairOptimizer, MargPOptimizer
CPC = ConstantProductCurve

import pandas as pd

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SimplePair))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CurveContainer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(PairOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))
# -

# # Optimizer Testing (TEMPLATE)

# This is a light workbook allowing to look at issues that may arise when running the optimizer on a specific set of curves. 
#
# Instructions:
#
# - locate the **exact** curve set to feed to the optimizer (it will be somewhere in the logging output, and it will be a list of ConstantProductCurve objects)
# - assign it to the `CurvesRaw` variable as shown below
# - add the missing token addresses to the `TOKENS` dict below
# - provide consistent values for `PSTART`
# - run the workbook
# - if the import statement fails, ensure `fastlane_bot` is on the path, or create symlink to `tools`

# ### >> Enter curves
#
# Place curves here in the form
#
#     CurvesRaw = [
#         ConstantProductCurve(k=27518385.40998667, x=1272.2926367501436, x_act=0, ...),
#         ConstantProductCurve(k=6.160500599566333e+18, x=11099999985.149971, x_act=0, ...),
#     ...
#     ]

CurvesRaw = [
    CPC.from_pk(pair="ETH_/USDP_",  cid="ETH/USDP1",  p=2000,   k=1),   # 1E+$2000 @ 2000
    # CPC.from_pk(pair="ETH_/USDP_",  cid="ETH/USDP1",  p=2000,   k=1*2000*1),   # 1E+$2000 @ 2000
    # CPC.from_pk(pair="ETH_/USDP_",  cid="ETH/USDP1",  p=3000,   k=1*3000*1),   # 1E+$2000 @ 2000
    CPC.from_pk(pair="LINK_/USDP_", cid="LINK/USDP1", p=  10,   k=100*1000), # 200L+$2000 @ 10
    CPC.from_pk(pair="LINK_/USDP_", cid="LINK/USDP1", p=  15,   k=100*1500), # 200L+$2000 @ 10
    # CPC.from_pk(pair="ETH_/LINK_",  cid="ETH/LINK1", p=  210,   k=1*210*0.0000000000001),    # ~1E @ 210
]
CCRaw = CurveContainer(CurvesRaw)

# +
# CurvesRaw = [
#     ConstantProductCurve(k=27518385.40998667, x=1272.2926367501436, x_act=0, y_act=2000.9999995236503, alpha=0.5, pair='0x514910771AF9Ca656af840dff83E8264EcF986CA/0x8E870D67F660D95d5be530380D0eC0bd388289E1', cid='0x425d5d4ad7243f88d9f4cde8da52863b45af1f64e05bede1299909bcaa6c52d1-0', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 2000.9999995236503, 'yint': 2000.9999995236503, 'A': 0.38144823884371704, 'B': 3.7416573867739373, 'pa': 16.99999999999995, 'pb': 13.99999999999997}),
#     ConstantProductCurve(k=6.160500599566333e+18, x=11099999985.149971, x_act=0, y_act=55.50000002646446, alpha=0.5, pair='0x8E870D67F660D95d5be530380D0eC0bd388289E1/0x514910771AF9Ca656af840dff83E8264EcF986CA', cid='0x425d5d4ad7243f88d9f4cde8da52863b45af1f64e05bede1299909bcaa6c52d1-1', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 55.50000002646446, 'yint': 55.50000002646446, 'A': 0, 'B': 0.22360678656963742, 'pa': 0.04999999999999889, 'pb': 0.04999999999999889}),
#     ConstantProductCurve(k=14449532.299465338, x=57487.82879658422, x_act=0, y_act=5.0, alpha=0.5, pair='0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', cid='0x3fcccfe0063b71fc973fab8dea39b6be9da80125910c10e57b924b3e4687295a-0', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 5.0, 'yint': 8.582730309868262, 'A': 0.002257868117407469, 'B': 0.06480740698407672, 'pa': 0.004497751124437756, 'pb': 0.004199999999999756}),
#     ConstantProductCurve(k=14456757.06563651, x=251.4750925240284, x_act=0, y_act=807.9145301701096, alpha=0.5, pair='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x514910771AF9Ca656af840dff83E8264EcF986CA', cid='0x3fcccfe0063b71fc973fab8dea39b6be9da80125910c10e57b924b3e4687295a-1', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 807.9145301701096, 'yint': 1974.7090228584536, 'A': 0.519359008452966, 'B': 14.907119849998594, 'pa': 237.97624997025295, 'pb': 222.22222222222211}),
#     ConstantProductCurve(k=56087178.30932376, x=131.6236694086859, x_act=0, y_act=15920.776548455418, alpha=0.5, pair='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x8E870D67F660D95d5be530380D0eC0bd388289E1', cid='0x6cc4b198ec4cf17fdced081b5611279be73e200711238068b5340e606ba86646-0', fee=2000, descr='carbon_v1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 15920.776548455418, 'yint': 32755.67010983316, 'A': 4.373757425036729, 'B': 54.77225575051648, 'pa': 3498.2508745627138, 'pb': 2999.9999999999854}),
#     ConstantProductCurve(k=56059148.73497429, x=426117.72306081816, x_act=0, y_act=5.0, alpha=0.5, pair='0x8E870D67F660D95d5be530380D0eC0bd388289E1/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', cid='0x6cc4b198ec4cf17fdced081b5611279be73e200711238068b5340e606ba86646-1', fee=2000, descr='carbon_v1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 5.0, 'yint': 10.106093048875099, 'A': 0.0013497708452092638, 'B': 0.016903085094568837, 'pa': 0.0003331667499582927, 'pb': 0.0002857142857142352})
# ]
# CCRaw = CurveContainer(CurvesRaw)
# -

# ### >> Enter prices
#
# Provide current prices (`pstart`) here, in the format
#
#     PRICES = {
#         '0x8E87...': 0.0003087360213944532, 
#         '0x5149...': 0.004372219704179475, 
#         '0xEeee...': 1
#     }
#     
# The price numeraire does not matter as long as they are all in the same numeraire. All tokens must be present. Additional tokens can be added and will be ignored. The keys in the dict here must correspond exactly to the 
# keys that are used in the pairs in the curves above.

PRICES_RAW = {
    'ETH_': 1950, 
    'LINK_':  11, 
    'USDP_':   1
}

# +
# PRICES_RAW = {
#     '0x8E870D67F660D95d5be530380D0eC0bd388289E1': 0.0003087360213944532, 
#     '0x514910771AF9Ca656af840dff83E8264EcF986CA': 0.004372219704179475, 
#     '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 1
# }
# -

# ### >> Enter tokens
#
# Provide token tickers here, in the format
#
#     TOKENS = {
#         "0x5149...": "LINK",
#         "0x8E87...": "USDP",
#         "0xEeee...": "ETH",
#     }
#     
# All tokens must be present. Additional tokens will be ignored. You must also provide the `TARGET_TOKEN_RAW`,
# for example by picking from the token list

# +
# TOKENS = {
#     "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE": "ETH",
#     "0x514910771AF9Ca656af840dff83E8264EcF986CA": "LINK",
#     "0x8E870D67F660D95d5be530380D0eC0bd388289E1": "USDP",
# }

# TARGET_TOKEN_RAW = list(TOKENS)[0]
# TARGET_TOKEN_RAW

# +
TOKENS = {
    "ETH_": "ETH",
    "LINK_": "LINK",
    "USDP_": "USDP",
}

TARGET_TOKEN_RAW = list(TOKENS)[-1]
TARGET_TOKEN_RAW
# -

# ### >>> Run optimizer
#
# please make sure that this line runs without errors (other than the error that needs to be addressed of course)

O = MargPOptimizer(CCRaw)
r = O.optimize(sfc=TARGET_TOKEN_RAW, params=dict(pstart=PRICES_RAW))
r


# **do not worry about the code below here; this is for the actual testing and will be adapted as need be**

# ### >>> Preprocessing
#
# Please ensure that this code runs without error. Errors here mean that the data provided above is not consistent.

# +
def replace_tokens(dct):
    """replaces the token address with the token name in dct"""
    tkns = dct["pair"].split("/")
    for i in range(len(tkns)):
        #tkns[i] = TOKENS.get(tkns[i]) or tkns[i]
        tkns[i] = TOKENS[tkns[i]]
    dct["pair"] = "/".join(tkns)
    return dct

def p(pair=None, *, tknb=None, tknq=None, prices=None):
    "price of tknb in terms of tknq"
    if not pair is None:
        tknb, tknq = pair.split("/")
    p = prices or PRICES
    return p[tknb]/p[tknq]

def round_(x, *args):
    "forgiving round()"
    try:
        return round(x, *args)
    except:
        return x

def wbp(c):
    "width of the range in bp [0 means infty]"
    try:
        return max(int((c.p_max_primary()/c.p_min_primary() - 1)*10000), 1)
    except:
        return 0
    
def cid0(c):
    "shortened cid (for standard format ones)"
    if len(c.cid) < 20: return c.cid
    return f"{c.cid[2:6]}{c.cid[-2:]}"


# -

# If this fails this probably means that one of the tokens has not been defined above

CC = CurveContainer.from_dicts([replace_tokens(d) for d in CCRaw.asdicts()])
PRICES = {TOKENS[addr]:price for addr, price in PRICES_RAW.items()}
TARGET_TOKEN = TOKENS[TARGET_TOKEN_RAW]
PRICES

# Here you can change the preference order of numeraire tokens (in a pair, the one with the lower number will be chosen as numeraire; tokens not present here are considered to have higher numbers; draw means alphabetic order). 
#
# The specific code below ensures that in ETH/LINK, LINK is the quote token and ETH the base token. As LINK is not in the list, otherwise this would be the other way round.

SimplePair.NUMERAIRE_TOKENS["LINK"] = SimplePair.NUMERAIRE_TOKENS["ETH"] - 1
#SimplePair.NUMERAIRE_TOKENS

# ## Curves

print("Num curves:   ", len(CC))
print("Pairs:        ", set(c.pairo.primary_n for c in CC))
print("Target token: ", TARGET_TOKEN)

PRICE_DECIMALS = 2
curvedata = [dict(
    cid0 = cid0(c),
    exch = c.params.get('exchange', "na"),
    pair = c.pairo.primary_n,
    mktp = round(p(c.pairo.primary_n), PRICE_DECIMALS),
    bs = c.buysell(),
    tkn = c.pairo.primary_tknb,
    p = round_(c.primaryp(), PRICE_DECIMALS),
    p_min = round_(c.p_min_primary(), PRICE_DECIMALS),
    p_max = round_(c.p_max_primary(), PRICE_DECIMALS),
    tknp = p(tknb=c.pairo.primary_tknb, tknq=TARGET_TOKEN),
    wbp = wbp(c),
    liq = round(c.tvl(tkn=c.pairo.primary_tknb), 2),
    liqtt = round(c.x_act*p(tknb=c.tknx, tknq=TARGET_TOKEN) + c.y_act*p(tknb=c.tkny, tknq=TARGET_TOKEN), 2),
) for c in CC]
#curvedata

# - `cid0`: shortened CID (same as in `debug_tkn2`)
# - `exch`: the type of the curve / exchange in question
# - `pair`: the normalized pair of the curve
# - `mktp`: the current market price of that pair (according to `PRICES_RAW`)
# - `bs`: whether curves buys ("b"),  sells ("s") the primary tokenm, or both
# - `tkn`: the primary token (base token of primary pair)
# - `p`, `p_min`, `p_max`: the current / minimum / maximum price of the curve
# - `tknp`: the price of `tkn` (as above) in terms of `TARGET_TOKEN`, as per the market price
# - `wbp`: width of the range (p_max/p_min) in basis points 
# - `liq`: liquidity (in units of `tkn` as defined above; converted at curve price)
# - `liqtt`: total curve liquidity (in `TARGET_TOKEN` units; converted at `mktp`)
#

curvedf = pd.DataFrame(curvedata)
curvedf

# For reference, the CID dataframe `ciddf` (separate because the field is too long; can be joined to `curvedf` via index)

ciddf = pd.DataFrame([dict(cid=c.cid) for c in CC])
ciddf

# ## MargPOptimizer

O = MargPOptimizer(CC)
r = O.optimize(sfc=TARGET_TOKEN, params=dict(
    pstart=PRICES,
    verbose=True,
    debug=False,
    debug_j=True,
    debug_dtkn=False,
    debug_dtkn2=False,
    debug_dtknd=True,
))
r

raise

# ### Explanation
#
# Convergence criterium is "relative" with given epsilon using L2 norm (unit does not matter here)
#
#     [margp_optimizer] crit=rel (eps=1e-06, unit=1, norm=L2)
#
# Base token is `USDP`; the prices and their inverses shown in order `ETH`, `LINK`
#
#     [margp_optimizer] USDP <- ETH, LINK
#     [margp_optimizer] p    1,950.00, 11.00
#     [margp_optimizer] 1/p  0.00, 0.09
#     
# Jacobian explainer: quote token us USDP
# `dETH/d%pLINK` means the change in ETH (in ETH units) when the `LINK/USDP` price changes by 1%
#
#     [margp_optimizer]
#     ============= JACOBIAN% =============>>>
#     tknq USDP
#     dETH/d%pETH, dLINK/d%pETH
#     dETH/d%pLINK, dLINK/d%pLINK
#     <<<============= JACOBIAN% =============
#
# Actual Jacobian in the same format as the explainer
#
#     [margp_optimizer]
#     ============= JACOBIAN% =============>>>
#     [[-0.01045332  0.005415  ]
#      [ 0.95994502 -1.90864222]]
#     <<<============= JACOBIAN% =============
#     
# Results of cycle 0
#
#     [margp_optimizer]
#     ========== cycle 0 =======>>>
#     USDP <- ETH, LINK
#     dtkn   0.101, -26.364
#     log p0 [3.290034611362518, 1.0413926851582251]
#     d logp [ 0.01472711 -0.05228352]
#     log p  [3.30476172 0.98910917]
#     p_t      (2017.2592691917046, 9.752347514669442) USDP
#     p        2,017.26, 9.75
#     1/p      0.00, 0.10
#     crit     5.43e-02 [1; L2], eps=1e-06, c/e=5e+04]
#     dtkn_d   {'ETH': 0.10113974590360497, 'USDP': 72.4594621534543, 'LINK': -26.36377863280171}
#     <<<========== cycle 0 =======


