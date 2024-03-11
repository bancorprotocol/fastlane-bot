"""
This module contains the Wallet class, which is a dataclass that represents a wallet on the given network.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import argparse
import ast
import os
from dataclasses import dataclass

import pandas as pd
from web3 import Web3
from web3.types import RPCEndpoint

from fastlane_bot.tests.deterministic.dtest_constants import (
    SUPPORTED_EXCHANGES,
    TEST_DATA_DIR,
)
from fastlane_bot.tests.deterministic.dtest_token import TestTokenBalance


@dataclass
class TestPool:
    """
    This class is used to represent a pool on the given network.
    """

    exchange_type: str
    pool_address: str
    tkn0_address: str
    tkn1_address: str
    slots: str or list  # List after __post_init__, str before
    param_lists: str or list  # List after __post_init__, str before
    tkn0_setBalance: TestTokenBalance or int  # TokenBalance after __post_init__, int before
    tkn1_setBalance: TestTokenBalance or int  # TokenBalance after __post_init__, int before
    param_blockTimestampLast: int = None
    param_blockTimestampLast_type: str = None
    param_reserve0: int = None
    param_reserve0_type: str = None
    param_reserve1: int = None
    param_reserve1_type: str = None
    param_liquidity: int = None
    param_liquidity_type: str = None
    param_sqrtPriceX96: int = None
    param_sqrtPriceX96_type: str = None
    param_tick: int = None
    param_tick_type: str = None
    param_observationIndex: int = None
    param_observationIndex_type: str = None
    param_observationCardinality: int = None
    param_observationCardinality_type: str = None
    param_observationCardinalityNext: int = None
    param_observationCardinalityNext_type: str = None
    param_feeProtocol: int = None
    param_feeProtocol_type: str = None
    param_unlocked: int = None
    param_unlocked_type: str = None

    def __post_init__(self):
        self.slots = ast.literal_eval(self.slots)
        self.param_lists = ast.literal_eval(self.param_lists)

    @staticmethod
    def attributes():
        """
        Returns the attributes of the TestPool class.
        """
        return list(TestPool.__dataclass_fields__.keys())

    @property
    def param_dict(self):
        """
        Returns a dictionary mapping the slots to the param_lists.
        """
        return dict(zip(self.slots, self.param_lists))

    @property
    def is_supported(self):
        """
        Returns True if the pool is supported, otherwise False.
        """
        return self.exchange_type in SUPPORTED_EXCHANGES

    def set_balance_via_faucet(self, args: argparse.Namespace,
                               w3: Web3, token_id: int):
        """
        This method sets the balance of the given token to the given amount using the faucet.

        Args:
            args: The command-line arguments.
            w3: The Web3 instance.
            token_id: The token id.
        """
        token_address = [self.tkn0_address, self.tkn1_address][token_id]
        amount_wei = [self.tkn0_setBalance, self.tkn1_setBalance][token_id]
        token_balance = TestTokenBalance(token=token_address, balance=amount_wei)
        params = token_balance.faucet_params(wallet_address=self.pool_address)
        method_name = RPCEndpoint(
            "tenderly_setBalance"
            if token_balance.token.is_eth
            else "tenderly_setErc20Balance"
        )
        w3.provider.make_request(method=method_name, params=params)
        token_balance.balance = amount_wei
        if token_id == 0:
            self.tkn0_setBalance = token_balance
        else:
            self.tkn1_setBalance = token_balance
        args.logger.debug(f"Reset Balance to {amount_wei}")

    @staticmethod
    def load_test_pools():
        # Import pool data
        static_pool_data_testing_path = os.path.normpath(
            f"{TEST_DATA_DIR}/static_pool_data_testing.csv"
        )
        return pd.read_csv(static_pool_data_testing_path, dtype=str)
