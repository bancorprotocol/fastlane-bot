"""
Class objects for Ethereum Network tokens.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from decimal import *

from web3 import Web3

from fastlane_bot.constants import ec


# *******************************************************************************************
# Tokens
# *******************************************************************************************


@dataclass
class EthBaseToken:
    """Base token for all Ethereum network tokens (ETH, BSC, etc.)"""

    _is_tkn0: bool = None
    """True if token0 is the token."""

    symbol: str = None
    """Symbol such as ETH, DAI, etc."""

    amt: int = 0
    """Amount of token."""

    decimals: int = 18
    """Decimals used to denominate the token."""

    address: str = None
    """Address of the token contract."""

    def convert_to_eth(self):
        self.address = ec.ETH_ADDRESS
        self.symbol = ec.ETH_SYMBOL
        return self

    def convert_to_weth(self):
        self.address = ec.WETH_ADDRESS
        self.symbol = ec.WETH_SYMBOL
        return self

    def is_tkn0(self) -> bool:
        """Returns True if token0 is the token."""
        return self._is_tkn0

    def to_weth(self):
        """
        :return: WETH address
        """
        return ec.WETH_ADDRESS

    def to_eth(self):
        """
        :return: ETH address
        """
        return ec.ETH_ADDRESS

    def is_eth(self) -> bool:
        """
        :return: True if the token is ETH
        """
        return self.symbol == ec.ETH_SYMBOL

    def is_weth(self) -> bool:
        """
        :return: True if the token is WETH
        """
        return self.symbol == ec.WETH_SYMBOL

    def is_bnt(self) -> bool:
        """
        :return: True if the token is BNT
        """
        return self.symbol == ec.BNT_SYMBOL

    def convert_to_wei(self, amount: int) -> int:
        """Convert a token amount to wei.
        Args:
            amount (int): Amount of token to convert.
        Returns:
            int: Amount of wei.
        """
        return amount * 10**self.decimals

    def convert_from_wei(self, amount: int) -> int:
        """Convert a wei amount to token.
        Args:
            amount (int): Amount of wei to convert.
        Returns:
            int: Amount of token.
        """
        return amount // 10**self.decimals

    def convert_eth_to_weth(self, address: str = None) -> str:
        """Convert an ETH address to a WETH address.
        Args:
            address (AddressLike): Address to convert.
        Returns:
            AddressLike: WETH address.
        """
        if address is None:
            address = self.address
        return ec.WETH_ADDRESS if str(address) == ec.ETH_ADDRESS else address

    def convert_weth_to_eth(self, address: str = None) -> str:
        """Convert a WETH address to an ETH address.
        Args:
            address (AddressLike): Address to convert.
        Returns:
            AddressLike: ETH address.
        """
        if address is None:
            address = self.address
        return ec.ETH_ADDRESS if str(address) == ec.WETH_ADDRESS else address

    def __repr__(self) -> str:
        return f"Token({self.symbol})"


@dataclass
class ERC20Token(EthBaseToken):
    """Represents an ERC20 token on the Ethereum network. Also used for native ETH."""

    symbol: str = None
    """Symbol such as ETH, DAI, etc."""

    amt: int or Decimal = 0
    """Amount of token."""

    decimals: int = None
    """Decimals used to denominate the token."""

    address: str = None
    """Address of the token contract."""

    def __eq__(self, other) -> bool:
        assert isinstance(
            other, ERC20Token
        ), "Equality can only be evaluated against another Erc20Token"
        return self.address.lower() == other.address.lower()

    def __post_init__(self):
        if self.decimals is None and self.symbol is not None:
            self.decimals = ec.DECIMAL_FROM_SYMBOL[self.symbol]
        if self.address is None and self.symbol is not None:
            self.address = Web3.toChecksumAddress(ec.ADDRESS_FROM_SYMBOL[self.symbol])
