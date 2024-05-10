"""
MultiCaller class

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Callable, ContextManager, Any, List, Dict

from eth_abi import decode

from fastlane_bot.data.abi import MULTICALL_ABI


def collapse_if_tuple(abi: Dict[str, Any]) -> str:
    """
    Converts a tuple from a dict to a parenthesized list of its types.

    >>> from eth_utils.abi import collapse_if_tuple
    >>> collapse_if_tuple(
    ...     {
    ...         'components': [
    ...             {'name': 'anAddress', 'type': 'address'},
    ...             {'name': 'anInt', 'type': 'uint256'},
    ...             {'name': 'someBytes', 'type': 'bytes'},
    ...         ],
    ...         'type': 'tuple',
    ...     }
    ... )
    '(address,uint256,bytes)'
    """
    if abi["type"].startswith("tuple"):
        delimited = ",".join(collapse_if_tuple(c) for c in abi["components"])
        return "({}){}".format(delimited, abi["type"][len("tuple"):])
    return abi["type"]


class MultiCaller(ContextManager):
    """
    Context manager for multicalls.
    """
    __DATE__ = "2022-09-26"
    __VERSION__ = "0.0.2"

    def __init__(self, target_contract: Any, multicall_contract_address: str):
        self.multicall_contract = target_contract.w3.eth.contract(
            abi=MULTICALL_ABI,
            address=multicall_contract_address
        )
        self.target_contract = target_contract
        self.contract_calls: List[Callable] = []
        self.output_types_list: List[List[str]] = []

    def __enter__(self) -> 'MultiCaller':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_call(self, call: Callable):
        self.contract_calls.append({
            'target': self.target_contract.address,
            'callData': call._encode_transaction_data()
        })
        self.output_types_list.append([
            collapse_if_tuple(item) for item in call.abi['outputs']
        ])

    def run_calls(self, block_identifier: Any = 'latest') -> List[Any]:
        encoded_data = self.multicall_contract.functions.tryAggregate(
            True,
            self.contract_calls
        ).call(block_identifier=block_identifier)

        decoded_data_list = []
        for output_types, encoded_output in zip(self.output_types_list, encoded_data):
            decoded_data = decode(output_types, encoded_output[1])
            decoded_data_list.append(decoded_data)

        return_data = [i[0] for i in decoded_data_list if len(i) == 1]
        return_data += [i[1] for i in decoded_data_list if len(i) > 1]

        return return_data
