"""
Transaction handlers for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__ = "01/May/2023"

import asyncio
import nest_asyncio
from _decimal import Decimal

from json import loads
from dataclasses import dataclass
from typing import List, Any, Dict, Optional

import requests
from alchemy import Network, Alchemy
from web3.exceptions import TimeExhausted

from fastlane_bot.config import Config
from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.utils import num_format, log_format, num_format_float, int_prefix

nest_asyncio.apply()

MAX_UINT256 = 2 ** 256 - 1
ETH_DECIMALS = 10 ** 18

@dataclass
class TxHelpers:
    """
    This class is used to organize web3 transaction tools.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    ConfigObj: Config

    def __post_init__(self):

        if self.ConfigObj.network.DEFAULT_PROVIDER != "tenderly":
            self.alchemy = Alchemy(
                api_key=self.ConfigObj.WEB3_ALCHEMY_PROJECT_ID,
                network=Network.ETH_MAINNET,
                max_retries=3,
            )
        self.arb_contract = self.ConfigObj.BANCOR_ARBITRAGE_CONTRACT
        self.web3 = self.ConfigObj.w3
        # Set the local account
        self.local_account = self.web3.eth.account.from_key(
            self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL
        )

        # Set the public address
        self.wallet_address = str(self.local_account.address)

        self.alchemy_api_url = self.ConfigObj.RPC_URL

    def validate_and_submit_transaction(
        self,
        route_struct: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        expected_profit_gastkn: Decimal,
        expected_profit_usd: Decimal,
        log_object: Dict[str, Any],
        flashloan_struct: List[Dict[str, int or str]],
    ) -> Optional[Dict[str, Any]]:
        """
        Validates and submits a transaction to the arb contract.
        """

        self.ConfigObj.logger.info(
            "[helpers.txhelpers.validate_and_submit_transaction] Validating trade..."
        )
        self.ConfigObj.logger.debug(
            f"[helpers.txhelpers.validate_and_submit_transaction] \nRoute to execute: routes: {route_struct}, sourceAmount: {src_amt}, source token: {src_address}, expected profit in GAS TOKEN: {num_format(expected_profit_gastkn)} \n\n"
        )

        # Get pending block
        pending_block = self.web3.eth.get_block("pending")

        arb_tx = self.build_transaction_with_gas(
            routes=route_struct,
            src_address=src_address,
            src_amt=src_amt,
            gas_price=pending_block.get("baseFeePerGas"),
            max_priority=int(self.get_max_priority_fee_per_gas_alchemy() * self.ConfigObj.DEFAULT_GAS_PRICE_OFFSET),
            nonce=self.web3.eth.get_transaction_count(self.wallet_address),
            flashloan_struct=flashloan_struct
        )

        if arb_tx is None:
            self.ConfigObj.logger.info(
                "[helpers.txhelpers.validate_and_submit_transaction] Failed to construct trade. "
                "This is expected to happen occasionally, discarding..."
            )
            return None

        gas_estimate = arb_tx["gas"]

        current_gas_price = arb_tx["maxFeePerGas" if "maxFeePerGas" in arb_tx else "gasPrice"]

        signed_arb_tx = self.web3.eth.account.sign_transaction(arb_tx, self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL)

        gas_cost_wei = int(current_gas_price * gas_estimate * self.ConfigObj.EXPECTED_GAS_MODIFIER)

        if self.ConfigObj.network.GAS_ORACLE_ADDRESS:
            gas_cost_wei += asyncio.get_event_loop().run_until_complete(
                asyncio.gather(self.ConfigObj.GAS_ORACLE_CONTRACT.caller.getL1Fee(signed_arb_tx.rawTransaction))
            )

        gas_cost_eth = Decimal(gas_cost_wei) / ETH_DECIMALS

        # Gas cost in usd can be estimated using the profit usd/eth rate
        gas_cost_usd = gas_cost_eth * expected_profit_usd / expected_profit_gastkn

        # Multiply by reward percentage, taken from the arb contract
        adjusted_reward_eth = Decimal(Decimal(expected_profit_gastkn) * Decimal(self.ConfigObj.ARB_REWARD_PERCENTAGE))
        adjusted_reward_usd = adjusted_reward_eth * expected_profit_usd / expected_profit_gastkn

        transaction_log = {
            "block_number": pending_block["number"],
            "gas": gas_estimate,
            "max_gas_fee_wei": current_gas_price,
            "gas_cost_eth": num_format_float(gas_cost_eth),
            "gas_cost_usd": +num_format_float(gas_cost_usd),
        }

        if "maxPriorityFeePerGas" in arb_tx:
            transaction_log["base_fee_wei"] = current_gas_price - arb_tx["maxPriorityFeePerGas"]
            transaction_log["priority_fee_wei"] = arb_tx["maxPriorityFeePerGas"]

        log_json = {**log_object, **transaction_log}

        self.ConfigObj.logger.info(log_format(log_data=log_json, log_name="arb_with_gas"))

        if adjusted_reward_eth > gas_cost_eth:
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.validate_and_submit_transaction] Expected reward of {num_format(adjusted_reward_eth)} GAS TOKEN vs cost of {num_format(gas_cost_eth)} GAS TOKEN in gas, executing arb."
            )
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.validate_and_submit_transaction] Expected reward of {num_format(adjusted_reward_usd)} USD vs cost of {num_format(gas_cost_usd)} USD in gas, executing arb."
            )

            # Submit the transaction
            if "tenderly" in self.web3.provider.endpoint_uri or self.ConfigObj.NETWORK != "ethereum":
                tx_hash = self.submit_regular_transaction(signed_arb_tx)
            else:
                tx_hash = self.submit_private_transaction(signed_arb_tx, pending_block["number"])
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.validate_and_submit_transaction] Arbitrage executed, tx hash: {tx_hash}"
            )
            return tx_hash
        else:
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.validate_and_submit_transaction] Gas price too expensive! profit of {num_format(adjusted_reward_eth)} GAS TOKEN vs gas cost of {num_format(gas_cost_eth)} GAS TOKEN. Abort, abort!\n\n"
            )
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.validate_and_submit_transaction] Gas price too expensive! profit of {num_format(adjusted_reward_usd)} USD vs gas cost of {num_format(gas_cost_usd)} USD. Abort, abort!\n\n"
            )
            return None

    def get_access_list(self, transaction_data, expected_gas):
        json_data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_createAccessList",
            "params": [
                {
                    "from": self.wallet_address,
                    "to": self.arb_contract.address,
                    "gas": expected_gas,
                    "data": transaction_data
                }
            ]
        }
        response = requests.post(self.alchemy_api_url, json=json_data)
        return loads(response.text)["result"]["accessList"]

    def construct_contract_function(
        self,
        routes: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        gas_price: int,
        max_priority: int,
        nonce: int,
        flashloan_struct=None,
    ):
        """
        Builds the transaction using the Arb Contract function. This version can generate transactions using flashloanAndArb and flashloanAndArbV2.

        routes: the routes to be used in the transaction
        src_amt: the amount of the source token to be sent to the transaction
        gas_price: the gas price to be used in the transaction

        returns: the transaction function ready to be submitted
        """
        if self.ConfigObj.SELF_FUND:
            return self._build_transaction(
                function_call=self.arb_contract.functions.fundAndArb(routes, src_address, src_amt),
                base_gas_price=gas_price,
                max_priority_fee=max_priority,
                nonce=nonce,
                value=src_amt if src_address in self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS else 0
            )

        elif flashloan_struct is None:
            return self._build_transaction(
                function_call=self.arb_contract.functions.flashloanAndArb(routes, src_address, src_amt),
                base_gas_price=gas_price,
                max_priority_fee=max_priority,
                nonce=nonce
            )

        else:
            return self._build_transaction(
                function_call=self.arb_contract.functions.flashloanAndArbV2(flashloan_struct, routes),
                base_gas_price=gas_price,
                max_priority_fee=max_priority,
                nonce=nonce
            )

    def build_transaction_with_gas(
        self,
        routes: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        gas_price: int,
        max_priority: int,
        nonce: int,
        access_list: bool = True,
        flashloan_struct: List[Dict[str, int or str]] = None,
    ):
        """
        Builds the transaction to be submitted to the blockchain.

        routes: the routes to be used in the transaction
        src_amt: the amount of the source token to be sent to the transaction
        gas_price: the gas price to be used in the transaction

        returns: the transaction to be submitted to the blockchain
        """

        try:
            transaction = self.construct_contract_function(
                routes=routes,
                src_amt=src_amt,
                src_address=src_address,
                gas_price=gas_price,
                max_priority=max_priority,
                nonce=nonce,
                flashloan_struct=flashloan_struct,
            )
        except Exception as e:
            self.ConfigObj.logger.debug(
                f"[helpers.txhelpers.build_transaction_with_gas] Error when building transaction: {e.__class__.__name__} {e}"
            )
            if "max fee per gas less than block base fee" in str(e):
                try:
                    message = str(e)
                    baseFee = int_prefix(message.split("baseFee: ")[1])
                    transaction = self.construct_contract_function(
                        routes=routes,
                        src_amt=src_amt,
                        src_address=src_address,
                        gas_price=baseFee,
                        max_priority=max_priority,
                        nonce=nonce,
                        flashloan_struct=flashloan_struct,
                    )
                except Exception as e:
                    self.ConfigObj.logger.warning(
                        f"[helpers.txhelpers.build_transaction_with_gas] (***1***) \n"
                        f"Error when building transaction, this is expected to happen occasionally, discarding. Exception: {e.__class__.__name__} {e}"
                    )
                    return None
            else:
                self.ConfigObj.logger.info(f"gas_price = {gas_price}, max_priority = {max_priority}")
                self.ConfigObj.logger.warning(
                    f"[helpers.txhelpers.build_transaction_with_gas] (***2***) \n"
                    f"Error when building transaction, this is expected to happen occasionally, discarding. Exception: {e.__class__.__name__} {e}"
                )
                return None

        try:
            estimated_gas = self.web3.eth.estimate_gas(transaction=transaction) + self.ConfigObj.DEFAULT_GAS_SAFETY_OFFSET
        except Exception as e:
            self.ConfigObj.logger.warning(
                f"[helpers.txhelpers.build_transaction_with_gas] Failed to estimate gas for transaction because the "
                f"transaction is likely fail. Most often this is due to an arb opportunity already being closed, "
                f"but it can include other bugs. This is expected to happen occasionally, discarding. Exception: {e}"
            )
            return None

        try:
            if access_list and self.ConfigObj.NETWORK_NAME in "ethereum":
                transaction["accessList"] = self.get_access_list(transaction_data=transaction["data"], expected_gas=estimated_gas)
                self.ConfigObj.logger.debug(
                    f"[helpers.txhelpers.build_transaction_with_gas] Transaction after access list: {transaction}"
                )
                estimated_gas_after = self.web3.eth.estimate_gas(transaction=transaction) + self.ConfigObj.DEFAULT_GAS_SAFETY_OFFSET
                self.ConfigObj.logger.debug(
                    f"[helpers.txhelpers.build_transaction_with_gas] gas before access list: {estimated_gas}, after access list: {estimated_gas_after}"
                )
                if estimated_gas > estimated_gas_after:
                    estimated_gas = estimated_gas_after
        except Exception as e:
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.build_transaction_with_gas] Failed to apply access list to transaction. Exception: {e}"
            )

        transaction["gas"] = estimated_gas
        return transaction

    def _build_transaction(
            self,
            function_call,
            nonce: int,
            base_gas_price: int = 0,
            max_priority_fee: int = 0,
            value: int = 0
    ) -> Any:
        """
        Builds the transaction to be submitted to the blockchain.

        maxFeePerGas: the maximum gas price to be paid for the transaction
        maxPriorityFeePerGas: the maximum miner tip to be given for the transaction
        value: The amount of ETH to send - only relevant if not using Flashloans
        The following condition must be met:
        maxFeePerGas <= baseFee + maxPriorityFeePerGas

        returns: the transaction to be submitted to the blockchain
        """

        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            self.wallet_address = self.ConfigObj.BINANCE14_WALLET_ADDRESS
            
        if self.ConfigObj.NETWORK in ["ethereum", "coinbase_base"]:
            tx_details = {
                "type": 2,
                "maxFeePerGas": base_gas_price + max_priority_fee,
                "maxPriorityFeePerGas": max_priority_fee,
                "from": self.wallet_address,
                "nonce": nonce,
                "value": value
            }
        else:
            tx_details =  {
                "type": 1,
                "gasPrice": base_gas_price + max_priority_fee,
                "from": self.wallet_address,
                "nonce": nonce,
                "value": value
            }

        return function_call.build_transaction(tx_details)

    def submit_regular_transaction(self, signed_tx) -> str:
        """
        Submits the transaction to the blockchain.

        :param signed_tx: the signed transaction to be submitted to the blockchain

        returns: the transaction hash of the submitted transaction
        """

        self.ConfigObj.logger.info(
            f"[helpers.txhelpers.submit_regular_transaction] Attempting to submit transaction {signed_tx}"
        )

        return self._submit_transaction(self.web3.eth.send_raw_transaction(signed_tx.rawTransaction))

    def submit_private_transaction(self, signed_tx, block_number: int) -> str:
        """
        Submits the transaction privately through Alchemy -> Flashbots RPC to mitigate frontrunning.

        :param signed_tx: the signed transaction to be submitted to the blockchain
        :param block_number: the current block number

        returns: The transaction receipt, or None if the transaction failed
        """

        self.ConfigObj.logger.info(
            f"[helpers.txhelpers.submit_private_transaction] Attempting to submit transaction to Flashbots"
        )

        params = [
            {
                "tx": signed_tx.rawTransaction.hex(),
                "maxBlockNumber": hex(block_number + 10),
                "preferences": {"fast": True},
            }
        ]

        response = self.alchemy.core.provider.make_request(
            method="eth_sendPrivateTransaction",
            params=params,
            method_name="eth_sendPrivateTransaction",
            headers={"accept": "application/json", "content-type": "application/json"},
        )

        if response != 400:
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.submit_private_transaction] Submitted transaction to Flashbots succeeded"
            )
            return self._submit_transaction(response.get("result"))
        else:
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.submit_private_transaction] Submitted transaction to Flashbots failed with response = {response}"
            )
            return None

    def _submit_transaction(self, tx_hash) -> str:
        try:
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_hash == tx_receipt["transactionHash"]
            return tx_hash
        except TimeExhausted as e:
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers._submit_transaction] Transaction timeout (stuck in mempool); moving on"
            )
            return None

    def get_max_priority_fee_per_gas_alchemy(self) -> int:
        """
        Queries the Alchemy API to get an estimated max priority fee per gas
        """
        if self.ConfigObj.NETWORK in ["ethereum", "coinbase_base"]:
            return 0

        response = requests.post(
            self.alchemy_api_url,
            json={"id": 1, "jsonrpc": "2.0", "method": "eth_maxPriorityFeePerGas"},
            headers={"accept": "application/json", "content-type": "application/json"},
        )
        return int(loads(response.text)["result"].split("0x")[1], 16)

    def check_and_approve_tokens(self, tokens: List):
        """
        This function checks if tokens have been previously approved from the wallet address to the Arbitrage contract.
        If they are not already approved, it will submit approvals for each token specified in Flashloan tokens.
        :param tokens: the list of tokens to check/approve
        """

        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            owner_address = self.ConfigObj.BINANCE14_WALLET_ADDRESS
        else:
            owner_address = self.wallet_address

        for token_address in [token for token in tokens if token != self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS]:
            token_contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
            allowance = token_contract.caller.allowance(owner_address, self.arb_contract.address)
            self.ConfigObj.logger.info(f"Remaining allowance for token {token_address} = {allowance}")
            if allowance > 0:
                continue

            base_gas_price = self.web3.eth.get_block("pending").get("baseFeePerGas")
            max_priority_fee = self.get_max_priority_fee_per_gas_alchemy()
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)

            for attempt in [1, 2]:
                tx = self._build_transaction(
                    function_call=token_contract.functions.approve(self.arb_contract.address, MAX_UINT256),
                    base_gas_price=base_gas_price,
                    max_priority_fee=max_priority_fee,
                    nonce=nonce
                )

                self.ConfigObj.logger.info(f"Attempt {attempt} for approving token {token_address}")

                try:
                    signed_tx = self.web3.eth.account.sign_transaction(tx, self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL)
                    tx_hash = self.submit_regular_transaction(signed_tx)
                    break
                except Exception as e:
                    self.ConfigObj.logger.info(f"Attempt {attempt} failed: {e.__class__.__name__} {e}")
                    if "max fee per gas less than block base fee" in str(e):
                        base_gas_price = int_prefix(str(e).split("baseFee: ")[1])
                    else:
                        tx_hash = None
                        break

                assert tx_hash is not None, f"Failed to approve token {token_address}"
