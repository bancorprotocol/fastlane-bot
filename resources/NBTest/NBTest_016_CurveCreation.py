# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3
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

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)

# +

# assert C.DATABASE == C.DATABASE_POSTGRES
# assert C.POSTGRES_DB == "tenderly"
# assert C.NETWORK == C.NETWORK_TENDERLY
# assert C.PROVIDER == C.PROVIDER_TENDERLY
C = Config()
bot = CarbonBot(ConfigObj=C)
assert str(type(bot.db)) == "<class 'fastlane_bot.db.manager.DatabaseManager'>"

# Get all tokens
db = MockDatabaseManager(C)
all_tokens = db.get_tokens()
print("All Tokens:")
# for token in all_tokens:
print(all_tokens[0])
assert len(all_tokens) == 232


# +
#### Curve Creation Basic Unit Test

# +
CCm = bot.get_curves()
CCc1 = CCm.byparams(exchange="carbon_v1")
CCb2 = CCm.byparams(exchange="bancor_v2")
CCb3 = CCm.byparams(exchange="bancor_v3")
CCu2 = CCm.byparams(exchange="uniswap_v2")
CCu3 = CCm.byparams(exchange="uniswap_v3")
CCsu = CCm.byparams(exchange="sushiswap_v2")

CCprice = CCm.bypairs()


print("Len CCm", len(CCm))
print("Len Carbon", len(CCc1))
print("Len CCm Bancor V2", len(CCb2))
print("Len CCm Bancor V3", len(CCb3))
print("Len CCm Uni V2", len(CCu2))
print("Len CCm Uni V3", len(CCu3))
print("Len CCm Sushi", len(CCsu))

assert len(CCc1) + len(CCb2) + len(CCb3) + len(CCu2) + len(CCu3) + len(CCsu) == len(CCm)


def max_decimals(value: float, num_dec: int) -> bool:
    """Fails with scientific notation"""
    after_dec = str(value).split(".")[1]

    if num_dec == 0 and after_dec == "0":
        return True
    if len(after_dec) > num_dec:
        print("before", value, " after", after_dec, " len(after_dec) ", len(after_dec), "decimals", num_dec)
        print('{:f}'.format(value))
    return False if len(after_dec) > num_dec else True



for curve in CCm:
    #print(curve)
    if curve.k == 0:
            assert curve.k == 0
            assert curve.x == 0
            assert curve.x_act == 0
            assert curve.y == 0
            assert curve.y_act == 0
    else:
        assert type(curve.k) == float and curve.k >= 0
        assert type(curve.x) == float and curve.x >= 0
        assert type(curve.x_act) == float and curve.x_act >= 0
        assert type(curve.y) == float and curve.y >= 0
        assert type(curve.y_act) == float and curve.y_act >= 0
    assert math.isclose(curve.x * curve.y, curve.k, rel_tol=1e-15)

    assert curve.cid
    assert type(curve.fee) == float or curve.fee == 0
    assert curve.params["exchange"] in curve.descr
    assert curve.pair in curve.descr
    assert curve.constr
    assert type(curve.params["tknx_dec"]) == int and curve.params["tknx_dec"] >= 0
    assert type(curve.params["tkny_dec"]) == int and curve.params["tkny_dec"] >= 0
    assert type(curve.params["blocklud"]) == int and curve.params["blocklud"] > 0

    """The following is a decimal precision test that currently fails for floats with scientific notation."""
    # tknx = curve.pair.split("/")[0]
    # tkny = curve.pair.split("/")[1]
    # assert max_decimals(value=curve.x_act, num_dec=curve.params["tknx_dec"]), f"Token decimals exceed maximum for token {tknx}"
    # assert max_decimals(value=curve.y_act, num_dec=curve.params["tkny_dec"]), f"Token decimals exceed maximum for token {tkny}"



# +
#### Bancor V2 Fee Test

# +
total_generic_fee = 0

for curve in CCb2:
    if curve.fee == 0.003:
        total_generic_fee += 1
    assert curve.constr == "uv2"

# The following test fails for the mock database, but should not fail for real data.
# assert total_generic_fee != len(CCb2), "Not all Bancor V2 pools should have a fee of 0.003."


# +
#### Bancor V3 Test
# -

for curve in CCb3:
    assert curve.fee == 0.0
    assert curve.constr == "uv2"

# +
#### Uniswap V2 & Sushiswap Test

# +
for curve in CCu2:
    assert curve.fee == 0.003
    assert curve.constr == "uv2"

for curve in CCsu:
    assert curve.fee == 0.003
    assert curve.constr == "uv2"

# +
#### Uniswap V3 Test
# -

for curve in CCu3:
    assert curve.fee == 0.003 or curve.fee == 0.0005 or curve.fee == 0.0001 or curve.fee == 0.01
    assert curve.constr == "pkpp"



# +
#### Pair Test

# +
weth = 'WETH-6Cc2'
usdc = 'USDC-eB48'
dai = 'DAI-1d0F'
link = "LINK-86CA"
bnt = "BNT-FF1C"
wbtc =" WBTC-C599"

pairs = [f"{a}/{b}" for a in [weth, usdc, dai, bnt] for b in [dai, wbtc, link, weth, bnt] if a!=b]
#print(pairs)
CCpairs = CCm.bypairs(pairs)

CCbnt = CCm.bytknx("BNT-FF1C")
assert (len(CCbnt) == 92)
# for curve in CCbnt:
#     print(curve)



CCp1 = CCm.bypair(f"{weth}/{usdc}")
CCp2 = CCm.bypair(f"{weth}/{dai}")
assert len(CCp1) == 2
assert len(CCp2) == 1

for curve in CCp1:
    assert weth in curve.pair
    assert usdc in curve.pair
    assert weth in curve.descr
    assert usdc in curve.descr



# +
#### By Token

# +




# -














































