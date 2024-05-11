# ------------------------------------------------------------
# Auto generated test file `test_899_CustomMulticall.py`
# ------------------------------------------------------------
# source file   = NBTest_899_CustomMulticall.py
# test id       = 899
# test comment  = CustomMulticall
# ------------------------------------------------------------


from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI
import os

from dotenv import load_dotenv
load_dotenv()
from fastlane_bot.config.multicaller import MultiCaller

from web3 import Web3
from json import dumps

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MultiCaller))


from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")
RPC_URL = f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}"
MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"
CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"

web3 = Web3(Web3.HTTPProvider(RPC_URL))
multicaller = MultiCaller(web3, MULTICALL_CONTRACT_ADDRESS)
carbon_contract = web3.eth.contract(address=CARBON_CONTROLLER_ADDRESS, abi=CARBON_CONTROLLER_ABI)

# ------------------------------------------------------------
# Test      899
# File      test_899_CustomMulticall.py
# Segment   test_multi_caller
# ------------------------------------------------------------
def test_test_multi_caller():
# ------------------------------------------------------------
    
    # +
    pairs = carbon_contract.caller.pairs()[:10]
    fee_funcs = [carbon_contract.functions.pairTradingFeePPM(*pair) for pair in pairs]
    strat_funcs = [carbon_contract.functions.strategiesByPair(*pair, 0, 5000) for pair in pairs]
    funcs = fee_funcs + strat_funcs

    for func in funcs:
        multicaller.add_call(func)

    block_number = web3.eth.get_block('latest').number

    sc_calls = [func.call(block_identifier=block_number) for func in funcs]
    mc_calls = multicaller.run_calls(block_identifier=block_number)

    for sc_output, mc_output in zip(sc_calls, mc_calls):
        sc_output_str = dumps(sc_output, indent=4).lower()
        mc_output_str = dumps(mc_output, indent=4).lower()
        assert sc_output_str == mc_output_str, f"sc_output = {sc_output_str}, mc_output = {mc_output_str}"
    # -
