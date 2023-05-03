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

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonBot))
from fastlane_bot.testing import *
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
## Curve Unit Test

# +
CCm = bot.get_curves()
CCc1 = CCm.byparams(exchange="carbon_v1")
CCb2 = CCm.byparams(exchange="bancor_v2")
CCb3 = CCm.byparams(exchange="bancor_v3")
CCu2 = CCm.byparams(exchange="uniswap_v2")
CCu3 = CCm.byparams(exchange="uniswap_v3")
CCsu = CCm.byparams(exchange="sushiswap_v2")


print("Len CCm", len(CCm))
print("Len Carbon", len(CCc1))
print("Len CCm Bancor V2", len(CCb2))
print("Len CCm Bancor V3", len(CCb3))
print("Len CCm Uni V2", len(CCu2))
print("Len CCm Uni V3", len(CCu3))
print("Len CCm Sushi", len(CCsu))

assert len(CCc1) + len(CCb2) + len(CCb3) + len(CCu2) + len(CCu3) + len(CCsu) == len(CCm)

for curve in CCm:
    print(curve)
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
    assert curve.pair
    assert curve.cid
    assert type(curve.fee) == float or curve.fee == 0
    assert curve.descr
    assert curve.constr
    assert curve.params
    assert curve.params["exchange"]
    assert type(curve.params["tknx_dec"]) == int and curve.params["tknx_dec"] >= 0
    assert type(curve.params["tkny_dec"]) == int and curve.params["tkny_dec"] >= 0
    assert curve.params["tknx_addr"]
    assert curve.params["tkny_addr"]
    assert type(curve.params["blocklud"]) == int and curve.params["blocklud"] > 0


for curve in CCb3:
    assert curve.fee == 0.0

for curve in CCu3:
    assert curve.fee == 0.003 or curve.fee == 0.0005 or curve.fee == 0.0001 or curve.fee == 0.01

for curve in CCu2:
    assert curve.fee == 0.003

for curve in CCsu:
    assert curve.fee == 0.003


# -








































































