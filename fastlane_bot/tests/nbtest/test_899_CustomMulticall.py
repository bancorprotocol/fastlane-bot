# ------------------------------------------------------------
# Auto generated test file `test_899_CustomMulticall.py`
# ------------------------------------------------------------
# source file   = NBTest_899_CustomMulticall.py
# test id       = 899
# test comment  = CustomMulticall
# ------------------------------------------------------------



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

WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")

CONTRACT_ABI = CARBON_CONTROLLER_ABI
CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
CONTRACT_ADDRESS = CARBON_CONTROLLER_ADDRESS

providers = {
    "mainnet": f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}",
    "tenderly": "https://rpc.tenderly.co/fork/5f70ee18-8d2f-40d7-8131-58d0c8ff4736",
}

class MockWeb3:
    class HTTPProvider:
        pass

    class eth:
        @staticmethod
        def contract(address, abi):
            return Mock()

class MockContract:
    pass

start_time = time.time()

contract = MultiProviderContractWrapper(CONTRACT_ABI, CONTRACT_ADDRESS, providers)

mainnet_pairs = contract.mainnet.functions.pairs().call()
tenderly_pairs = contract.tenderly.functions.pairs().call()

if len(mainnet_pairs) > 10:
    mainnet_pairs = mainnet_pairs[:10]

pair_fees_without_multicall = [contract.mainnet.functions.pairTradingFeePPM(pair[0], pair[1]).call() for pair in mainnet_pairs]

pair_fees_time_without_multicall = time.time() - start_time

start_time = time.time()

strats_by_pair_without_multicall = [contract.mainnet.functions.strategiesByPair(pair[0], pair[1], 0, 5000).call() for pair in mainnet_pairs]

strats_by_pair_time_without_multicall = time.time() - start_time



# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_multicaller_init
# ------------------------------------------------------------
def test_test_multicaller_init():
# ------------------------------------------------------------
    
    # +
    
    original_method = Mock()
    multicaller = Mock()
    
    wrapper = ContractMethodWrapper(original_method, multicaller)
    
    assert wrapper.original_method == original_method
    assert wrapper.multicaller == multicaller
    # -
    

# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_contract_method_wrapper_call
# ------------------------------------------------------------
def test_test_contract_method_wrapper_call():
# ------------------------------------------------------------
    
    # +
    original_method = Mock()
    multicaller = Mock()
    
    wrapper = ContractMethodWrapper(original_method, multicaller)
    
    result = wrapper('arg1', kwarg1='kwarg1')
    
    original_method.assert_called_with('arg1', kwarg1='kwarg1')
    multicaller.add_call.assert_called_with(result)
    # -
    

# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_multi_caller_init
# ------------------------------------------------------------
def test_test_multi_caller_init():
# ------------------------------------------------------------
    
    # +
    contract = Mock()
    
    multicaller = MultiCaller(contract)
    
    assert multicaller.contract == contract
    assert multicaller.block_identifier == 'latest'
    assert multicaller._contract_calls == []
    # -
    

# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_multi_caller_add_call
# ------------------------------------------------------------
def test_test_multi_caller_add_call():
# ------------------------------------------------------------
    
    # +
    contract = Mock()
    multicaller = MultiCaller(contract)
    fn = Mock()
    
    multicaller.add_call(fn, 'arg1', kwarg1='kwarg1')
    
    assert len(multicaller._contract_calls) == 1
    # -
    

# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_multi_caller_context_manager
# ------------------------------------------------------------
def test_test_multi_caller_context_manager():
# ------------------------------------------------------------
    
    # +
    contract = Mock()
    multicaller = MultiCaller(contract)
    
    with patch.object(multicaller, 'multicall') as mock_multicall:
        with multicaller:
            pass
    
        mock_multicall.assert_called_once()
    # -
    

# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_multicaller_pairTradingFeePPM
# ------------------------------------------------------------
def test_test_multicaller_pairtradingfeeppm():
# ------------------------------------------------------------
    
    # +
    contract = MultiProviderContractWrapper(CONTRACT_ABI, CONTRACT_ADDRESS, providers)
    
    multicaller = MultiCaller(contract=contract.mainnet)
    
    # Time how long it takes to get all fees using multicall
    start_time = time.time()
    
    with multicaller as mc:
        for pair in mainnet_pairs:
            mc.add_call(contract.mainnet.functions.pairTradingFeePPM, pair[0], pair[1])
    
    pair_fees_with_multicall = multicaller.multicall()
    
    pair_fees_time_with_multicall = time.time() - start_time
    
    assert pair_fees_with_multicall == pair_fees_without_multicall
    assert pair_fees_time_with_multicall < pair_fees_time_without_multicall
    
    # -
    

# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_multicaller_strategiesByPair
# ------------------------------------------------------------
def test_test_multicaller_strategiesbypair():
# ------------------------------------------------------------
    
    # +
    contract = MultiProviderContractWrapper(CONTRACT_ABI, CONTRACT_ADDRESS, providers)
    
    multicaller = MultiCaller(contract=contract.mainnet)
    
    # Time how long it takes to get all fees using multicall
    start_time = time.time()
    
    with multicaller as mc:
        for pair in mainnet_pairs:
            mc.add_call(contract.mainnet.functions.strategiesByPair, pair[0], pair[1], 0, 5000)
    
    strats_by_pair_with_multicall = multicaller.multicall()
    
    strats_by_pair_time_with_multicall = time.time() - start_time
    
    assert len(strats_by_pair_with_multicall) == len(strats_by_pair_without_multicall)
    assert strats_by_pair_time_with_multicall < strats_by_pair_time_without_multicall
    
    # -
    
    