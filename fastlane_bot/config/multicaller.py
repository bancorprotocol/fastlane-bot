"""
MultiCaller class

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List, Dict

from eth_abi import decode
from web3.contract.contract import ContractFunction

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


class MultiCaller:
    """
    Context manager for multicalls.
    """
    __DATE__ = "2022-09-26"
    __VERSION__ = "0.0.2"

    def __init__(self, web3: Any, multicall_contract_address: str):
        self.multicall_contract = web3.eth.contract(abi=MULTICALL_ABI, address=multicall_contract_address)
        self.contract_calls: List[ContractFunction] = []
        self.output_types_list: List[List[str]] = []

    def add_call(self, call: ContractFunction):
        self.contract_calls.append({'target': call.address, 'callData': call._encode_transaction_data()})
        self.output_types_list.append([collapse_if_tuple(item) for item in call.abi['outputs']])

    def run_calls(self, block_identifier: Any = 'latest') -> List[Any]:
        encoded_data = self.multicall_contract.functions.tryAggregate(
            False,
            self.contract_calls
        ).call(block_identifier=block_identifier)

        result_list = [
            decode(output_types, encoded_output[1]) if encoded_output[0] else (None,)
            for output_types, encoded_output in zip(self.output_types_list, encoded_data)
        ]

        # Convert every single-value tuple into a single value
        return [result if len(result) > 1 else result[0] for result in result_list]
