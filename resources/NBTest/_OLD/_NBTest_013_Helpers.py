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
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from fastlane_bot import Config, Bot

# from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
from fastlane_bot.helpers import (
    TradeInstruction,
    TxReceiptHandler,
    TxRouteHandler,
    TxSubmitHandler,
    TxHelpers,
    TxHelper,
)

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TradeInstruction))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxReceiptHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxRouteHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxSubmitHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxHelpers))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxHelper))
from fastlane_bot.testing import *

plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]
from fastlane_bot import __VERSION__

require("2.0", __VERSION__)

# # Helpers [NBTest013]

# +
# C = Config()
C = Config.new(config=Config.CONFIG_UNITTEST)
bot = Bot(ConfigObj=C)

arb_data_struct = [
    {
        "exchangeId": 6,
        "targetToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "minTargetAmount": 1,
        "deadline": 1683013903,
        "customAddress": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "customInt": 0,
        "customData": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000050000000000000000000000000000000500000000000000000000000000000000000000000000000000000004a9dfd4e6",
    },
    {
        "exchangeId": 4,
        "targetToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "minTargetAmount": 1,
        "deadline": 1683013903,
        "customAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "customInt": 100,
        "customData": "0x",
    },
]
flash_tkn = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
flash_amt = 20029887718
profit = 19348  # totally made up!

arb_data_struct_weth_test = [
    {
        "exchangeId": 4,
        "targetToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "minTargetAmount": 1,
        "deadline": 1683013903,
        "customAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "customInt": 100,
        "customData": "0x",
    },
    {
        "exchangeId": 6,
        "targetToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "minTargetAmount": 1,
        "deadline": 1683013903,
        "customAddress": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "customInt": 0,
        "customData": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000050000000000000000000000000000000500000000000000000000000000000000000000000000000000000004a9dfd4e6",
    },
]
flash_tkn_weth_test = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
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
# help(h)

# +
# help(h)
# -

# ## TxSubmitHandler

h = TxSubmitHandler(ConfigObj=C)
assert type(h).__name__ == "TxSubmitHandler"
assert type(h).__bases__[0].__name__ == "TxSubmitHandlerBase"

help(h)

# ## TradeInstruction

ti0 = TradeInstruction(
    ConfigObj=C,
    cid="1701411834604692317316873037158841057285-1",
    tknin="USDC-eB48",
    amtin=20029.887718107937,
    tknout="WETH-6Cc2",
    amtout=-10.0,
    db=bot.db,
)
ti1 = TradeInstruction(
    ConfigObj=C,
    cid="10548753374549092367364612830384814555378",
    tknin="WETH-6Cc2",
    amtin=9.899999894800894,
    tknout="USDC-eB48",
    amtout=-20977.111871615052,
    db=bot.db,
    exchange_override="uniswap_v2",
)
assert type(ti0).__name__ == "TradeInstruction"
assert type(ti1).__name__ == "TradeInstruction"
assert ti0.tknin_key == "USDC-eB48"
assert ti0.tknout_key == "WETH-6Cc2"
assert ti0.is_carbon == True, "The first order is a Carbon order"
assert ti1.is_carbon == False, "The second order is not a Carbon order"
assert (
    type(ti0._amtin_wei) == int
), f"_amtin_wei is of type: {type(ti0._amtin_wei)}, expected int"
assert (
    type(ti0._amtout_wei) == int
), f"_amtout_wei is of type: {type(ti0._amtout_wei)}, expected int"
assert (
    type(ti0._amtin_quantized) == Decimal
), f"_amtin_quantized returning wrong type: {type(ti0._amtin_quantized)}, expected Decimal"
assert (
    ti0._amtin_quantized > 0
), f"_amtin_quantized = {ti0._amtout_quantized}, expected a positive number in"
assert (
    type(ti0._amtout_quantized) == Decimal
), f"_amtin_quantized returning wrong type: {type(ti1._amtin_quantized)}, expected Decimal"
assert (
    ti0._amtout_quantized < 0
), f"_amtin_quantized = {ti0._amtout_quantized}, expected a negative number out"
assert ti0.exchange_id == 6, f"wrong exchange id for ti0: {ti0.exchange_id}, expected 6"
assert ti1.exchange_id == 3, f"wrong exchange id for ti1: {ti1.exchange_id}, expected 3"
assert (
    ti0.exchange_name == C.CARBON_V1_NAME
), f"wrong exchange name for ti0: {ti0.exchange_name}, expected {C.CARBON_V1_NAME}"
assert (
    ti1.exchange_name == C.UNISWAP_V2_NAME
), f"wrong exchange name for ti1: {ti1.exchange_name}, expected {C.UNISWAP_V2_NAME}"
assert (
    str(ti0._tknin_address) == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
), f"wrong token in address for ti0: {ti0._tknin_address}, expected: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
assert (
    str(ti0._tknout_address) == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
), f"wrong token in address for ti0: {ti1._tknin_address}, expected: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
assert (
    ti0._tknin_decimals == 6
), f"wrong decimals for ti0 in: {ti0._tknin_decimals}, expected 6"
assert (
    ti0._tknout_decimals == 18
), f"wrong decimals for ti0 out: {ti0._tknout_decimals}, expected 18"
assert (
    ti0._tknin_address != ti1._tknin_address
), f"ti0 tknin address == ti1 tkin address, order mismatch!"
assert (
    ti0._tknout_address != ti1._tknout_address
), f"ti0 tknout address == ti1 tkout address, order mismatch!"
assert ti0.raw_txs == "[]", "ti0 raw tx should not be populated yet"
assert ti1.raw_txs == "[]", "ti1 raw tx should not be populated yet"


