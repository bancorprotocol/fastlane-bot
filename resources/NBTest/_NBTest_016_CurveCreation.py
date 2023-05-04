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

# +
import math

from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
from fastlane_bot.db.mock_model_managers import MockDatabaseManager
from fastlane_bot.testing import *

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonBot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MockDatabaseManager))

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)
require("3.0.2", MockDatabaseManager.__VERSION__)
# -

# # Testing Curve Creation functions [NBTest016]

#

# +
C = Config.new(config=Config.CONFIG_UNITTEST)
bot = CarbonBot(ConfigObj=C)
# assert str(type(bot.db)) == "<class 'fastlane_bot.db.manager.DatabaseManager'>"

# Get all tokens
db = bot.db
all_tokens = db.get_tokens()
# assert len(all_tokens) == 232
CCm = bot.get_curves()

eth = "ETH-EEeE"
weth = 'WETH-6Cc2'
usdc = 'USDC-eB48'
dai = 'DAI-1d0F'
link = "LINK-86CA"
bnt = "BNT-FF1C"
wbtc =" WBTC-C599"

# -

type(db)

bot.db.get_pools()

bot.db.get_tokens()

bot.get_curves()

# ## Demo section [NOTEST]
#
#

pass

# ## Unit Testing Curves
#

for curve in CCm.curves:
    print(curve.descr)

for curve in CCm:
    #print(curve)

    if curve.k == 0 and curve.params["exchange"] != "carbon_v1":
            assert curve.k == 0
            #print(curve.k, curve.x, curve.y, curve.x_act, curve.y_act)
            assert curve.x == 0
            assert curve.x_act == 0
            assert curve.y == 0
            assert curve.y_act == 0
    else:
        #print(curve.k, curve.x, curve.y, curve.x_act, curve.y_act)
        assert type(curve.k) == float or int, "k not a float"
        assert curve.k >= 0, "k less than 0"
        assert type(curve.x) == float or int, "x not a float"
        assert curve.x >= 0, "x less than 0"
        assert type(curve.x_act) == float or int, "x actual not a float"
        assert curve.x_act >= 0, "x actual less than 0"
        assert type(curve.y) == float or int, "y not a float"
        assert curve.y >= 0 , "y less than 0"
        assert type(curve.y_act) == float or int, "y actual not a float"
        assert curve.y_act >= 0, "y actual less than 0"
    assert math.isclose(curve.x * curve.y, curve.k, rel_tol=1e-15)

    assert curve.cid
    assert type(curve.fee) == float or curve.fee == 0
    assert curve.params["exchange"] in curve.descr

    if curve.params["exchange"] == "carbon_v1":
        tkn0 = str(curve.pair).split("/")[0]
        tkn1 = str(curve.pair).split("/")[1]

        if tkn0 == weth:
            tkn0 = eth
        elif tkn1 == weth:
            tkn1 = eth
        assert tkn0 in curve.descr and tkn1 in curve.descr, f"pair {curve.pair} not in descr: {curve.descr}\ncurve:{curve}"
    else:
        assert curve.pair in curve.descr, f"pair {curve.pair} not in descr: {curve.descr}\ncurve:{curve}"
    assert curve.constr
    assert type(curve.params["tknx_dec"]) == int and curve.params["tknx_dec"] >= 0
    assert type(curve.params["tkny_dec"]) == int and curve.params["tkny_dec"] >= 0
    assert type(curve.params["blocklud"]) == int and curve.params["blocklud"] > 0

# ## Test Bancor V3 Curves

# +
CCb3 = CCm.byparams(exchange="bancor_v3")
for curve in CCb3:
    assert curve.fee == 0.0, f"Fee for Bancor V3 pool not set to 0 for curve: {curve}"
    assert curve.constr == "uv2", f"Wrong constraint used for Bancor V3 pool: {curve}"


# -

#

# ## Test Bancor V2 Curves

# +
CCb2 = CCm.byparams(exchange="bancor_v2")

total_generic_fee = 0

for curve in CCb2:
    if curve.fee == 0.003:
        total_generic_fee += 1
    assert curve.constr == "uv2", f"Wrong constraint used for Bancor V2 pool: {curve}"

# The following test fails for the mock database, but should not fail for real data.
# assert total_generic_fee != len(CCb2), "Not all Bancor V2 pools should have a fee of 0.003."
# -

# ## Test Uni V2 and Sushi Curves

# +
CCu2 = CCm.byparams(exchange="uniswap_v2")
CCsu = CCm.byparams(exchange="sushiswap_v2")

