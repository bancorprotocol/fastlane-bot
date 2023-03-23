"""
Exceptions for fastlane_bot - these are used to raise errors in the code.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""


class ResultLoggingException(Exception):
    """Raised when an exception occurs during logging of a result."""

    def __init__(self, ts=None, path=None) -> None:
        Exception.__init__(
            self,
            f"The result could not be logged to the file: {path} at timestamp: {ts}",
        )


class TradePathSequenceException(Exception):
    """Raised when the tkn1 of PoolA does not match tkn0 of PoolB (the next pool in the path)."""

    def __init__(self, tkn0=None, tkn1=None, idx=None) -> None:
        Exception.__init__(
            self,
            f"The tkn0: {tkn0} of pool {idx} does not match the tkn1: {tkn1} of pool {idx - 1}",
        )


class InvalidRouteTypeException(Exception):
    """Raised when the trade path specified is not of a supported type."""

    def __init__(self, exchange_base=None) -> None:
        Exception.__init__(
            self,
            f"The trade path must meet the requirements of a supported route type. "
            f"First pool must be a CPMM on {exchange_base}. Last pool must be a CPMM on {exchange_base}. "
            f"First and last trade_path must have the same token.",
        )


class InvalidTokenIndexException(Exception):
    """Raised when the index of the selected token is not 0 or 1."""

    def __init__(self, idx=None) -> None:
        Exception.__init__(self, f"The selected token index: {idx} must be 0 or 1")


class InvalidPoolIndexException(Exception):
    """Raised when a pool index is specified but does not exist."""

    def __init__(self, idx=None, route_length=None) -> None:
        Exception.__init__(
            self,
            f"The selected index (idx) must be less than the trade_path length: {route_length}",
        )


class InvalidPoolInitialization(Exception):
    """Raised when a pool is initialized without at least one of address or fee specified."""

    def __init__(
        self, address=None, fee=None, pair=None, exchange=None, tkn0=None, tkn1=None
    ) -> None:
        Exception.__init__(
            self,
            f"Invalid pool initialization for address: {address} or fee: {fee} or pair: {pair} or exchange: {exchange}, or tkn0: {tkn0} or tkn1: {tkn1}",
        )


class InvalidExchangeException(Exception):
    """Raised when an invalid Exchange version is attempted (e.g. Uniswap V7)."""

    def __init__(self, exchange: str) -> None:
        Exception.__init__(
            self,
            f"Invalid exchange {exchange}. Please use a valid exchange version.",
        )
