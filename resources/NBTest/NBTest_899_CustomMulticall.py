# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + is_executing=true
import json

from fastlane_bot.config.multiprovider import MultiProviderContractWrapper
from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI
import os
from unittest.mock import Mock, patch

from dotenv import load_dotenv
load_dotenv()
import time
from fastlane_bot.config.multicaller import MultiCaller
from fastlane_bot.config.multicaller import ContractMethodWrapper


import pytest

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MultiCaller))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ContractMethodWrapper))


from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# + is_executing=true
WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")

# Define ABI and address
CONTRACT_ABI = CARBON_CONTROLLER_ABI
CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
CONTRACT_ADDRESS = CARBON_CONTROLLER_ADDRESS

# Define providers
providers = {
    "mainnet": f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}",
    "tenderly": "https://rpc.tenderly.co/fork/5f70ee18-8d2f-40d7-8131-58d0c8ff4736",
}

# Mock the Web3 and Contract classes
class MockWeb3:
    class HTTPProvider:
        pass

    class eth:
        @staticmethod
        def contract(address, abi):
            return Mock()

class MockContract:
    pass


# -

# ## test_multicaller_init

# + is_executing=true

original_method = Mock()
multicaller = Mock()

wrapper = ContractMethodWrapper(original_method, multicaller)

assert wrapper.original_method == original_method
assert wrapper.multicaller == multicaller
# -

# ## test_contract_method_wrapper_call

# + is_executing=true
original_method = Mock()
multicaller = Mock()

wrapper = ContractMethodWrapper(original_method, multicaller)

result = wrapper('arg1', kwarg1='kwarg1')

original_method.assert_called_with('arg1', kwarg1='kwarg1')
multicaller.add_call.assert_called_with(result)
# -

# ## test_multi_caller_init

# + is_executing=true
contract = Mock()

multicaller = MultiCaller(contract)

assert multicaller.contract == contract
assert multicaller.block_identifier == 'latest'
assert multicaller._contract_calls == []
# -

# ## test_multi_caller_add_call

# + is_executing=true
contract = Mock()
multicaller = MultiCaller(contract)
fn = Mock()

multicaller.add_call(fn, 'arg1', kwarg1='kwarg1')

assert len(multicaller._contract_calls) == 1
# -

# ## test_multi_caller_multicall

# + is_executing=true
contract = Mock()
contract.address = "some_address"
fn = Mock()
fn()._encode_transaction_data.return_value = 'some_data'

with patch('fastlane_bot.data.abi.MULTICALL_ABI', 'MULTICALL_ABI'):  # Replace 'your_module' with the actual module name
    multicaller = MultiCaller(contract)
    multicaller._contract_calls = [fn]

    with patch.object(multicaller.contract, 'web3') as mock_web3:
        mock_contract = Mock()
        mock_web3.eth.contract.return_value = mock_contract

        multicaller.multicall()

        mock_contract.functions.aggregate.assert_called()
# -

# ## test_multi_caller_context_manager

# + is_executing=true
contract = Mock()
multicaller = MultiCaller(contract)

with patch.object(multicaller, 'multicall') as mock_multicall:
    with multicaller:
        pass

    mock_multicall.assert_called_once()
# -

# ## test_multiprovider

# + is_executing=true
# Initialize the Contract wrapper
contract = MultiProviderContractWrapper(CONTRACT_ABI, CONTRACT_ADDRESS, providers)

# Execute contract calls
mainnet_pairs = contract.mainnet.functions.pairs().call()
tenderly_pairs = contract.tenderly.functions.pairs().call()

assert len(mainnet_pairs) > 0
assert len(tenderly_pairs) > 0
# -

# ## test_multicaller

# + is_executing=true
multicaller = MultiCaller(contract=contract.mainnet)

# Time how long it takes to get all fees using multicall
start_time = time.time()

with multicaller as mc:
    for pair in mainnet_pairs:
        mc.add_call(contract.mainnet.functions.pairTradingFeePPM, pair[0], pair[1])

pair_fees_with_multicall = multicaller.multicall()

time_with_multicall = time.time() - start_time

# Time how long it takes to get all fees without using multicall
start_time = time.time()

pair_fees_without_multicall = [contract.mainnet.functions.pairTradingFeePPM(pair[0], pair[1]).call() for pair in mainnet_pairs]

time_without_multicall = time.time() - start_time

assert len(pair_fees_with_multicall) == len(mainnet_pairs)
assert len(pair_fees_with_multicall) == len(mainnet_pairs)
assert time_with_multicall < (time_without_multicall / 10)
