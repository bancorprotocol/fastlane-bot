"""
This module contains the TokenBalance class, which is used to represent the balance of a token in a wallet
in the deterministic tests.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
from dataclasses import dataclass

from web3 import Web3

from fastlane_bot.tests.deterministic.token import Token


@dataclass
class TokenBalance:
    """
    A class to represent the balance of a token in a wallet in the deterministic tests.
    """

    token: Token or str  # Token after __post_init__, str before
    balance: int

    def __post_init__(self):
        self.token = Token(self.token)
        self.balance = int(self.balance)

    @property
    def hex_balance(self):
        return Web3.to_hex(self.balance)

    def faucet_params(self, wallet_address: str = None) -> list:
        """
        This method is used to return the faucet parameters for the token balance.
        """
        return (
            [[self.token.address], self.hex_balance]
            if self.token.is_eth
            else [self.token.address, wallet_address, self.hex_balance]
        )
