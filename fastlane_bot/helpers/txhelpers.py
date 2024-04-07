"""
Defines a collection of transaction-related helper functions

This module defines the ``TxHelpers`` class, which provides a collection of properties
and methods for working with transactions:

- ``validate_and_submit_transaction``: Validates a transaction and then submits it to the arb contract
- ``check_and_approve_tokens``: Approves every token with zero allowance to the maximum allowance

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
__VERSION__ = "1.0"
__DATE__ = "01/May/2023"

from _decimal import Decimal

from json import dumps
from dataclasses import dataclass
from typing import List, Any, Dict, Optional

from web3.exceptions import TimeExhausted

from fastlane_bot.config import Config
from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.utils import num_format, log_format

MAX_UINT256 = 2 ** 256 - 1
ETH_RESOLUTION = 10 ** 18

@dataclass
class TxHelpers:
    """
    This class is used to organize web3 transaction tools.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    cfg: Config

    def __post_init__(self):
        self.chain_id = self.cfg.w3.eth.chain_id
        self.arb_contract = self.cfg.BANCOR_ARBITRAGE_CONTRACT
        self.arb_rewards_portion = Decimal(self.cfg.ARB_REWARDS_PPM) / 1_000_000
        self.wallet_address = self.cfg.w3.eth.account.from_key(self.cfg.ETH_PRIVATE_KEY_BE_CAREFUL).address

        if self.cfg.NETWORK == self.cfg.NETWORK_ETHEREUM:
            self.use_access_list = True
            self.send_transaction = self._send_private_transaction
        else:
            self.use_access_list = False
            self.send_transaction = self._send_regular_transaction

    def validate_and_submit_transaction(
        self,
        route_struct: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        expected_profit_gastkn: Decimal,
        expected_profit_usd: Decimal,
        log_object: Dict[str, Any],
        flashloan_struct: List[Dict]
    ) -> Optional[str]:
        """
        This method validates and submits a transaction to the arb contract.

        Args:
            route_struct: 
            src_amt: 
            src_address: 
            expected_profit_gastkn: 
            expected_profit_usd: 
            log_object: 
            flashloan_struct: 

        Returns:
            The hash of the transaction if executed, None otherwise.
        """

        self.cfg.logger.info("[helpers.txhelpers.validate_and_submit_transaction] Validating trade...")
        self.cfg.logger.debug(
            f"[helpers.txhelpers.validate_and_submit_transaction]:\n"
            f"- Routes: {route_struct}\n"
            f"- Source amount: {src_amt}\n"
            f"- Source token: {src_address}\n"
            f"- Expected profit: {num_format(expected_profit_gastkn)} GAS token ({num_format(expected_profit_usd)} USD)\n"
        )

        if self.cfg.SELF_FUND:
            fn_name = "fundAndArb"
            args = [route_struct, src_address, src_amt]
            value = src_amt if src_address == self.cfg.NATIVE_GAS_TOKEN_ADDRESS else 0
        else:
            fn_name = "flashloanAndArbV2"
            args = [flashloan_struct, route_struct]
            value = 0

        tx = self._create_transaction(self.arb_contract, fn_name, args, value)

        try:
            self._update_transaction(tx)
        except Exception as e:
            self.cfg.logger.info(f"Transaction {dumps(tx, indent=4)}\nGas estimation failed with {e}")
            return None

        tx["gas"] += self.cfg.DEFAULT_GAS_SAFETY_OFFSET

        raw_tx = self._sign_transaction(tx)

        gas_cost_wei = tx["gas"] * tx["maxFeePerGas"]
        if self.cfg.network.GAS_ORACLE_ADDRESS:
            gas_cost_wei += self.cfg.GAS_ORACLE_CONTRACT.caller.getL1Fee(raw_tx)

        gas_cost_eth = Decimal(gas_cost_wei) / ETH_RESOLUTION
        gas_cost_usd = gas_cost_eth * expected_profit_usd / expected_profit_gastkn

        gas_gain_eth = self.arb_rewards_portion * expected_profit_gastkn
        gas_gain_usd = self.arb_rewards_portion * expected_profit_usd

        self.cfg.logger.info(log_format(log_name="arb_with_gas", log_data={**log_object, "tx": tx}))

        self.cfg.logger.info(
            f"[helpers.txhelpers.validate_and_submit_transaction]:\n"
            f"- Expected cost: {num_format(gas_cost_eth)} GAS token ({num_format(gas_cost_usd)} USD)\n"
            f"- Expected gain: {num_format(gas_gain_eth)} GAS token ({num_format(gas_gain_usd)} USD)\n"
        )

        if gas_gain_eth > gas_cost_eth:
            self.cfg.logger.info("Executing profitable arb transaction")
            tx_hash = self.send_transaction(raw_tx)
            self._wait_for_transaction_receipt(tx_hash)
            return tx_hash
        else:
            self.cfg.logger.info("Discarding non-profitable arb transaction")
            return None

    def check_and_approve_tokens(self, tokens: List):
        """
        This method checks if tokens have been previously approved from the wallet address to the Arbitrage contract.
        If they are not already approved, it will submit approvals for each token specified in the given list of tokens.

        Args:
            tokens: A list of tokens to check/approve
        """

        for token_address in [token for token in tokens if token != self.cfg.NATIVE_GAS_TOKEN_ADDRESS]:
            token_contract = self.cfg.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            allowance = token_contract.caller.allowance(self.wallet_address, self.arb_contract.address)
            self.cfg.logger.info(f"Remaining allowance for token {token_address} = {allowance}")
            if allowance == 0:
                tx = self._create_transaction(token_contract, "approve", [self.arb_contract.address, MAX_UINT256], 0)
                self._update_transaction(tx)
                raw_tx = self._sign_transaction(tx)
                tx_hash = self._send_regular_transaction(raw_tx)
                self._wait_for_transaction_receipt(tx_hash)

    def _create_transaction(self, contract, fn_name: str, args: list, value: int) -> dict:
        return {
            "type": 2,
            "chainId": self.chain_id,
            "from": self.wallet_address,
            "to": contract.address,
            "data": contract.encode_abi(fn_name=fn_name, args=args),
            "value": value,
            "nonce": self.cfg.w3.eth.get_transaction_count(self.wallet_address),
            "maxFeePerGas": self.cfg.w3.eth.gas_price,
            "maxPriorityFeePerGas": self.cfg.w3.eth.max_priority_fee
        }

    def _update_transaction(self, tx: dict):
        tx["gas"] = self.cfg.w3.eth.estimate_gas(tx) # occasionally throws an exception
        if self.use_access_list:
            result = self.cfg.w3.eth.create_access_list(tx) # rarely throws an exception
            if tx["gas"] > result["gasUsed"]:
                tx["gas"] = result["gasUsed"]
                tx["accessList"] = [
                    {
                        "address": access_item["address"],
                        "storageKeys": [storage_key.hex() for storage_key in access_item["storageKeys"]]
                    }
                    for access_item in result["accessList"]
                ]

    def _sign_transaction(self, tx: dict) -> str:
        return self.cfg.w3.eth.account.sign_transaction(tx, self.cfg.ETH_PRIVATE_KEY_BE_CAREFUL).rawTransaction

    def _send_regular_transaction(self, raw_tx: str) -> str:
        return self.cfg.w3.eth.send_raw_transaction(raw_tx).hex()

    def _send_private_transaction(self, raw_tx: str) -> str:
        response = self.cfg.w3.provider.make_request(
            method="eth_sendPrivateTransaction",
            params=[{"tx": raw_tx, "maxBlockNumber": hex(self.cfg.w3.eth.block_number + 10), "preferences": {"fast": True}}]
        )
        assert "result" in response, f"Private transaction failed: {dumps(response, indent=4)}"
        return response["result"]

    def _wait_for_transaction_receipt(self, tx_hash: str):
        try:
            tx_receipt = self.cfg.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.cfg.logger.info(f"Transaction {tx_hash} completed: {dumps(tx_receipt, indent=4)}")
        except TimeExhausted as _:
            self.cfg.logger.info(f"Transaction {tx_hash} stuck in mempool; moving on")
