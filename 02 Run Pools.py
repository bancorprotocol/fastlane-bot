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

from fastlane_bot.tools.cpc import T, CPCContainer, ConstantProductCurve as CPC
from fastlane_bot.bot import CarbonBot, CarbonBotBase
flashloan_tokens = [T.WETH, T.DAI, T.USDC, T.USDT, T.WBTC, T.BNT]
import matplotlib.pyplot as plt
plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]


# # Carbon curves on mainnet

help(CarbonBot)

# +
# # Run the bot
# bot.run(flashloan_tokens=flashloan_tokens, update_pools=update_pools)

# +
# brownie networks set_provider alchemy
# -

d = {'inputs': [{'components': [{'internalType': 'uint16',
     'name': 'exchangeId',
     'type': 'uint16'},
    {'internalType': 'contract Token',
     'name': 'targetToken',
     'type': 'address'},
    {'internalType': 'uint256', 'name': 'minTargetAmount', 'type': 'uint256'},
    {'internalType': 'uint256', 'name': 'deadline', 'type': 'uint256'},
    {'internalType': 'address', 'name': 'customAddress', 'type': 'address'},
    {'internalType': 'uint256', 'name': 'customInt', 'type': 'uint256'},
    {'internalType': 'bytes', 'name': 'customData', 'type': 'bytes'}],
   'internalType': 'struct BancorArbitrage.Route[]',
   'name': 'routes',
   'type': 'tuple[]'},
  {'internalType': 'contract Token', 'name': 'token', 'type': 'address'},
  {'internalType': 'uint256', 'name': 'sourceAmount', 'type': 'uint256'}]}

import json
FAST_LANE_CONTRACT_ABI = json.loads(
    """
    [{"inputs":[],"name":"AccessDenied","type":"error"},{"inputs":[],"name":"InvalidAddress","type":"error"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"previousAdmin","type":"address"},{"indexed":false,"internalType":"address","name":"newAdmin","type":"address"}],"name":"AdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"beacon","type":"address"}],"name":"BeaconUpgraded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"implementation","type":"address"}],"name":"Upgraded","type":"event"},{"stateMutability":"payable","type":"fallback"},{"inputs":[],"name":"admin","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"implementation","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"}],"name":"upgradeTo","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"upgradeToAndCall","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"},{"inputs":[],"name":"AlreadyInitialized","type":"error"},{"inputs":[],"name":"InvalidETHAmountSent","type":"error"},{"inputs":[],"name":"InvalidExchangeId","type":"error"},{"inputs":[],"name":"InvalidFee","type":"error"},{"inputs":[],"name":"InvalidFlashLoanCaller","type":"error"},{"inputs":[],"name":"InvalidInitialAndFinalTokens","type":"error"},{"inputs":[],"name":"InvalidRouteLength","type":"error"},{"inputs":[],"name":"InvalidSourceToken","type":"error"},{"inputs":[],"name":"MinTargetAmountTooHigh","type":"error"},{"inputs":[],"name":"Overflow","type":"error"},{"inputs":[],"name":"ZeroValue","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"caller","type":"address"},{"indexed":false,"internalType":"uint16[]","name":"exchangeIds","type":"uint16[]"},{"indexed":false,"internalType":"address[]","name":"tokenPath","type":"address[]"},{"indexed":false,"internalType":"uint256","name":"sourceAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"burnAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"rewardAmount","type":"uint256"}],"name":"ArbitrageExecuted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"prevPercentagePPM","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"newPercentagePPM","type":"uint32"},{"indexed":false,"internalType":"uint256","name":"prevMaxAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newMaxAmount","type":"uint256"}],"name":"RewardsUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"EXCHANGE_ID_BANCOR_V2","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"EXCHANGE_ID_BANCOR_V3","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"EXCHANGE_ID_CARBON","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"EXCHANGE_ID_SUSHISWAP","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"EXCHANGE_ID_UNISWAP_V2","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"EXCHANGE_ID_UNISWAP_V3","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"uint16","name":"exchangeId","type":"uint16"},{"internalType":"contract Token","name":"targetToken","type":"address"},{"internalType":"uint256","name":"minTargetAmount","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"address","name":"customAddress","type":"address"},{"internalType":"uint256","name":"customInt","type":"uint256"},{"internalType":"bytes","name":"customData","type":"bytes"}],"internalType":"struct BancorArbitrage.Route[]","name":"routes","type":"tuple[]"},{"internalType":"contract Token","name":"token","type":"address"},{"internalType":"uint256","name":"sourceAmount","type":"uint256"}],"name":"flashloanAndArb","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"uint16","name":"exchangeId","type":"uint16"},{"internalType":"contract Token","name":"targetToken","type":"address"},{"internalType":"uint256","name":"minTargetAmount","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"address","name":"customAddress","type":"address"},{"internalType":"uint256","name":"customInt","type":"uint256"},{"internalType":"bytes","name":"customData","type":"bytes"}],"internalType":"struct BancorArbitrage.Route[]","name":"routes","type":"tuple[]"},{"internalType":"contract Token","name":"token","type":"address"},{"internalType":"uint256","name":"sourceAmount","type":"uint256"}],"name":"fundAndArb","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"getRoleMember","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleMemberCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"caller","type":"address"},{"internalType":"contract IERC20","name":"erc20Token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"feeAmount","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"onFlashLoan","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"data","type":"bytes"}],"name":"postUpgrade","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rewards","outputs":[{"components":[{"internalType":"uint32","name":"percentagePPM","type":"uint32"},{"internalType":"uint256","name":"maxAmount","type":"uint256"}],"internalType":"struct BancorArbitrage.Rewards","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"roleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"pure","type":"function"},{"inputs":[{"components":[{"internalType":"uint32","name":"percentagePPM","type":"uint32"},{"internalType":"uint256","name":"maxAmount","type":"uint256"}],"internalType":"struct BancorArbitrage.Rewards","name":"newRewards","type":"tuple"}],"name":"setRewards","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"logic","type":"address"},{"internalType":"address","name":"initAdmin","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"stateMutability":"payable","type":"constructor"}]
    """
)
FAST_LANE_CONTRACT_ABI
for i, r in enumerate(FAST_LANE_CONTRACT_ABI):
    print(i, r["name"])