# +
# help(h)
# -

# ## TxRouteHandler

# ### initialization

# + jupyter={"outputs_hidden": false}
eth = "ETH-EEeE"
weth = "WETH-6Cc2"
usdc = "USDC-eB48"
dai = "DAI-1d0F"
link = "LINK-86CA"
bnt = "BNT-FF1C"
wbtc = " WBTC-C599"

tx_route_h = TxRouteHandler(trade_instructions=[ti0, ti1])
assert type(tx_route_h).__name__ == "TxRouteHandler"
assert type(tx_route_h).__bases__[0].__name__ == "TxRouteHandlerBase"
assert tx_route_h.contains_carbon, "No orders in route that contain a Carbon order"
assert (
    6 in tx_route_h.exchange_ids and 3 in tx_route_h.exchange_ids
), "Exchange ids missing from txRouteHandler"
assert tx_route_h.is_wrapped_gas_token(
    tx_route_h.trade_instructions[0].tknout_address
), f"TxRouteHandler is_weth returned: {tx_route_h.is_wrapped_gas_token(h.trade_instructions[0].tknout_address)}, expected True"
assert not tx_route_h.is_wrapped_gas_token(
    tx_route_h.trade_instructions[0].tknin_address
), f"TxRouteHandler is_weth returned: {tx_route_h.is_wrapped_gas_token(h.trade_instructions[0].tknin_address)}, expected False"


uni_v2_pool = bot.db.get_pool(exchange_name="uniswap_v2", pair_name=f"{usdc}/{weth}")
uni_v3_pool = bot.db.get_pool(exchange_name="uniswap_v3", pair_name=f"{usdc}/{weth}")
carbon_pool = bot.db.get_pool(id="4")
print(uni_v2_pool)
print(uni_v3_pool)
print(carbon_pool)

# -

# ### custom_data_encoder


# ### _abi_encode_data


# ### to_route_struct


# ### get_route_structs


# ### get_arb_contract_args


# ### _get_trade_dicts_from_objects


# ### _slice_dataframe


# ### _aggregate_carbon_trades


# ### _find_tradematches


# ### _determine_trade_route


# ### _extract_route_index


# ### _find_match_for_tkn


# ### _find_match_for_amount


# ### _match_trade


# ### _reorder_trade_instructions


# ### _calc_amount0


# ### _calc_amount1


# ### _swap_token0_in


# ### _calc_uniswap_v3_output