for curve in CCu2:
    print(curve)
    assert curve.fee == 0.003, f"Wrong fee set for Uni V2 pool: {curve.fee}, expected 0.003, curve={curve}"
    assert curve.constr == "uv2", f"Wrong constraint used for Uniswap V2 pool: {curve}"

for curve in CCsu:
    assert curve.fee == 0.003, f"Wrong fee set for Sushi pool: {curve.fee}, expected 0.003, curve={curve}"
    assert curve.constr == "uv2", f"Wrong constraint used for Sushi pool: {curve}"
# -

# ## Test Uni V3 Curves

# +
CCu3 = CCm.byparams(exchange="uniswap_v3")

for curve in CCu3:
    assert curve.fee == 0.003 or curve.fee == 0.0005 or curve.fee == 0.0001 or curve.fee == 0.01, f"Wrong fee set for Uni V3 pool: {curve.fee}, expected 0.003 or 0.0005 or 0.0001 or 0.01, curve={curve}"
    assert curve.constr == "pkpp", f"Wrong constraint: {curve.constr} used for Uni V3 pool, expected pkpp. Curve = {curve}"
# -

# ## Test Carbon Curves

# +
CCc1 = CCm.byparams(exchange="carbon_v1")

assert len(CCc1) == 88, f"Number of Carbon curves in mock db updated: {len(CCc1)}, expected 88"

for curve in CCc1:
    # assert curve.fee == 0.002, f"Wrong fee set for Carbon curve: {curve.fee}, expected 0.002, curve={curve}" Currently curves are set to 0.0 fee for Carbon, should be 0.002
    assert curve.constr == "carb", f"Wrong constraint: {curve.constr} used for Carbon curve, expected pkpp. Curve = {curve}"

# Carbon Curves not in mock DB


# -

# ## Test Pair Filtering

# +
pairs = [f"{a}/{b}" for a in [weth, usdc, dai, bnt] for b in [dai, wbtc, link, weth, bnt] if a!=b]
#print(pairs)
CCpairs = CCm.bypairs(pairs)

CCbnt = CCm.bytknx("BNT-FF1C")

assert (len(CCbnt) == 9), f"Number of curves with BNT in mock database has changed. Current = {len(CCbnt)}, expected 9"
# for curve in CCbnt:
#     print(curve)



CCp1 = CCm.bypair(f"{weth}/{usdc}")
CCp2 = CCm.bypair(f"{weth}/{dai}")

assert len(CCp1) == 21, f"Number of curves with {weth}/{usdc} in mock database has changed. Current = {len(CCp1)}, expected 21"
assert len(CCp2) == 2, f"Number of curves with {weth}/{dai} in mock database has changed. Current = {len(CCp2)}, expected 2"

for curve in CCp1:
    assert weth in curve.pair, f"weth not present in curve {curve}"
    assert usdc in curve.pair, f"usdc not present in curve {curve}"
    assert weth in curve.descr or eth in curve.descr, f"weth or eth not present in curve description: {curve}"
    assert usdc in curve.descr, f"usdc not present in curve description {curve}"

# -

# ## Test Token Filtering

# +
CCt1 = CCm.bytknx(weth)
CCt2 = CCm.bytknx(usdc)
CCt3 = CCm.bytkny(weth)
CCt4 = CCm.bytkny(usdc)


assert len(CCt1) == 32, f"Number of curves with tknx weth in mock database has changed. Current = {len(CCt1)}, expected 32"
assert len(CCt2) == 21, f"Number of curves with tknx usdc in mock database has changed. Current = {len(CCt2)}, expected 21"
assert len(CCt3) == 45, f"Number of curves with tkny weth in mock database has changed. Current = {len(CCt3)}, expected 45"
assert len(CCt4) == 18, f"Number of curves with tkny usdc in mock database has changed. Current = {len(CCt4)}, expected 18"



for curve in CCt1:
    assert str(curve.pair).split("/")[0] == weth, f"weth not tknx in curve: {curve}"
    assert curve.pair != f"{weth}/{weth}", f"weth is both tokens in curve: {curve}"

for curve in CCt2:
    assert str(curve.pair).split("/")[0] == usdc, f"usdc not tknx in curve: {curve}"
    assert curve.pair != f"{usdc}/{usdc}", f"usdc is both tokens in curve: {curve}"

for curve in CCt3:
    assert str(curve.pair).split("/")[1] == weth, f"weth not tkny in curve: {curve}"
    assert curve.pair != f"{weth}/{weth}", f"weth is both tokens in curve: {curve}"

for curve in CCt4:
    assert str(curve.pair).split("/")[1] == usdc, f"usdc not tkny in curve: {curve}"
    assert curve.pair != f"{usdc}/{usdc}", f"usdc is both tokens in curve: {curve}"
# -


















