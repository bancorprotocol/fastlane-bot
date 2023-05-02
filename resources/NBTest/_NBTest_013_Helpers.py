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

from fastlane_bot import Config, Bot
#from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
from fastlane_bot.helpers import TradeInstruction, TxReceiptHandler, TxRouteHandler, TxSubmitHandler, TxHelpers, TxHelper
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TradeInstruction))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxReceiptHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxRouteHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxSubmitHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxHelpers))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxHelper))
from fastlane_bot.testing import *
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)

# # Helpers [NBTest013]

# +
# C = Config()
C = Config.new(config=Config.CONFIG_UNITTEST)
bot = Bot(ConfigObj=C)
arb_data_struct = [{'exchangeId': 6,
  'targetToken': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
  'minTargetAmount': 1,
  'deadline': 1683013903,
  'customAddress': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
  'customInt': 0,
  'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000050000000000000000000000000000000500000000000000000000000000000000000000000000000000000004a9dfd4e6'},
 {'exchangeId': 4,
  'targetToken': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  'minTargetAmount': 1,
  'deadline': 1683013903,
  'customAddress': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  'customInt': 100,
  'customData': '0x'}]
flash_tkn = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
flash_amt = 20029887718

arb_data_struct_weth_test = [{'exchangeId': 4,
  'targetToken': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  'minTargetAmount': 1,
  'deadline': 1683013903,
  'customAddress': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  'customInt': 100,
  'customData': '0x'}, {'exchangeId': 6,
  'targetToken': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
  'minTargetAmount': 1,
  'deadline': 1683013903,
  'customAddress': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
  'customInt': 0,
  'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000050000000000000000000000000000000500000000000000000000000000000000000000000000000000000004a9dfd4e6'}]
flash_tkn_weth_test = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
flash_amt_weth_test = 20029887718
# -

# ## TradeInstruction

# ## TxReceiptHandler
#
# Note: `TxReceiptHandler` is currently a dummy class. No tests to do.

h = TxReceiptHandler()
assert type(h).__name__ == "TxReceiptHandler"
assert type(h).__bases__[0].__name__ == "TxReceiptHandlerBase"

# +
#help(h)

# +
#help(h)
# -

# ## TxSubmitHandler

h = TxSubmitHandler(ConfigObj=C)
assert type(h).__name__ == "TxSubmitHandler"
assert type(h).__bases__[0].__name__ == "TxSubmitHandlerBase"

help(h)

# ## TradeInstruction

# +
ti0 = TradeInstruction(ConfigObj=C, cid='1701411834604692317316873037158841057285-1', tknin="USDC-eB48", amtin=20029.887718107937, tknout='WETH-6Cc2', amtout=-10.0, db=bot.db)
ti1 = TradeInstruction(ConfigObj=C, cid='10548753374549092367364612830384814555378', tknin="WETH-6Cc2", amtin=9.899999894800894, tknout='USDC-eB48', amtout=-20977.111871615052, db=bot.db)
assert type(ti0).__name__ == "TradeInstruction"
assert type(ti1).__name__ == "TradeInstruction"

assert ti0.tknin_key
assert ti0.tknout_key
assert ti0.is_carbon == True, "The first order is a Carbon order"
assert ti1.is_carbon == False, "The second order is not a Carbon order"
assert type(ti0._amtin_wei) == int
assert type(ti0._amtout_wei) == int
assert type(ti0._amtin_quantized) == Decimal
assert ti0._amtin_quantized > 0
assert type(ti0._amtout_quantized) == Decimal
assert ti0._amtout_quantized < 0
assert ti0.exchange_id == 6
assert ti1.exchange_id == 4
assert ti0.exchange_name == C.CARBON_V1_NAME
assert ti1.exchange_name == C.UNISWAP_V3_NAME


assert str(ti0._tknin_address) == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
assert str(ti0._tknout_address) == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"



assert ti0._tknin_decimals == 6
assert ti0._tknout_decimals == 18
assert ti0._tknin_address != ti1._tknin_address
assert ti0._tknout_address != ti1._tknout_address


assert ti0.raw_txs == "[]"
assert ti1.raw_txs == "[]"


# +
#help(h)
# -

# ## TxRouteHandler

# + jupyter={"outputs_hidden": false}
h = TxRouteHandler(ConfigObj=C, trade_instructions=[ti0, ti1])
assert type(h).__name__ == "TxRouteHandler"
assert type(h).__bases__[0].__name__ == "TxRouteHandlerBase"
assert h.contains_carbon
assert h.exchange_ids == [6, 4]
assert h.is_weth(h.trade_instructions[0].tknout_address)
assert not h.is_weth(h.trade_instructions[0].tknin_address)


# -

# ## TxHelpers

# +
h = TxHelpers(ConfigObj=C)
assert type(h).__name__ == "TxHelpers"

"""Currently skipping for TxHelper"""

# -

help(h)

# ## TxHelper

# +
h = TxHelper(ConfigObj=C)
assert type(h).__name__ == "TxHelper"
assert h.w3.__class__.__name__ == "Web3"
assert h.w3.isConnected()
assert h.PRIVATE_KEY
assert type(h.COINGECKO_URL) == str
# This indicates the arb contract is correctly instantiated. These values can change, but the default is 50% rewards for the caller, and 100 BNT max profit.
assert h.arb_contract.caller.rewards() == (500000,100000000000000000000)
assert (h.wallet_address), "Address not loading. Check that .env file has field ETH_PRIVATE_KEY_BE_CAREFUL"
assert (h.wallet_balance)
assert type(h.wei_balance) == int
# print(h.ether_balance, type(h.ether_balance))
# assert type(h.ether_balance) == float #TODO currently returns Decimal, expected float
assert h.nonce >= 0 and type(h.nonce) == int

assert h.gas_limit >= 0 # this also tests the function get_gas_limit_from_usd
assert h.base_gas_price >=0 # this includes 0 to account for the 0 gas price on Tenderly
assert type(h.base_gas_price) == int
assert type(h.gas_price_gwei) == float
assert h.gas_price_gwei * 1000000000 == h.base_gas_price

assert type(h.ether_price_usd) == float
assert h.deadline > h.w3.eth.getBlock('latest')['timestamp'] + C.DEFAULT_BLOCKTIME_DEVIATION - 1

flash_tkn_normal = h.submit_flashloan_arb_tx(arb_data=arb_data_struct, flashloan_token_address=flash_tkn, flashloan_amount=flash_amt, verbose=False, result=h.XS_WETH)
flash_tkn_weth = h.submit_flashloan_arb_tx(arb_data=arb_data_struct_weth_test, flashloan_token_address=flash_tkn_weth_test, flashloan_amount=flash_amt_weth_test, verbose=False, result=h.XS_WETH)

assert flash_tkn_normal == flash_tkn
assert flash_tkn_weth == C.ETH_ADDRESS

transaction = h.submit_flashloan_arb_tx(arb_data=arb_data_struct, flashloan_token_address=flash_tkn, flashloan_amount=flash_amt, verbose=False, result=h.XS_TRANSACTION)

# TODO these values should change for EIP 1559 style transactions
assert transaction['value'] == 0
assert transaction['chainId'] >= 0
assert transaction['gas'] > 0
assert transaction['nonce'] >= 0
assert transaction['to'] == C.FASTLANE_CONTRACT_ADDRESS
assert transaction['data'] is not None

signed_transaction = h.submit_flashloan_arb_tx(arb_data=arb_data_struct, flashloan_token_address=flash_tkn, flashloan_amount=flash_amt, verbose=False, result=h.XS_SIGNED)
assert signed_transaction


# -

help(h)