# ### _decodeFloat and decode


# ### _get_input_trade_by_target_carbon

# +
print(carbon_pool)


# -

# ### _get_output_trade_by_source_carbon

# +
tkn0_key = carbon_pool.pair_name.split("/")[0]
tkn1_key = carbon_pool.pair_name.split("/")[1]

y0, z0 = (
    Decimal(carbon_pool.y_0) / Decimal("10") ** Decimal(str(6)),
    Decimal(carbon_pool.z_0) / Decimal("10") ** Decimal(str(6)),
)
A0, B0 = tx_route_h.decode_decimal_adjustment(
    Decimal(str(tx_route_h.decode(carbon_pool.A_0))), 18, 6
), tx_route_h.decode_decimal_adjustment(
    Decimal(str(tx_route_h.decode(carbon_pool.B_0))), 18, 6
)

y1, z1 = (
    Decimal(carbon_pool.y_1) / Decimal("10") ** Decimal(str(18)),
    Decimal(carbon_pool.z_1) / Decimal("10") ** Decimal(str(18)),
)
A1, B1 = tx_route_h.decode_decimal_adjustment(
    Decimal(str(tx_route_h.decode(carbon_pool.A_1))), 6, 18
), tx_route_h.decode_decimal_adjustment(
    Decimal(str(tx_route_h.decode(carbon_pool.B_1))), 6, 18
)

assert y0 == Decimal(
    "20"
), f"y0 calculation error. Expected 20, got: {y0} for curve {carbon_pool}. Probably a token decimal issue."
assert z0 == Decimal(
    "20"
), f"z0 calculation error. Expected 20, got: {z0} for curve {carbon_pool}. Probably a token decimal issue."
assert A0 == Decimal(
    "0"
), f"A0 calculation error. Expected 0, got: {A0} for curve {carbon_pool}. Probably a token decimal issue."
assert B0 == Decimal(
    "0.9995003722451656000000"
), f"B0 calculation error. Expected 0.9995003722451656000000, got: {B0} for curve {carbon_pool}. Probably a token decimal issue."
assert y1 == Decimal(
    "30"
), f"y0 calculation error. Expected 20, got: {y1} for curve {carbon_pool}. Probably a token decimal issue."
assert z1 == Decimal(
    "30"
), f"z0 calculation error. Expected 20, got: {z1} for curve {carbon_pool}. Probably a token decimal issue."
assert A1 == Decimal(
    "0"
), f"A0 calculation error. Expected 0, got: {A1} for curve {carbon_pool}. Probably a token decimal issue."
assert B1 == Decimal(
    "0.9994998749374598"
), f"B0 calculation error. Expected 0.9995003722451656000000, got: {B1} for curve {carbon_pool}. Probably a token decimal issue."


# Test putting in a normal trade into curve
tkns_in1, tkns_out1 = tx_route_h._get_output_trade_by_source_carbon(
    y=y0, z=z0, A=A0, B=B0, fee=0.002, tkns_in=12
)

assert tkns_in1 == Decimal(
    "12"
), f"Tokens in unexpected result, expected 12 got: {tkns_in1}"
assert tkns_out1 == Decimal(
    "11.96403590555985781993903135536615936"
), f"Tokens out unexpected result, expected 11.96403590555985781993903135536615936 got: {tkns_out1}"

# Test putting in more than maximum possible tokens
tkns_in2, tkns_out2 = tx_route_h._get_output_trade_by_source_carbon(
    y=y0, z=z0, A=A0, B=B0, fee=0.002, tkns_in=35
)
assert tkns_in2 == Decimal(
    "20.0200000978508971124688381089495090130576819926368108623102590650634788487027"
), f"Tokens in unexpected result, expected 20.0200000978508971124688381089495090130576819926368108623102590650634788487027 got: {tkns_in2}"
assert tkns_out2 == Decimal(
    "19.960"
), f"Tokens out unexpected result, expected 19.960 got: {tkns_out2}"

