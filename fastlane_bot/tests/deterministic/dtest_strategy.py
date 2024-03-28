"""
This file contains the Strategy class, which is used to represent a strategy in the deterministic tests.

(c) Copyright Bprotocol foundation 2024.
All rights reserved.
Licensed under MIT License.
"""
import argparse
from dataclasses import dataclass

from eth_typing import ChecksumAddress
from web3 import Web3

from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.tests.deterministic import dtest_constants as constants
from fastlane_bot.tests.deterministic.dtest_token import TestToken
from fastlane_bot.tests.deterministic.dtest_wallet import TestWallet


@dataclass
class TestStrategy:
    """
    A class to represent a strategy in the deterministic tests.
    """

    w3: Web3
    token0: TestToken
    token1: TestToken
    y0: int
    z0: int
    A0: int
    B0: int
    y1: int
    z1: int
    A1: int
    B1: int
    wallet: TestWallet

    @property
    def id(self):
        return self._id or None

    @id.setter
    def id(self, id: int):
        self._id = id

    def __post_init__(self):
        self.token0 = TestToken(self.token0)
        self.token0.contract = self.w3.eth.contract(
            address=self.token0.address, abi=ERC20_ABI
        )
        self.token1 = TestToken(self.token1)
        self.token1.contract = self.w3.eth.contract(
            address=self.token1.address, abi=ERC20_ABI
        )
        self.wallet = TestWallet(self.w3, self.wallet)

    def get_token_approval(
        self, args: argparse.Namespace, token_id: int, approval_address: ChecksumAddress
    ) -> str:
        """
        This method is used to get the token approval for the given token and approval address.

        Args:
            args (argparse.Namespace): The command line arguments.
            token_id (int): The token ID. Should be 0 or 1.
            approval_address (ChecksumAddress): The approval address.

        Returns:
            str: The transaction hash.
        """
        token = self.token0 if token_id == 0 else self.token1
        if token.address in [
            constants.BNT_ADDRESS,
            constants.USDC_ADDRESS,
            constants.USDT_ADDRESS,
        ]:
            function_call = token.contract.functions.approve(
                approval_address, 0
            ).transact(
                {
                    "gasPrice": constants.DEFAULT_GAS_PRICE,
                    "gas": constants.DEFAULT_GAS,
                    "from": self.wallet.address,
                    "nonce": self.wallet.nonce,
                }
            )
            tx_reciept = self.w3.eth.wait_for_transaction_receipt(function_call)
            tx_hash = self.w3.to_hex(dict(tx_reciept)["transactionHash"])

            if dict(tx_reciept)["status"] != 1:
                args.logger.debug("Approval Failed")
            else:
                args.logger.debug("Successfully Approved for 0")

            args.logger.debug(f"tx_hash = {tx_hash}")

        function_call = token.contract.functions.approve(
            approval_address, constants.TEST_MODE_AMT
        ).transact(
            {
                "gasPrice": constants.DEFAULT_GAS_PRICE,
                "gas": constants.DEFAULT_GAS,
                "from": self.wallet.address,
                "nonce": self.wallet.nonce,
            }
        )
        tx_reciept = self.w3.eth.wait_for_transaction_receipt(function_call)
        tx_hash = self.w3.to_hex(dict(tx_reciept)["transactionHash"])

        if dict(tx_reciept)["status"] != 1:
            args.logger.debug("Approval Failed")
        else:
            args.logger.debug("Successfully Approved Token for Unlimited")

        args.logger.debug(f"tx_hash = {tx_hash}")
        return tx_hash

    @property
    def value(self):
        return (
            self.y0 if self.token0.is_eth else self.y1 if self.token1.is_eth else None
        )
