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

# +
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

# +
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
        
        @staticmethod
        def to_checksum_address(address):
            return address

    @staticmethod
    def to_checksum_address(address):
        return address

class MockContract:
    
    def __init__(self, address, abi):
        self.address = address
        self.abi = abi

    def functions(self):
        return Mock()

    def encodeABI(self):
        return Mock()

    def address(self):
        return self.address

    def abi(self):
        return self.abi

    def to_checksum_address(self, address):
        return address
    
    # handle encoded data 
    def encode_abi(self):
        return Mock()
    
    def decode_abi(self):
        return Mock()

# Time how long it takes to get all fees without using multicall
start_time = time.time()

# Initialize the Contract wrapper
contract = MultiProviderContractWrapper(CONTRACT_ABI, CONTRACT_ADDRESS, providers)

# Execute contract calls
mainnet_pairs = contract.mainnet.functions.pairs().call()
tenderly_pairs = contract.tenderly.functions.pairs().call()

# Take a sample of 20 pairs to speed up testing
if len(mainnet_pairs) > 10:
    mainnet_pairs = mainnet_pairs[:10]

pair_fees_without_multicall = [contract.mainnet.functions.pairTradingFeePPM(pair[0], pair[1]).call() for pair in mainnet_pairs]

pair_fees_time_without_multicall = time.time() - start_time

start_time = time.time()

strats_by_pair_without_multicall = [contract.mainnet.functions.strategiesByPair(pair[0], pair[1], 0, 5000).call() for pair in mainnet_pairs]

strats_by_pair_time_without_multicall = time.time() - start_time

# -

# ## test_multicaller_init

# +

original_method = Mock()
multicaller = Mock()

wrapper = ContractMethodWrapper(original_method, multicaller)

assert wrapper.original_method == original_method
assert wrapper.multicaller == multicaller
# -

# ## test_contract_method_wrapper_call

# +
original_method = Mock()
multicaller = Mock()

wrapper = ContractMethodWrapper(original_method, multicaller)

result = wrapper('arg1', kwarg1='kwarg1')

original_method.assert_called_with('arg1', kwarg1='kwarg1')
multicaller.add_call.assert_called_with(result)
# -

# ## test_multi_caller_init

# +
contract = Mock()
web3 = MockWeb3()

multicaller = MultiCaller(contract, web3=web3)

assert multicaller.contract == contract
assert multicaller.block_identifier == 'latest'
assert multicaller._contract_calls == []
# -

# ## test_multi_caller_add_call

# +
contract = Mock()
web3 = MockWeb3()

multicaller = MultiCaller(contract, web3=web3)
fn = Mock()

multicaller.add_call(fn, 'arg1', kwarg1='kwarg1')

assert len(multicaller._contract_calls) == 1
# -

# ## test_multi_caller_context_manager

# +
contract = Mock()
web3 = MockWeb3()
multicaller = MultiCaller(contract, web3=web3)

with patch.object(multicaller, 'multicall') as mock_multicall:
    with multicaller:
        multicaller.multicall()
        pass

    mock_multicall.assert_called_once()
# -


