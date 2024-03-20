"""
Defines the ``MultiProviderContractWrapper`` class 

TODO-MIKE: This is a very short module, so maybe the code should move somewhere else;
also -- should it really be in config?

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from web3 import Web3
from typing import Dict

from web3.contract import Contract


class MultiProviderContractWrapper:
    def __init__(self, abi: Dict, address: str, providers: Dict[str, str]):
        self.abi = abi
        self.contracts = {}

        for name, url in providers.items():
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 60}))
            self.contracts[name] = w3.eth.contract(address=address, abi=self.abi)

    def __getattr__(self, name: str) -> Contract:
        if name in self.contracts:
            return self.contracts[name]
        raise AttributeError(f"No provider named {name}")
