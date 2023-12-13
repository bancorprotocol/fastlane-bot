# coding=utf-8
"""
This is the multicaller module.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from functools import partial
from typing import List, Callable, ContextManager, Any, Dict

import web3
from eth_abi import decode_abi

from fastlane_bot.config.multiprovider import MultiProviderContractWrapper
from fastlane_bot.data.abi import MULTICALL_ABI


def cast(typ, val):
    """Cast a value to a type.

    This returns the value unchanged.  To the type checker this
    signals that the return value has the designated type, but at
    runtime we intentionally don't check anything (we want this
    to be as fast as possible).
    """
    return val


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
    typ = abi["type"]
    if not isinstance(typ, str):
        raise TypeError(
            "The 'type' must be a string, but got %r of type %s" % (typ, type(typ))
        )
    elif not typ.startswith("tuple"):
        return typ

    delimited = ",".join(collapse_if_tuple(c) for c in abi["components"])
    # Whatever comes after "tuple" is the array dims.  The ABI spec states that
    # this will have the form "", "[]", or "[k]".
    array_dim = typ[5:]
    collapsed = "({}){}".format(delimited, array_dim)

    return collapsed


def get_output_types_from_abi(abi: List[Dict[str, Any]], function_name: str) -> List[str]:
    """
    Get the output types from an ABI.

    Parameters
    ----------
    abi : List[Dict[str, Any]]
        The ABI
    function_name : str
        The function name

    Returns
    -------
    List[str]
        The output types

    """
    for item in abi:
        if item['type'] == 'function' and item['name'] == function_name:
            return [collapse_if_tuple(cast(Dict[str, Any], item)) for item in item['outputs']]
    raise ValueError(f"No function named {function_name} found in ABI.")


class ContractMethodWrapper:
    """
    Wraps a contract method to be used with multicall.
    """
    __DATE__ = "2022-09-26"
    __VERSION__ = "0.0.2"

    def __init__(self, original_method, multicaller):
        self.original_method = original_method
        self.multicaller = multicaller

    def __call__(self, *args, **kwargs):
        contract_call = self.original_method(*args, **kwargs)
        self.multicaller.add_call(contract_call)
        return contract_call


class MultiCaller(ContextManager):
    """
    Context manager for multicalls.
    """
    __DATE__ = "2022-09-26"
    __VERSION__ = "0.0.2"


    def __init__(self, contract: MultiProviderContractWrapper or web3.contract.Contract,
                 block_identifier: Any = 'latest', multicall_address = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"):
        self._contract_calls: List[Callable] = []
        self.contract = contract
        self.block_identifier = block_identifier
        self.MULTICALL_CONTRACT_ADDRESS = multicall_address

    def __enter__(self) -> 'MultiCaller':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_call(self, fn: Callable, *args, **kwargs) -> None:
        self._contract_calls.append(partial(fn, *args, **kwargs))

    def multicall(self) -> List[Any]:
        calls_for_aggregate = []
        output_types_list = []
        _calls_for_aggregate = {}
        _output_types_list = {}
        for fn in self._contract_calls:
            fn_name = str(fn).split('functools.partial(<Function ')[1].split('>')[0]
            output_types = get_output_types_from_abi(self.contract.abi, fn_name)
            if fn_name in _calls_for_aggregate:
                _calls_for_aggregate[fn_name].append({
                'target': self.contract.address,
                'callData': fn()._encode_transaction_data()
            })
                _output_types_list[fn_name].append(output_types)
            else:
                _calls_for_aggregate[fn_name] = [{
                'target': self.contract.address,
                'callData': fn()._encode_transaction_data()
            }]
                _output_types_list[fn_name] = [output_types]

        for fn_list in _calls_for_aggregate.keys():
            calls_for_aggregate += (_calls_for_aggregate[fn_list])
            output_types_list += (_output_types_list[fn_list])

        w3 = self.contract.web3
        _encoded_data = []
        function_keys = _calls_for_aggregate.keys()
        for fn_list in function_keys:
            _encoded_data.append(w3.eth.contract(
                abi=MULTICALL_ABI,
                address=self.MULTICALL_CONTRACT_ADDRESS
            ).functions.aggregate(_calls_for_aggregate[fn_list]).call(block_identifier=self.block_identifier))

        if not isinstance(_encoded_data[0], list):
            raise TypeError(f"Expected encoded_data to be a list, got {type(_encoded_data[0])} instead.")

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

        return_data = [i[0] for i in decoded_data_list if len(i) == 1]
        return_data += [i[1] for i in decoded_data_list if len(i) > 1]

        # Handling for Bancor POL - combine results into a Tuple
        if "tokenPrice" in function_keys and "amountAvailableForTrading" in function_keys:
            new_return = []
            returned_items = int(len(return_data))
            total_pools = int(returned_items / 2)
            assert returned_items % 2 == 0, f"[multicaller.py multicall] non-even number of returned calls for Bancor POL {returned_items}"
            total_pools = int(total_pools)

            for idx in range(total_pools):
                new_return.append((return_data[idx][0], return_data[idx][1], return_data[idx + total_pools]))
            return_data = new_return

        return return_data