# Test putting in a normal trade into second curve
tkns_in3, tkns_out3 = tx_route_h._get_output_trade_by_source_carbon(
    y=y1, z=z1, A=A1, B=B1, fee=0.002, tkns_in=12
)
assert tkns_in3 == Decimal(
    "12"
), f"Tokens in unexpected result, expected 12 got: {tkns_in3}"
assert tkns_out3 == Decimal(
    "11.96402399999997342332740024875369504"
), f"Tokens out unexpected result, expected 11.96402399999997342332740024875369504 got: {tkns_out3}"

# Test putting in more than maximum possible tokens into second curve
tkns_in4, tkns_out4 = tx_route_h._get_output_trade_by_source_carbon(
    y=y1, z=z1, A=A1, B=B1, fee=0.002, tkns_in=35
)

assert tkns_in4 == Decimal(
    "30.0300300300300967382108451811838747252089617651151212896828272680233632092172"
), f"Tokens in unexpected result, expected 30.0300300300300967382108451811838747252089617651151212896828272680233632092172 got: {tkns_in4}"
assert tkns_out4 == Decimal(
    "29.940"
), f"Tokens out unexpected result, expected 29.940 got: {tkns_out4}"


# -

# ### _calc_carbon_output

# +
print(carbon_pool)

tkn0_key = carbon_pool.pair_name.split("/")[0]
tkn1_key = carbon_pool.pair_name.split("/")[1]

print(tkn0_key, tkn1_key)

output = tx_route_h._calc_carbon_output(
    curve=carbon_pool, tkn_in=dai, tkn_out_decimals=18, amount_in=15
)
output


# -

# ### single_trade_result_constant_product

# +
tkn0_amt = tx_route_h._from_wei_to_decimals(
    tkn0_amt=Decimal(uni_v2_pool.tkn0_balance), tkn0_decimals=6
)
tkn1_amt = tx_route_h._from_wei_to_decimals(
    tkn0_amt=Decimal(uni_v2_pool.tkn1_balance), tkn0_decimals=18
)
fee = uni_v2_pool.fee

assert tkn0_amt == Decimal(
    "36261493.395747"
), f"Balance of Uniswap V2 pool id=170 tkn0 changed, expected 36261493.395747, received: {tkn0_amt}"
assert tkn1_amt == Decimal(
    "18592.465452538740235568"
), f"Balance of Uniswap V2 pool id=170 tkn1 changed, expected 18592.465452538740235568, received: {tkn1_amt}"
assert (
    fee == "0.003"
), f"Fee for Uniswap V2 pool id=170 tkn0 changed, expected 0.003, received: {fee}"
output = tx_route_h.single_trade_result_constant_product(
    tokens_in=1500, token0_amt=tkn0_amt, token1_amt=tkn1_amt, fee=fee
)

assert output == Decimal(
    "0.766760531344682608637070737092913621544992522112938784489488080993164585482453"
)


# -

# ### _solve_trade_output


# ### _calculate_trade_outputs


# ### _from_wei_to_decimals

assert (
    tx_route_h._from_wei_to_decimals(tkn0_amt=1000000000000000000, tkn0_decimals=18)
    == 1
), f"_from_wei_to_decimals error, input: tkn0_amt=1000000000000000000, tkn0_decimals=18, output={tx_route_h._from_wei_to_decimals(tkn0_amt=1000000000000000000, tkn0_decimals=18)}, expected: 1"
assert (
    not tx_route_h._from_wei_to_decimals(tkn0_amt=1000000000000000000, tkn0_decimals=18)
    == 0.1
)
assert (
    tx_route_h._from_wei_to_decimals(tkn0_amt=500, tkn0_decimals=0) == 500
), f"_from_wei_to_decimals error, input: tkn0_amt=500, tkn0_decimals=0, output={tx_route_h._from_wei_to_decimals(tkn0_amt=1000000000000000000, tkn0_decimals=18)}, expected: 500"
assert not tx_route_h._from_wei_to_decimals(tkn0_amt=500, tkn0_decimals=0) == 50

# ### _cid_to_pool

