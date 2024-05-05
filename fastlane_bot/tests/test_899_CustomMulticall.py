# ------------------------------------------------------------
# Auto generated test file `test_899_CustomMulticall.py`
# ------------------------------------------------------------
# source file   = NBTest_899_CustomMulticall.py
# test id       = 899
# test comment  = CustomMulticall
# ------------------------------------------------------------


from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI
import os
from unittest.mock import Mock, patch

from dotenv import load_dotenv
load_dotenv()
import time
from fastlane_bot.config.multicaller import MultiCaller
from fastlane_bot.config.multicaller import ContractMethodWrapper

from web3 import Web3

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MultiCaller))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ContractMethodWrapper))


from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")
RPC_URL = f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}"
CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"

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

start_time = time.time()

w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'timeout': 60}))
contract = w3.eth.contract(address=CARBON_CONTROLLER_ADDRESS, abi=CARBON_CONTROLLER_ABI)

mainnet_pairs = contract.caller.pairs()

if len(mainnet_pairs) > 10:
    mainnet_pairs = mainnet_pairs[:10]

pair_fees_without_multicall = [contract.caller.pairTradingFeePPM(pair[0], pair[1]) for pair in mainnet_pairs]

pair_fees_time_without_multicall = time.time() - start_time

start_time = time.time()

strats_by_pair_without_multicall = [contract.caller.strategiesByPair(pair[0], pair[1], 0, 5000) for pair in mainnet_pairs]

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
    web3 = MockWeb3()
    
    multicaller = MultiCaller(contract, web3=web3)
    
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
    web3 = MockWeb3()
    
    multicaller = MultiCaller(contract, web3=web3)
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
    web3 = MockWeb3()
    multicaller = MultiCaller(contract, web3=web3)
    
    with patch.object(multicaller, 'multicall') as mock_multicall:
        with multicaller:
            multicaller.multicall()
            pass
    
        mock_multicall.assert_called_once()
    # -
    
    