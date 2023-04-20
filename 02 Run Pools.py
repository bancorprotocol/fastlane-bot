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

from carbon.tools.cpc import T, CPCContainer
from fastlane_bot.bot import CarbonBot
flashloan_tokens = [T.WETH, T.DAI, T.USDC, T.USDT, T.WBTC, T.BNT]
import matplotlib.pyplot as plt
plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]


# # Carbon curves on mainnet

# +
#help(CarbonBot)

# +
# # Run the bot
# bot.run(flashloan_tokens=flashloan_tokens, update_pools=update_pools)

# +
# brownie networks set_provider alchemy
# -

# ## Load the curves

bot = CarbonBot()

CC0 = bot.get_curves()
print(len(CC0))

{c.P("exchange") for c in CC0}

# ## Carbon curves

curves = [c for c in CC0 if c.P("exchange")=='carbon_v1']
print(f"Num curves: {len(curves)}")
CC = CPCContainer(curves)
CC.plot()

# ## Uniswap v2

curves = [c for c in CC0 if c.P("exchange")=='uniswap_v2']
print(f"Num curves: {len(curves)}")
CC = CPCContainer(curves)
CC.plot()

# ## Bancor v3

curves = [c for c in CC0 if c.P("exchange")=='bancor_v3']
print(f"Num curves: {len(curves)}")
CC = CPCContainer(curves)
CC.plot()

# ## Uniswap v3

curves = [c for c in CC0 if c.P("exchange")=='uniswap_v3']
print(f"Num curves: {len(curves)}")
CC = CPCContainer(curves)
CC.plot()

# ## Sushiswap

curves = [c for c in CC0 if c.P("exchange")=='sushiswap_v2']
print(f"Num curves: {len(curves)}")
CC = CPCContainer(curves)
CC.plot()

import sqlalchemy


