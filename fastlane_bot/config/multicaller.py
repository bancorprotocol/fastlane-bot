from functools import partial
from typing import List, Callable, ContextManager, Any

from fastlane_bot.config.multiprovider import MultiProviderContractWrapper
from fastlane_bot.data.abi import MULTICALL_ABI


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

    def __init__(self, contract: MultiProviderContractWrapper, block_identifier: Any = 'latest'):
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

    def multicall(self) -> None:
        calls_for_aggregate = [
            {
                'target': self.contract.address,
                'callData': fn()._encode_transaction_data()
            }
            for fn in self._contract_calls
        ]
        w3 = self.contract.web3
        return w3.eth.contract(
            abi=MULTICALL_ABI,
            address=self.MULTICALL_CONTRACT_ADDRESS
        ).functions.aggregate(calls_for_aggregate).call(block_identifier=self.block_identifier)