assert (
    tx_route_h._cid_to_pool(cid=9868188640707215440437863615521278132498, db=bot.db)
    is not None
), "DB updated? Expected pool at cid 9868188640707215440437863615521278132498"
assert (
    tx_route_h._cid_to_pool(cid=777, db=bot.db) == None
), "DB updated? Expected no pool at cid 777"


# ## TxHelpers

# +
h = TxHelpers(ConfigObj=C)
assert type(h).__name__ == "TxHelpers"
assert h.web3.__class__.__name__ == "Web3"
assert h.web3.isConnected()


# This indicates the arb contract is correctly instantiated. These values can change, but the default is 50% rewards for the caller, and 100 BNT max profit.
assert h.arb_contract.caller.rewards() == (500000, 100000000000000000000)
assert (
    len(h.wallet_address) > 2
), "Address not loading. Check that .env file has field ETH_PRIVATE_KEY_BE_CAREFUL"
assert h.get_nonce() >= 0 and type(h.get_nonce()) == int


# Tests the database function to get BNT/ETH liquidity for gas calculations. This is now in the _run function that has direct access to the database.
pool = bot.db.get_pool(
    exchange_name=bot.ConfigObj.BANCOR_V3_NAME, pair_name="BNT-FF1C/ETH-EEeE"
)
bnt_eth = (int(pool.tkn0_balance), int(pool.tkn1_balance))
bnt, eth = bnt_eth

assert bnt > 100
assert eth > 1000


# -

# ### Function & API Unit Tests

# +
assert h._get_headers == {
    "accept": "application/json",
    "content-type": "application/json",
}
assert h._get_payload(method="eth_estimateGas") == {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "eth_estimateGas",
    "params": None,
}
assert h._get_payload(method="eth_sendPrivateTransaction", params="BigArbHunting") == {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "eth_sendPrivateTransaction",
    "params": "BigArbHunting",
}
assert h._get_payload(method="other") == {"id": 1, "jsonrpc": "2.0", "method": "other"}
assert h.get_max_priority_fee_per_gas_alchemy() > 100
assert h.get_eth_gas_price_alchemy() > 100

assert "https://eth-mainnet.alchemyapi.io/v2/" in h._get_alchemy_url

tx_boilerplate = h.build_tx(nonce=8, gas_price=1995, max_priority_fee=100)
assert (
    tx_boilerplate["type"] == "0x2"
    and tx_boilerplate["maxFeePerGas"] == 1995
    and tx_boilerplate["maxPriorityFeePerGas"] == 100
    and tx_boilerplate["nonce"] == 8
)


bnt, eth = 15437763684982513550130685, 3886561157532864487485
gas_price, gas_estimate = 98188186533, 515000

assert h.estimate_gas_in_bnt(
    gas_price=gas_price, gas_estimate=gas_estimate, bnt=bnt, eth=eth
) == Decimal(
    "200.856250253259717372280939534167761272845814437633248811441035398506141985836"
)

# Cf = Config()
# h = TxHelpers(ConfigObj=Cf)
# print(h.get_bnt_tkn_liquidity())


bnt, eth = int(bnt_eth[0]), int(bnt_eth[1])


# -

# ### submit_private_transaction


# ### validate_and_submit_transaction

route_struct = [
    {
        "exchangeId": 6,
        "targetToken": C.w3.to_checksum_address(
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
        ),
        "minTargetAmount": 1,
        "deadline": 171820341414141144,
        "customAddress": C.w3.to_checksum_address(
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
        ),
        "customInt": 0,
        "customData": "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000c00000000000000000000000000000048000000000000000000000000000000000000000000000000000000012a05f200",
    },
    {
        "exchangeId": 2,
        "targetToken": C.w3.to_checksum_address(
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        ),
        "minTargetAmount": 1,
        "deadline": 171820341414141144,
        "customAddress": C.w3.to_checksum_address(
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        ),
        "customInt": 0,
        "customData": "0x",
    },
]
flashloan_token_address = C.w3.to_checksum_address(
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
)
flashloan_amount = 5000000000

