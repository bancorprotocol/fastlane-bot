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
try:
    from fastlane_bot.tools.simplepair import SimplePair
    from fastlane_bot.tools.cpc import ConstantProductCurve, CPCContainer
    from fastlane_bot.tools.optimizer import PairOptimizer, MargPOptimizer
except:
    from tools.simplepair import SimplePair
    from tools.cpc import ConstantProductCurve, CPCContainer
    from tools.optimizer import PairOptimizer, MargPOptimizer
CPC = ConstantProductCurve

import pandas as pd

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SimplePair))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCContainer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(PairOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))
# -

# # Optimizer Testing

# This is a light workbook allowing to look at issues that may arise when running the optimizer on a specific set of curves. 
#
# Instructions:
#
# - locate the **exact** curve set to feed to the optimizer (it will be somewhere in the logging output, and it will be a list of ConstantProductCurve objects)
# - assign it to the `CurvesRaw` variable as shown below
# - add the missing token addresses to the `TOKENS` dict below
# - provide consistent values for `PSTART`
# - run the workbook

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
    ConstantProductCurve(k=27518385.40998667, x=1272.2926367501436, x_act=0, y_act=2000.9999995236503, alpha=0.5, pair='0x514910771AF9Ca656af840dff83E8264EcF986CA/0x8E870D67F660D95d5be530380D0eC0bd388289E1', cid='0x425d5d4ad7243f88d9f4cde8da52863b45af1f64e05bede1299909bcaa6c52d1-0', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 2000.9999995236503, 'yint': 2000.9999995236503, 'A': 0.38144823884371704, 'B': 3.7416573867739373, 'pa': 16.99999999999995, 'pb': 13.99999999999997}),
    ConstantProductCurve(k=6.160500599566333e+18, x=11099999985.149971, x_act=0, y_act=55.50000002646446, alpha=0.5, pair='0x8E870D67F660D95d5be530380D0eC0bd388289E1/0x514910771AF9Ca656af840dff83E8264EcF986CA', cid='0x425d5d4ad7243f88d9f4cde8da52863b45af1f64e05bede1299909bcaa6c52d1-1', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 55.50000002646446, 'yint': 55.50000002646446, 'A': 0, 'B': 0.22360678656963742, 'pa': 0.04999999999999889, 'pb': 0.04999999999999889}),
    ConstantProductCurve(k=14449532.299465338, x=57487.82879658422, x_act=0, y_act=5.0, alpha=0.5, pair='0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', cid='0x3fcccfe0063b71fc973fab8dea39b6be9da80125910c10e57b924b3e4687295a-0', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 5.0, 'yint': 8.582730309868262, 'A': 0.002257868117407469, 'B': 0.06480740698407672, 'pa': 0.004497751124437756, 'pb': 0.004199999999999756}),
    ConstantProductCurve(k=14456757.06563651, x=251.4750925240284, x_act=0, y_act=807.9145301701096, alpha=0.5, pair='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x514910771AF9Ca656af840dff83E8264EcF986CA', cid='0x3fcccfe0063b71fc973fab8dea39b6be9da80125910c10e57b924b3e4687295a-1', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 807.9145301701096, 'yint': 1974.7090228584536, 'A': 0.519359008452966, 'B': 14.907119849998594, 'pa': 237.97624997025295, 'pb': 222.22222222222211}),
    ConstantProductCurve(k=56087178.30932376, x=131.6236694086859, x_act=0, y_act=15920.776548455418, alpha=0.5, pair='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x8E870D67F660D95d5be530380D0eC0bd388289E1', cid='0x6cc4b198ec4cf17fdced081b5611279be73e200711238068b5340e606ba86646-0', fee=2000, descr='carbon_v1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 15920.776548455418, 'yint': 32755.67010983316, 'A': 4.373757425036729, 'B': 54.77225575051648, 'pa': 3498.2508745627138, 'pb': 2999.9999999999854}),
    ConstantProductCurve(k=56059148.73497429, x=426117.72306081816, x_act=0, y_act=5.0, alpha=0.5, pair='0x8E870D67F660D95d5be530380D0eC0bd388289E1/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', cid='0x6cc4b198ec4cf17fdced081b5611279be73e200711238068b5340e606ba86646-1', fee=2000, descr='carbon_v1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 5.0, 'yint': 10.106093048875099, 'A': 0.0013497708452092638, 'B': 0.016903085094568837, 'pa': 0.0003331667499582927, 'pb': 0.0002857142857142352})
]
CCRaw = CPCContainer(CurvesRaw)

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
# The price numeraire does not matter as long as they are all in the same numeraire. All tokens must be present. Additional tokens can be added and will be ignored. 

PRICES_RAW = {
    '0x8E870D67F660D95d5be530380D0eC0bd388289E1': 0.0003087360213944532, 
    '0x514910771AF9Ca656af840dff83E8264EcF986CA': 0.004372219704179475, 
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 1
}

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
# All tokens must be present. Additional tokens will be ignored. You must also provide the `TARGET_TOKEN` (default: first token of `TOKENS`)
#

# +
TOKENS = {
    "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE": "ETH",
    "0x514910771AF9Ca656af840dff83E8264EcF986CA": "LINK",
    "0x8E870D67F660D95d5be530380D0eC0bd388289E1": "USDP",
}

TARGET_TOKEN_RAW = list(TOKENS)[0]
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

def replace_tokens(dct):
    """replaces the token address with the token name in dct"""
    tkns = dct["pair"].split("/")
    for i in range(len(tkns)):
        #tkns[i] = TOKENS.get(tkns[i]) or tkns[i]
        tkns[i] = TOKENS[tkns[i]]
    dct["pair"] = "/".join(tkns)
    return dct


# If this fails this probably means that one of the tokens has not been defined above

CC = CPCContainer.from_dicts([replace_tokens(d) for d in CCRaw.asdicts()])
PRICES = {TOKENS[addr]:price for addr, price in PRICES_RAW.items()}
TARGET_TOKEN = TOKENS[TARGET_TOKEN_RAW]
PRICES


def p(pair=None, *, tknb=None, tknq=None, prices=None):
    "price of tknb in terms of tknq"
    if not pair is None:
        tknb, tknq = pair.split("/")
    p = prices or PRICES
    return p[tknb]/p[tknq]


# The code below ensures that in ETH/LINK, LINK is the quote token and ETH the base token (for better price displays)

SimplePair.NUMERAIRE_TOKENS["LINK"] = SimplePair.NUMERAIRE_TOKENS["ETH"] - 1
#SimplePair.NUMERAIRE_TOKENS

# ## Curves

print("Num curves:   ", len(CC))
print("Pairs:        ", set(c.pairo.primary_n for c in CC))
print("Target token: ", TARGET_TOKEN)

PRICE_DECIMALS = 2
curvedata = [dict(
    cid0 = f"{c.cid[2:6]}{c.cid[-2:]}",
    exch = c.params['exchange'],
    pair = c.pairo.primary_n,
    mktp = round(p(c.pairo.primary_n), PRICE_DECIMALS),
    bs = c.buysell(),
    tkn = c.pairo.primary_tknb,
    p = round(c.primaryp(), PRICE_DECIMALS),
    p_min = round(c.p_min_primary(), PRICE_DECIMALS),
    p_max = round(c.p_max_primary(), PRICE_DECIMALS),
    tknp = p(tknb=c.pairo.primary_tknb, tknq=TARGET_TOKEN),
    wbp = max(int((c.p_max_primary()/c.p_min_primary() - 1)*10000), 1),
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

# Curves 2,3 and 4,5 are overlapping ranges with good liquidity that serve as a market for curve 1 which is the operational curve in this arbitrage. In fact, what we expect is
#
# - Curve 0 (`425d-0`) buys LINK for USDP from 17 down to 14
# - Curves 2-5 (`3fcc` and `6cc4`) sell LINK for USDP (via ETH) at 14.16 and above
#
# The expected price is somewhat above 14, depending on the capacity of the overlapping curves 2-5

# The approximate effective LINK/USDP price from the overlapping curves (buy and sell)

3239.013043/228.716777

# The width of the overlapping ranges (2,3 and 4,5) in basis points

(228.716777/228.602476-1)*10000, (3239.013043/3237.394345-1)*10000

# For reference, the CID dataframe `ciddf` (separate because the field is too long; can be joined to `curvedf` via index)

ciddf = pd.DataFrame([dict(cid=c.cid) for c in CC])
ciddf

# +
#help(CC[0])

# +
#help(CC[0].pairo)
# -

# ## MargPOptimizer

O = MargPOptimizer(CC)
r = O.optimize(sfc="ETH", params=dict(
    pstart=PRICES,
    verbose=True,
    debug=True,
    debug_j=True,
    debug_dtkn=True,
    debug_dtkn2=True,
))
r


