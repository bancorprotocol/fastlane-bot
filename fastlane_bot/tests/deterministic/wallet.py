"""
This module contains the Wallet class, which is a dataclass that represents a wallet on the Ethereum network.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
from dataclasses import dataclass

from eth_typing import Address
from web3 import Web3

from fastlane_bot.tests.deterministic.token_balance import TokenBalance


@dataclass
class Wallet:
    w3: Web3
    address: str or Address  # Address after __post_init__, str before
    balances: list[
        TokenBalance or dict
        ] = None  # List of TokenBalances after __post_init__, list of dicts before

    def __post_init__(self):
        self.address = Web3.to_checksum_address(self.address)
        self.balances = [TokenBalance(**args) for args in self.balances or []]

    @property
    def nonce(self):
        return self.w3.eth.get_transaction_count(self.address)