# +
(
    gas_price,
    current_max_priority_gas,
    current_block,
    nonce,
) = h.validate_and_submit_transaction(
    route_struct=route_struct,
    src_amt=flashloan_amount,
    src_address=flashloan_token_address,
    expected_profit=profit,
    result=h.XS_API_CALLS,
)

print(
    f"Result of API calls: current_gas_price={gas_price}, current_max_priority_gas={current_max_priority_gas}, block_number={current_block}, nonce={nonce}"
)
assert gas_price > 1000
assert current_max_priority_gas > 100
assert current_block > 17182034, "current block is less than the timestamped block"
assert (
    nonce >= 0
), "nonce not found, private key in .env file may need to be configured or added"

"""
Beyond this point it is not possible to test without real data. build_transaction_with_gas fails without a transaction that is expected to succeed.
"""

# transaction_built = h.validate_and_submit_transaction(route_struct=arb_data_struct, src_amt=flash_amt, src_address=flash_tkn, expected_profit=profit, result=h.XS_TRANSACTION)
#
# print(f"transaction built = {transaction_built}")
#
# adj_profit, gas_cost_bnt = h.validate_and_submit_transaction(route_struct=arb_data_struct, src_amt=flash_amt, src_address=flash_tkn, expected_profit=profit, result=h.XS_MIN_PROFIT_CHECK)
#
# print(f"adjusted profit = {adj_profit}, gas cost in bnt = {gas_cost_bnt}, transaction will submit? {adj_profit > gas_cost_bnt}")

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
assert h.arb_contract.caller.rewards() == (500000, 100000000000000000000)
assert (
    len(h.wallet_address) > 2
), "Address not loading. Check that .env file has field ETH_PRIVATE_KEY_BE_CAREFUL"
assert h.wallet_balance[0] >= 0, "Wallet balance not loading"
assert h.wei_balance >= 0 and type(h.wei_balance) == int
# print(h.ether_balance, type(h.ether_balance))
# assert type(h.ether_balance) == float #TODO currently returns Decimal, expected float

assert type(h.base_gas_price) == int

assert h.ether_price_usd > 0
assert h.gas_price_gwei >= 0
assert h.gas_price_gwei * 1000000000 == h.base_gas_price
assert h.nonce >= 0 and type(h.nonce) == int
assert h.gas_limit >= 0  # this also tests the function get_gas_limit_from_usd
assert (
    h.base_gas_price >= 0
)  # this includes 0 to account for the 0 gas price on Tenderly

assert (
    h.deadline
    > h.w3.eth.getBlock("latest")["timestamp"] + C.DEFAULT_BLOCKTIME_DEVIATION - 1
)

flash_tkn_normal = h.submit_flashloan_arb_tx(
    arb_data=arb_data_struct,
    flashloan_token_address=flash_tkn,
    flashloan_amount=flash_amt,
    verbose=False,
    result=h.XS_WETH,
)
flash_tkn_weth = h.submit_flashloan_arb_tx(
    arb_data=arb_data_struct_weth_test,
    flashloan_token_address=flash_tkn_weth_test,
    flashloan_amount=flash_amt_weth_test,
    verbose=False,
    result=h.XS_WETH,
)

assert flash_tkn_normal == flash_tkn
assert flash_tkn_weth == C.ETH_ADDRESS

transaction = h.submit_flashloan_arb_tx(
    arb_data=arb_data_struct,
    flashloan_token_address=flash_tkn,
    flashloan_amount=flash_amt,
    verbose=False,
    result=h.XS_TRANSACTION,
)

# TODO these values should change for EIP 1559 style transactions
assert transaction["value"] == 0
assert transaction["chainId"] >= 0
assert transaction["gas"] > 0
assert transaction["nonce"] >= 0
assert transaction["to"] == C.FASTLANE_CONTRACT_ADDRESS
assert transaction["data"] is not None

signed_transaction = h.submit_flashloan_arb_tx(
    arb_data=arb_data_struct,
    flashloan_token_address=flash_tkn,
    flashloan_amount=flash_amt,
    verbose=False,
    result=h.XS_SIGNED,
)
assert signed_transaction


# -

help(h)
