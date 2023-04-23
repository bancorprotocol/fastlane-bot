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

import fastlane_bot as flb
from fastlane_bot.bot import CarbonBot

# # SKL Testing

#bot = flb.Bot()
bot = CarbonBot()

# +
#bot.run()
# -

CCm = bot.get_curves()
len(CCm)

len(CCm)

help(bot._find_arbitrage_opportunities)

bot._find_arbitrage_opportunities()


