"""
Token class to store token address and contract object for interacting with the token on the blockchain.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
from dataclasses import dataclass

from eth_typing import Address
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.tests.deterministic.constants import ETH_ADDRESS


@dataclass
class Token:
    address: str or Address  # Address after __post_init__, str before

    def __post_init__(self):
        self.address = Web3.to_checksum_address(self.address)
        self._contract = None

    @property
    def contract(self):
        return self._contract

    @contract.setter
    def contract(self, contract: Contract):
        self._contract = contract

    @property
    def is_eth(self):
        return self.address == ETH_ADDRESS