FAST_LANE_CONTRACT_ABI





d

d["inputs"]

d["inputs"][0]

d["inputs"][0]["components"]

d["inputs"][0].keys()



d["inputs"][1]

dd = {
    "inputs": {
      "Route":[
            {
            "exhangeId": 255,
            "targetToken": "0x....",
            "minTargetAmount": 1,
            "deadline": 16700700,
            'customAddress': "0x...",
            "customInt": 1234566,
            "customData": b"12234455",
        }, {
            "exhangeId": 255,
            "targetToken": "0x....",
            "minTargetAmount": 1,
            "deadline": 16700700,
            'customAddress': "0x...",
            "customInt": 1234566,
            "customData": b"12234455",

        }],
        "Token": "0x00",
        "sourceAmount": 122334,
    }
}
dd

dd = {
    "inputs": {
      "Route": [asdict(rt) for rt in routes],
        "Token": "0x00",
        "sourceAmount": 122334,
    }
}





d = {'inputs': [{'components': [{'internalType': 'uint16',
      'name': 'exchangeId',
      'type': 'uint16'},
     {'internalType': 'contract Token',
      'name': 'targetToken',
      'type': 'address'},
     {'internalType': 'uint256', 'name': 'minTargetAmount', 'type': 'uint256'},
     {'internalType': 'uint256', 'name': 'deadline', 'type': 'uint256'},
     {'internalType': 'address', 'name': 'customAddress', 'type': 'address'},
     {'internalType': 'uint256', 'name': 'customInt', 'type': 'uint256'},
     {'internalType': 'bytes', 'name': 'customData', 'type': 'bytes'}],
    'internalType': 'struct BancorArbitrage.Route[]',
    'name': 'routes',
    'type': 'tuple[]'},
   {'internalType': 'contract Token', 'name': 'token', 'type': 'address'},
   {'internalType': 'uint256', 'name': 'sourceAmount', 'type': 'uint256'}],
  'name': 'flashloanAndArb',
  'outputs': [],
  'stateMutability': 'nonpayable',
  'type': 'function'}
di = d["inputs"]
di

di[0].keys()

di[0]["name"], di[0]["type"], di[0]["internalType"], 

# +
#     exchangeId: int  # TODO: WHY IS THIS AN INT?
#     targetToken: str
#     minTargetAmount: int
#     deadline: int
#     customAddress: str
#     customInt: int
#     customData: bytes
# -

di[0]["components"]

",".join([x["name"] for x in di[0]["components"]])

{
            "exhangeId": 255,
            "targetToken": "0x....",
            "minTargetAmount": 1,
            "deadline": 16700700,
            'customAddress': "0x...",
            "customInt": 1234566,
            "customData": b"12234455",
}


ddd = {
      "exchangeId": 2,
      "targetToken": "0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c",
      "minTargetAmount": "1",
      "deadline": "1681972764",
      "customAddress": "0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c",
      "customInt": "0",
      "customData": ""
}
ddd

",".join([x for x in ddd])

"exchangeId,targetToken,minTargetAmount,deadline,customAddress,customInt,customData" == 'exchangeId,targetToken,minTargetAmount,deadline,customAddress,customInt,customData'



di[1]

di[2]

raise

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


