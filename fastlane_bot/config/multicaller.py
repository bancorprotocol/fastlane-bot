from web3 import Web3
from typing import List, Callable, Any

from fastlane_bot.data.abi import MULTICALL_ABI


class MultiCaller:
    def __init__(self, provider_url: str, multicall_address: str):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.multicall_address = multicall_address

    def multicall(self, contract_calls: List[Callable], block_identifier: Any = 'latest') -> Any:
        encoded_calls = [fn._encode_transaction_data() for fn in contract_calls]

        return self.w3.eth.call(
            {
                'to': self.multicall_address,
                'data': self.w3.eth.contract(
                    abi=MULTICALL_ABI, address=self.multicall_address
                )
                .functions.aggregate(encoded_calls)
                .buildTransaction()['data'],
            },
            block_identifier,
        )