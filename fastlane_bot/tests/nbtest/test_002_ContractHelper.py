# ------------------------------------------------------------
# Auto generated test file `test_002_ContractHelper.py`
# ------------------------------------------------------------
# source file   = NBTest_002_ContractHelper.py
# source path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/ArbBot/resources/NBTest/
# test id       = 002
# test comment  = ContractHelper
# ------------------------------------------------------------





from fastlane_bot.db.updaters.helpers import ContractHelper
import fastlane_bot.config as c
import unittest
from web3.exceptions import InvalidAddress

contract_helper = ContractHelper(w3=c.w3)

print(f"Version: {contract_helper.__VERSION__.format('0.0.0')}")
print(f"Date: {contract_helper.__DATE__}")


assert isinstance(contract_helper, ContractHelper)
assert contract_helper.w3 == c.w3
assert isinstance(contract_helper.contracts, dict)

assert contract_helper.carbon_controller.address == c.CARBON_CONTROLLER_ADDRESS


contract = contract_helper.initialize_contract_with_abi(
    address=c.CARBON_CONTROLLER_ADDRESS, abi=c.CARBON_CONTROLLER_ABI, w3=c.w3
)

assert contract.address == c.CARBON_CONTROLLER_ADDRESS

test_case = unittest.TestCase()

invalid_address = "invalid_ethereum_address"

test_case.assertRaises(InvalidAddress, contract_helper.initialize_contract_with_abi, invalid_address, c.CARBON_CONTROLLER_ABI, c.w3)

contract = contract_helper.initialize_contract_without_abi(
    address=c.CARBON_CONTROLLER_ADDRESS, w3=c.w3
)

assert contract.address == c.CARBON_CONTROLLER_ADDRESS

test_case.assertRaises(ValueError, contract_helper.initialize_contract_without_abi, invalid_address, c.w3)

contract_with_abi = contract_helper.initialize_contract(
    address=c.CARBON_CONTROLLER_ADDRESS, _abi=c.CARBON_CONTROLLER_ABI, w3=c.w3
)

contract_without_abi = contract_helper.initialize_contract(
    address=c.CARBON_CONTROLLER_ADDRESS, w3=c.w3
)

assert contract_with_abi.address == c.CARBON_CONTROLLER_ADDRESS
assert contract_without_abi.address == c.CARBON_CONTROLLER_ADDRESS

test_case.assertRaises(InvalidAddress, contract_helper.initialize_contract, c.w3, invalid_address, c.CARBON_CONTROLLER_ABI)


contract = contract_helper.contract_from_address(
    exchange_name=c.UNISWAP_V2_NAME, pool_address='0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'
)

assert contract.address == '0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'

unsupported_exchange_name = "unsupported_exchange_name"

test_case.assertRaises(NotImplementedError, contract_helper.contract_from_address, unsupported_exchange_name, c.CARBON_CONTROLLER_ADDRESS)


contract = contract_helper.get_or_init_contract(
    exchange_name=c.UNISWAP_V2_NAME, pool_address='0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'
)

assert contract.address == '0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'
assert contract_helper.contracts[c.UNISWAP_V2_NAME]['0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'] == contract
assert len(contract_helper.contracts[c.UNISWAP_V2_NAME]) == 1
