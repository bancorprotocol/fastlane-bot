"""This class handles logic to automatically shut down Bancor V3 pools. The bot checks Bancor V3 Vault token balances
vs staked balances. If the vault's token balance exceeds the staked balance, it will submit a transaction calling the
withdrawPOL function for the token.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List

from fastlane_bot.data.abi import (
    BANCOR_V3_NETWORK_ABI,
    BANCOR_V3_NETWORK_SETTINGS,
    BANCOR_V3_POOL_COLLECTION_ABI,
)
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.helpers.txhelpers import TxHelpers, int_prefix


@dataclass
class AutomaticPoolShutdown:
    """
    This is a standalone class to find Bancor V3 liquidity pools that are in surplus and automatically shut them down

    Parameters
    ----------
    mgr: Manager
        The Manager object
    shutdown_whitelist: List[Any] = None
        A list of tokens to shut down
    active_pools: Dict[str, Any] = field(default_factory=dict)
        A dictionary of active pools
    polling_interval: int = 12
        The time to wait between checks
    arb_mode: str = "pool_shutdown"
        The mode to run
    """

    mgr: Manager
    shutdown_whitelist: List[Any] = None
    active_pools: Dict[str, Any] = field(default_factory=dict)
    polling_interval: int = 12
    arb_mode: str = "pool_shutdown"

    def __post_init__(self):
        self.tx_helpers = TxHelpers(ConfigObj=self.mgr.cfg)
        self.bancor_network_contract = self.mgr.web3.eth.contract(
            address=self.mgr.web3.to_checksum_address(
                self.mgr.cfg.BANCOR_V3_NETWORK_ADDRESS
            ),
            abi=BANCOR_V3_NETWORK_ABI,
        )
        self.bancor_settings_contract = self.mgr.web3.eth.contract(
            address=self.mgr.web3.to_checksum_address(
                self.mgr.cfg.BANCOR_V3_NETWORK_SETTINGS
            ),
            abi=BANCOR_V3_NETWORK_SETTINGS,
        )
        self.pool_collection_contract = self.mgr.web3.eth.contract(
            address=self.mgr.web3.to_checksum_address(
                self.mgr.cfg.BANCOR_V3_POOL_COLLECTOR_ADDRESS
            ),
            abi=BANCOR_V3_POOL_COLLECTION_ABI,
        )
        self.get_whitelist()

    def main_loop(self):
        """
        Run this function in a loop.
        """
        while True:
            self.main_sequence()

    def main_sequence(self):
        """
        This runs the main sequence of the mode:

        1: searches active pools to get their status and staked balance
        2: checks the balance of the Bancor V3 vault & compares it to the staked balance
        3: if a token is found in surplus, submits a TX to shut the pool down

        """
        self.mgr.cfg.logger.info(f"\n\nRunning AutomaticPoolShutdown main sequence.")
        self.parse_active_pools()
        self.mgr.cfg.logger.info(
            "Pool data collected, checking vault token balances and comparing."
        )
        tkn_to_shutdown = self.iterate_active_pools()
        if tkn_to_shutdown is not None:
            self.mgr.cfg.logger.info(
                f"Found pool to shut down: {tkn_to_shutdown}, initiating launch sequence."
            )
            self.generate_shutdown_tx(tkn=tkn_to_shutdown)
        else:
            self.mgr.cfg.logger.info(
                "No pools found to shut down. Waiting and restarting sequence."
            )
        time.sleep(self.polling_interval)

    def get_whitelist(self):
        """
        This function gets the token whitelist from the Bancor V3 Network Settings contract.

        """
        self.shutdown_whitelist = (
            self.bancor_settings_contract.caller.tokenWhitelistForPOL()
        )

    def parse_active_pools(self):
        """
        This function uses a multicall to get pool details for each Bancor V3 token. If the pool is active, it updates the dict with the current staked balance. If the pool is inactive, it removes it from the dictionary if it existed previously.
        """
        for tkn in self.shutdown_whitelist:
            (
                pool_token,
                trading_fee_PPM,
                trading_enabled,
                depositing_enabled,
                average_rate,
                tkn_pool_liquidity,
            ) = self.pool_collection_contract.functions.poolData(tkn).call()
            tkn_results = list(tkn_pool_liquidity)
            (
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                staked_balance,
            ) = tkn_results
            if tkn_trading_liquidity > 0 and trading_enabled:
                self.active_pools[tkn] = staked_balance

    def iterate_active_pools(self):
        """
        This function iterates over each active pool and compares the balance of the Bancor V3 vault vs the staked balance. If the staked balance is greater, it will call the autoshutdown function.
        """
        for tkn in self.active_pools.keys():
            if tkn == self.mgr.cfg.ETH_ADDRESS:
                eth_balance = self.mgr.web3.eth.get_balance(
                    self.mgr.web3.to_checksum_address(self.mgr.cfg.BANCOR_V3_VAULT)
                )
                if eth_balance > 0 and eth_balance > self.active_pools[tkn]:
                    return tkn
            else:
                tkn_balance = self.get_vault_balance_of_tkn(tkn)
                if tkn_balance > 0 and tkn_balance > self.active_pools[tkn]:
                    return tkn
        return None

    def get_vault_balance_of_tkn(self, tkn: str) -> int:
        """
        Get the ERC20 token balance of the POL contract

        Parameters
        ----------
        tkn: str
            The token address

        Returns
        -------
        int
            The token balance

        """

        tkn_contract = self.mgr.get_or_create_token_contracts(
            self.mgr.web3,
            self.mgr.erc20_contracts,
            self.mgr.web3.to_checksum_address(tkn),
        )
        return tkn_contract.functions.balanceOf(self.mgr.cfg.BANCOR_V3_VAULT).call()

    def generate_shutdown_tx(self, tkn: str) -> str:
        """
        :param tkn: the token of the pool to shut down.

        Generates and submits the pool shutdown transaction
        """
        # Get current base fee for pending block
        gas_price = self.mgr.web3.eth.get_block("pending").get("baseFeePerGas")
        # Get the current recommended priority fee from Alchemy, and increase it by our offset
        max_priority_gas = int(
            self.tx_helpers.get_max_priority_fee_per_gas_alchemy()
            * self.mgr.cfg.DEFAULT_GAS_PRICE_OFFSET
        )
        transaction = self.build_transaction(
            tkn=tkn,
            gas_price=gas_price,
            max_priority_gas=max_priority_gas,
            nonce=self.tx_helpers.get_nonce(),
        )
        return (
            self.tx_helpers.submit_private_transaction(
                arb_tx=transaction, block_number=self.mgr.web3.eth.block_number
            )
            if transaction is not None
            else None
        )

    def build_transaction(
        self, tkn: str, gas_price: int, max_priority_gas: int, nonce: int
    ):
        """
        Handles the transaction generation

        Parameters
        ----------
        tkn: str
            The token address
        gas_price: int
            The gas price
        max_priority_gas: int
            The max priority gas
        nonce: int
            The nonce

        Returns
        --------
        str
            The transaction hash if successful, None if not
        """

        try:
            return self.bancor_network_contract.functions.withdrawPOL(
                self.mgr.web3.to_checksum_address(tkn)
            ).build_transaction(
                self.tx_helpers.build_tx(
                    base_gas_price=gas_price,
                    max_priority_fee=max_priority_gas,
                    nonce=nonce,
                )
            )
        except Exception as e:
            self.mgr.cfg.logger.debug(
                f"Error when building transaction: {e.__class__.__name__} {e}"
            )
            if "max fee per gas less than block base fee" in str(e):
                try:
                    return self._build_transaction(e, max_priority_gas, tkn, nonce)
                except Exception as e:
                    self.mgr.cfg.logger.debug(
                        f"(***2***) Error when building transaction: {e.__class__.__name__} {e}"
                    )
                    return None

    def _build_transaction(self, e: Exception, max_priority: int, tkn: str, nonce: int):
        """
        Handles the transaction generation logic.

        Parameters
        ----------
        e: Exception
            The exception
        max_priority: int
            The max priority fee input
        tkn: str
            The token address
        nonce: int
            The nonce

        Returns
        -------
        str
            The transaction hash if successful, None if not

        """
        message = str(e)
        baseFee = int_prefix(message.split("baseFee: ")[1])
        return self.bancor_network_contract.functions.withdrawPOL(
            self.mgr.web3.to_checksum_address(tkn)
        ).build_transaction(
            self.tx_helpers.build_tx(
                base_gas_price=baseFee,
                max_priority_fee=max_priority,
                nonce=nonce,
            )
        )
