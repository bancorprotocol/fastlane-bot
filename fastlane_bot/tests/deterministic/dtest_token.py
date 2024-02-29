"""
Token class to store token address and contract object for interacting with the token on the blockchain.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
from dataclasses import dataclass

from eth_typing import Address
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.tests.deterministic.dtest_constants import ETH_ADDRESS


@dataclass
class TestToken:
    """
    A class to represent a token on the blockchain.

    Attributes:
        address: str or Address
    """

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


@dataclass
class TestTokenBalance:
    """
    A class to represent the balance of a token in a wallet in the deterministic tests.

    Attributes:
        token: TestToken or str
        balance: int
    """

    token: TestToken or str  # Token after __post_init__, str before
    balance: int

    def __post_init__(self):
        self.token = TestToken(self.token)
        self.balance = int(self.balance)

    @property
    def hex_balance(self):
        return Web3.to_hex(self.balance)

    def faucet_params(self, wallet_address: str = None) -> list:
        """
        This method is used to return the faucet parameters for the token balance.

        Args:
            wallet_address: str

        Returns:
            list: The faucet parameters.
        """
        return (
            [[self.token.address], self.hex_balance]
            if self.token.is_eth
            else [self.token.address, wallet_address, self.hex_balance]
        )
