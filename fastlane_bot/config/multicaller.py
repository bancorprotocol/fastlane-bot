from functools import partial
from typing import List, Callable, ContextManager, Any

import brownie
import web3
from eth_abi import decode_abi

from fastlane_bot.config.multiprovider import MultiProviderContractWrapper
from fastlane_bot.data.abi import MULTICALL_ABI

def get_output_types_from_abi(abi, function_name):
    for item in abi:
        if item['type'] == 'function' and item['name'] == function_name:
            return [output['type'] for output in item['outputs']]
    raise ValueError(f"No function named {function_name} found in ABI.")


class ContractMethodWrapper:
    __DATE__ = "2022-09-24"
    __VERSION__ = "0.0.1"

    def __init__(self, original_method, multicaller):
        self.original_method = original_method
        self.multicaller = multicaller

    def __call__(self, *args, **kwargs):
        contract_call = self.original_method(*args, **kwargs)
        self.multicaller.add_call(contract_call)
        return contract_call


class MultiCaller(ContextManager):
    __DATE__ = "2022-09-24"
    __VERSION__ = "0.0.1"
    MULTICALL_CONTRACT_ADDRESS = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"

    def __init__(self, contract: MultiProviderContractWrapper or web3.contract.Contract or brownie.Contract, block_identifier: Any = 'latest'):
        self._contract_calls: List[Callable] = []
        self.contract = contract
        self.block_identifier = block_identifier

    def __enter__(self) -> 'MultiCaller':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.multicall()

    def add_call(self, fn: Callable, *args, **kwargs) -> None:
        self._contract_calls.append(partial(fn, *args, **kwargs))

    def multicall(self) -> List[Any]:
        calls_for_aggregate = []
        output_types_list = []

        for fn in self._contract_calls:
            fn_name = str(fn).split('functools.partial(<Function ')[1].split('>')[0]
            print(f"fn_name: {fn_name}")
            calls_for_aggregate.append({
                'target': self.contract.address,
                'callData': fn()._encode_transaction_data()
            })
            output_types = get_output_types_from_abi(self.contract.abi, fn_name)
            output_types_list.append(output_types)

        w3 = self.contract.web3
        encoded_data = w3.eth.contract(
            abi=MULTICALL_ABI,
            address=self.MULTICALL_CONTRACT_ADDRESS
        ).functions.aggregate(calls_for_aggregate).call(block_identifier=self.block_identifier)

        if not isinstance(encoded_data, list):
            raise TypeError(f"Expected encoded_data to be a list, got {type(encoded_data)} instead.")

        encoded_data = encoded_data[1]
        decoded_data_list = []
        for output_types, encoded_output in zip(output_types_list, encoded_data):
            decoded_data = decode_abi(output_types, encoded_output)
            decoded_data_list.append(decoded_data)

        return decoded_data_list
