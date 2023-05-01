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

# # Unit tests for ContractHelper

# + jupyter={"outputs_hidden": false}
from fastlane_bot.db.updaters.helpers import ContractHelper
import fastlane_bot.config as c
import unittest
from web3.exceptions import InvalidAddress

# +
# Create a ContractHelper instance
contract_helper = ContractHelper(w3=c.w3)

# Print and format version and date
print(f"Version: {contract_helper.__VERSION__.format('0.0.0')}")
print(f"Date: {contract_helper.__DATE__}")

# + jupyter={"outputs_hidden": false}
# 1. Test initialization of ContractHelper
#    - Test if ContractHelper instance is properly created with the given parameters.

assert isinstance(contract_helper, ContractHelper)
assert contract_helper.w3 == c.w3
assert isinstance(contract_helper.contracts, dict)

# + jupyter={"outputs_hidden": false}
# 2. Test carbon_controller property
#   - Test if the CarbonController contract is returned correctly.
assert contract_helper.carbon_controller.address == c.CARBON_CONTROLLER_ADDRESS

# + jupyter={"outputs_hidden": false}

# 3. Test initialize_contract_with_abi function
#    - Test if the function returns a Contract object when given valid parameters.
contract = contract_helper.initialize_contract_with_abi(
    address=c.CARBON_CONTROLLER_ADDRESS, abi=c.CARBON_CONTROLLER_ABI, w3=c.w3
)

assert contract.address == c.CARBON_CONTROLLER_ADDRESS

# Create a TestCase instance
test_case = unittest.TestCase()

# Create an invalid address
invalid_address = "invalid_ethereum_address"

# - Test if the function raises an exception when given invalid parameters.
test_case.assertRaises(InvalidAddress, contract_helper.initialize_contract_with_abi, invalid_address, c.CARBON_CONTROLLER_ABI, c.w3)

# + jupyter={"outputs_hidden": false}
# 4. Test initialize_contract_without_abi function
#    - Test if the function returns a Contract object when given valid parameters.
contract = contract_helper.initialize_contract_without_abi(
    address=c.CARBON_CONTROLLER_ADDRESS, w3=c.w3
)

assert contract.address == c.CARBON_CONTROLLER_ADDRESS

# Test if the function raises an exception when given invalid parameters.
test_case.assertRaises(ValueError, contract_helper.initialize_contract_without_abi, invalid_address, c.w3)

# + jupyter={"outputs_hidden": false}
# 5. Test initialize_contract function
#    - Test if the function returns a Contract object when given valid parameters with and without ABI.
contract_with_abi = contract_helper.initialize_contract(
    address=c.CARBON_CONTROLLER_ADDRESS, _abi=c.CARBON_CONTROLLER_ABI, w3=c.w3
)

contract_without_abi = contract_helper.initialize_contract(
    address=c.CARBON_CONTROLLER_ADDRESS, w3=c.w3
)

assert contract_with_abi.address == c.CARBON_CONTROLLER_ADDRESS
assert contract_without_abi.address == c.CARBON_CONTROLLER_ADDRESS

#   - Test if the function raises an exception when given invalid parameters.
test_case.assertRaises(InvalidAddress, contract_helper.initialize_contract, c.w3, invalid_address, c.CARBON_CONTROLLER_ABI)

# + jupyter={"outputs_hidden": false}
# 6. Test contract_from_address function
#    - Test if the function returns the correct contract for valid exchange_name and pool_address.

# Create a contract
contract = contract_helper.contract_from_address(
    exchange_name=c.UNISWAP_V2_NAME, pool_address='0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'
)

assert contract.address == '0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'

#   - Test if the function raises a NotImplementedError when given an unsupported exchange_name.
unsupported_exchange_name = "unsupported_exchange_name"

test_case.assertRaises(NotImplementedError, contract_helper.contract_from_address, unsupported_exchange_name, c.CARBON_CONTROLLER_ADDRESS)

# + jupyter={"outputs_hidden": false}

# 7. Test get_or_init_contract function
#    - Test if the function returns the correct contract for valid exchange_name and pool_address.
contract = contract_helper.get_or_init_contract(
    exchange_name=c.UNISWAP_V2_NAME, pool_address='0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'
)

assert contract.address == '0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'
assert contract_helper.contracts[c.UNISWAP_V2_NAME]['0x3fd4Cf9303c4BC9E13772618828712C8EaC7Dd2F'] == contract
assert len(contract_helper.contracts[c.UNISWAP_V2_NAME]) == 1

