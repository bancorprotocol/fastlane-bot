# ------------------------------------------------------------
# Auto generated test file `test_032_PricesMainnetTenderly.py`
# ------------------------------------------------------------
# source file   = NBTest_032_PricesMainnetTenderly.py
# test id       = 032
# test comment  = PricesMainnetTenderly
# ------------------------------------------------------------



from fastlane_bot import Bot, Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
from fastlane_bot.tools.analyzer import CPCAnalyzer
from fastlane_bot.tools.optimizer import CPCArbOptimizer
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCAnalyzer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *
import itertools as it
import collections as cl
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)




# ------------------------------------------------------------
# Test      032
# File      test_032_PricesMainnetTenderly.py
# Segment   Price estimates [NOTEST]
# ------------------------------------------------------------
def notest_price_estimates():
# ------------------------------------------------------------
    
    start_time = time.time()
    botm    = Bot()
    print(f"elapsed time: {time.time()-start_time:.2f}s")
    
    start_time = time.time()
    CCm     = botm.get_curves()
    print(f"elapsed time: {time.time()-start_time:.2f}s")
    
    # +
    # bott    = Bot() # --> change to Tenderly bot
    # CCt     = bott.get_curves()
    # -
    
    start_time = time.time()
    tokensm = CCm.tokens()
    prices_usdc = CCm.price_estimates(tknbs=tokensm, tknqs=f"{T.USDC}", raiseonerror=False)
    print(f"elapsed time: {time.time()-start_time:.2f}s")
    
    pricesdf = pd.DataFrame(prices_usdc, index=tokensm, columns=["USDC"]).sort_values("USDC", ascending=False)
    pricesdf
    
    print("TOKEN                       PRICE(USD)")
    print("======================================")
    for ix, d in pricesdf.iterrows():
        try:
            p = float(d)
            price = f"{p:12,.4f}"
            if p < 1:
                continue
        except:
            continue
        print(f"{ix:25} {price}")
    
    print("TOKEN                       PRICE(USc)")
    print("======================================")
    for ix, d in pricesdf.iterrows():
        try:
            p = float(d)
            price = f"{p*100:12,.6f}"
            if p >= 1.1:
                continue
        except:
            continue
        print(f"{ix:25} {price}")
    
    print("TOKEN                      UNAVAILABLE")
    print("======================================")
    for ix, d in pricesdf.iterrows():
        try:
            p = float(d)
            continue
        except:
            pass
        print(f"{ix:25}")
    
    