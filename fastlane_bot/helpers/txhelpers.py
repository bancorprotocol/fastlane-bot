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

# import itertools
# import random
# import time
from dataclasses import dataclass
from typing import List, Any, Dict, Tuple, Optional

# import eth_abi
# import math
# import pandas as pd
import requests
from alchemy import Network, Alchemy
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.types import TxReceipt

# from fastlane_bot.config import *  # TODO: PRECISE THE IMPORTS or from .. import config
# from fastlane_bot.db.models import Token, Pool
# import fastlane_bot.config as c
# from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.config import Config
from fastlane_bot.data.abi import *  # TODO: PRECISE THE IMPORTS or from .. import abi
from fastlane_bot.utils import num_format, log_format, num_format_float, int_prefix, count_bytes

nest_asyncio.apply()


@dataclass
class TxHelper:
    """
    A class to represent a flashloan arbitrage.

    Attributes
    ----------
    usd_gas_limit : float
        The USD gas limit.
    gas_price_multiplier : float
        The gas price multiplier.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    ConfigObj: Config
    usd_gas_limit: float = 20  # TODO this needs to be dynamic
    gas_price_multiplier: float = 1.2

    def __post_init__(self):
        self.PRIVATE_KEY: str = self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL
        self.COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true"
        self.arb_contract: Any = self.ConfigObj.BANCOR_ARBITRAGE_CONTRACT
        self.w3: Web3 = self.ConfigObj.w3

    @property
    def wallet_address(self) -> str:
        """Get the wallet address.

        Returns:
            str: The wallet address.
        """
        return self.ConfigObj.LOCAL_ACCOUNT.address

    @property
    def wallet_balance(self) -> Tuple[Any, int]:
        """Get the wallet balance in Ether.

        Returns:
            float: The wallet balance in Ether.
        """
        balance = self.w3.eth.getBalance(self.wallet_address)
        return balance, self.w3.fromWei(balance, "ether")

    @property
    def wei_balance(self) -> int:
        """Get the wallet balance in Wei.

        Returns:
            int: The wallet balance in Wei.
        """
        return self.wallet_balance[0]

    @property
    def ether_balance(self) -> float:
        """Get the wallet balance in Ether.

        Returns:
            float: The wallet balance in Ether.
        """
        return self.wallet_balance[1]

    @property
    def nonce(self):
        return self.ConfigObj.w3.eth.get_transaction_count(
            self.ConfigObj.LOCAL_ACCOUNT.address
        )

    @property
    def gas_limit(self):
        return self.get_gas_limit_from_usd(self.usd_gas_limit)

    @property
    def base_gas_price(self):
        """
        Get the base gas price from the Web3 instance.
        """
        return self.ConfigObj.w3.eth.gasPrice

    @property
    def gas_price_gwei(self):
        """
        Get the gas price from the Web3 instance (gwei).
        """
        return self.base_gas_price / 1e9

    @property
    def ether_price_usd(self):
        """
        Get the ether price in USD.
        """
        response = requests.get(self.COINGECKO_URL)
        data = response.json()
        return data["ethereum"]["usd"]

    @property
    def deadline(self):
        return (
            self.ConfigObj.w3.eth.getBlock("latest")["timestamp"]
            + self.ConfigObj.DEFAULT_BLOCKTIME_DEVIATION
        )

    def get_gas_limit_from_usd(self, gas_cost_usd: float) -> int:
        """Calculate the gas limit based on the desired gas cost in USD.

        Args:
            gas_cost_usd (float): The desired gas cost in USD.

        Returns:
            int: The calculated gas limit.
        """
        ether_cost = gas_cost_usd / self.ether_price_usd
        gas_limit = ether_cost / self.gas_price_gwei * 1e9
        return int(gas_limit)


@dataclass
class TxHelpers:
    """
    This class is used to organize web3 transaction tools.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    ConfigObj: Config
    # This is used for the Alchemy SDK
    network = Network.ETH_MAINNET

    def __post_init__(self):

        if self.ConfigObj.network.DEFAULT_PROVIDER != "tenderly":
            self.alchemy = Alchemy(
                api_key=self.ConfigObj.WEB3_ALCHEMY_PROJECT_ID,
                network=self.network,
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
        self.nonce = self.get_nonce()

    def _get_transaction_info(self) -> (int, int, int, int):
        # Get current base fee for pending block
        current_gas_price = self.web3.eth.get_block("pending").get("baseFeePerGas")

        # Get the current recommended priority fee from Alchemy, and increase it by our offset
        current_max_priority_gas = (
            int(
                self.get_max_priority_fee_per_gas_alchemy()
                * self.ConfigObj.DEFAULT_GAS_PRICE_OFFSET
            )
            if self.ConfigObj.NETWORK in ["ethereum", "coinbase_base"]
            else 0
        )

        # Get current block number
        block_number = int(self.web3.eth.get_block("latest")["number"])

        # Get current nonce for our account
        nonce = self.get_nonce()

        return current_gas_price, current_max_priority_gas, block_number, nonce

    def _get_prices_info(
            self,
            current_gas_price: int,
            gas_estimate: int,
            expected_profit_usd: Decimal,
            expected_profit_eth: Decimal,
            raw_transaction: Any
        ) -> (int, int, int, int):
        # Multiply expected gas by 0.8 to account for actual gas usage vs expected.
        gas_cost_eth = (
            Decimal(str(current_gas_price))
            * Decimal(str(gas_estimate))
            * Decimal(self.ConfigObj.EXPECTED_GAS_MODIFIER)
            / Decimal("10") ** Decimal("18")
        )

        if self.ConfigObj.network.GAS_ORACLE_ADDRESS:
            layer_one_gas_fee = self._get_layer_one_gas_fee(raw_transaction)
            gas_cost_eth += layer_one_gas_fee

        # Gas cost in usd can be estimated using the profit usd/eth rate
        gas_cost_usd = gas_cost_eth * expected_profit_usd / expected_profit_eth

        # Multiply by reward percentage, taken from the arb contract
        adjusted_reward_eth = Decimal(Decimal(expected_profit_eth) * Decimal(self.ConfigObj.ARB_REWARD_PERCENTAGE))
        adjusted_reward_usd = adjusted_reward_eth * expected_profit_usd / expected_profit_eth

        return gas_cost_eth, gas_cost_usd, adjusted_reward_eth, adjusted_reward_usd

    def validate_and_submit_transaction(
        self,
        route_struct: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        expected_profit_gastkn: Decimal,
        expected_profit_usd: Decimal,
        verbose: bool = False,
        safety_override: bool = False,
        log_object: Dict[str, Any] = None,
        flashloan_struct: List[Dict[str, int or str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Validates and submits a transaction to the arb contract.

        Parameters
        ----------

        """

        if expected_profit_gastkn < self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN:
            self.ConfigObj.logger.info(
                f"Transaction below minimum profit, reverting... /*_*\\"
            )
            return None

        if verbose:
            self.ConfigObj.logger.info(
                "[helpers.txhelpers.validate_and_submit_transaction] Validating trade..."
            )
            self.ConfigObj.logger.debug(
                f"[helpers.txhelpers.validate_and_submit_transaction] \nRoute to execute: routes: {route_struct}, sourceAmount: {src_amt}, source token: {src_address}, expected profit in GAS TOKEN: {num_format(expected_profit_gastkn)} \n\n"
            )

        current_gas_price, current_max_priority_gas, block_number, nonce = self._get_transaction_info()

        arb_tx = self.build_transaction_with_gas(
            routes=route_struct,
            src_address=src_address,
            src_amt=src_amt,
            gas_price=current_gas_price,
            max_priority_fee=current_max_priority_gas,
            nonce=nonce,
            test_fake_gas=False,
            flashloan_struct=flashloan_struct,
        )

        if arb_tx is None:
            self.ConfigObj.logger.info(
                "[helpers.txhelpers.validate_and_submit_transaction] Failed to construct trade. "
                "This is expected to happen occasionally, discarding..."
            )
            return None
        gas_estimate = arb_tx["gas"]

        if "maxFeePerGas" in arb_tx:
            current_gas_price = arb_tx["maxFeePerGas"]
        else:
            current_gas_price = arb_tx["gasPrice"]

        signed_arb_tx = self.sign_transaction(arb_tx)

        gas_cost_eth, gas_cost_usd, adjusted_reward_eth, adjusted_reward_usd = self._get_prices_info(
            current_gas_price,
            gas_estimate,
            expected_profit_usd,
            expected_profit_gastkn,
            signed_arb_tx.rawTransaction
        )

        transaction_log = {
            "block_number": block_number,
            "gas": gas_estimate,
            "max_gas_fee_wei": current_gas_price,
            "gas_cost_eth": num_format_float(gas_cost_eth),
            "gas_cost_usd": +num_format_float(gas_cost_usd),
        }
        if "maxPriorityFeePerGas" in arb_tx:
            transaction_log["base_fee_wei"] = (
                current_gas_price - arb_tx["maxPriorityFeePerGas"]
            )
            transaction_log["priority_fee_wei"] = arb_tx["maxPriorityFeePerGas"]

        log_json = {**log_object, **transaction_log}

        self.ConfigObj.logger.info(
            log_format(log_data=log_json, log_name="arb_with_gas")
        )

        if adjusted_reward_eth > gas_cost_eth or safety_override:
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
                tx_hash = self.submit_private_transaction(signed_arb_tx, block_number)
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

    def get_access_list(self, transaction_data, expected_gas, eth_input=None):
        expected_gas = hex(expected_gas)
        json_data = (
            {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "eth_createAccessList",
                "params": [
                    {
                        "from": self.wallet_address,
                        "to": self.arb_contract.address,
                        "gas": expected_gas,
                        "data": transaction_data,
                    }
                ],
            }
            if eth_input is None
            else {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "eth_createAccessList",
                "params": [
                    {
                        "from": self.wallet_address,
                        "to": self.arb_contract.address,
                        "gas": expected_gas,
                        "value": hex(eth_input),
                        "data": transaction_data,
                    }
                ],
            }
        )
        response = requests.post(self.alchemy_api_url, json=json_data)
        if "failed to apply transaction" in response.text:
            return None
        else:
            access_list = json.loads(response.text)["result"]["accessList"]
            return access_list

    def construct_contract_function(
        self,
        routes: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
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
            return self.arb_contract.functions.fundAndArb(
                routes, src_address, src_amt
            )
        return self.arb_contract.functions.flashloanAndArbV2(
            flashloan_struct, routes
        )

    def _handle_function_build_exception(self, exception: Exception) -> int or None:
        """Handles exceptions that occur during transaction building.

        This method logs the exception and attempts to extract information from it. If the exception
        indicates that the maximum fee per gas is less than the block base fee, it extracts and returns
        the base fee. Otherwise, it logs a warning and returns None.

        Args:
            self: The instance of the class.
            exception (Exception): The exception raised during transaction building.

        Returns:
            int or None: The base fee if it can be extracted from the exception, otherwise None.

        """
        self.ConfigObj.logger.debug(
            f"[helpers.txhelpers.build_transaction_with_gas] Error when building transaction: {exception.__class__.__name__} {exception}"
        )
        if "max fee per gas less than block base fee" in str(exception):
            message = str(exception)
            return int_prefix(message.split("baseFee: ")[1])

        else:
            self.ConfigObj.logger.warning(
                f"[helpers.txhelpers.build_transaction_with_gas] (***2***) \n"
                f"Error when building transaction, this is expected to happen occasionally, discarding. Exception: {exception.__class__.__name__} {exception}"
            )
            return None

    def build_transaction_with_gas(
        self,
        routes: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        gas_price: int,
        max_priority_fee: int,
        nonce: int,
        access_list: bool = True,
        test_fake_gas: bool = False,
        flashloan_struct: List[Dict[str, int or str]] = None,
    ):
        """
        Builds the transaction to be submitted to the blockchain.

        routes: the routes to be used in the transaction
        src_amt: the amount of the source token to be sent to the transaction
        gas_price: the gas price to be used in the transaction

        returns: the transaction to be submitted to the blockchain
        """
        value = src_amt if (src_address == self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS and self.ConfigObj.SELF_FUND) else 0
        transaction = self.build_transaction_generic(
                self.construct_contract_function,
                routes,
                src_amt,
                src_address,
                flashloan_struct,
                gas_price=gas_price,
                max_priority_fee=max_priority_fee,
                nonce=nonce,
                value=value
        )
        if transaction is None:
            return None

        if test_fake_gas:
            transaction["gas"] = self.ConfigObj.DEFAULT_GAS
            return transaction

        try:
            estimated_gas = int(
                    self.web3.eth.estimate_gas(transaction=transaction)
                    + self.ConfigObj.DEFAULT_GAS_SAFETY_OFFSET
            )
        except Exception as e:
            self.ConfigObj.logger.warning(
                f"[helpers.txhelpers.build_transaction_with_gas] Failed to estimate gas for transaction because the "
                f"transaction is likely fail. Most often this is due to an arb opportunity already being closed, "
                f"but it can include other bugs. This is expected to happen occasionally, discarding. Exception: {e}"
            )
            return None
        try:
            if access_list and self.ConfigObj.NETWORK_NAME in "ethereum":
                access_list = self.get_access_list(
                    transaction_data=transaction["data"], expected_gas=estimated_gas
                )

                if access_list is not None:
                    transaction_after = transaction
                    transaction_after["accessList"] = access_list
                    self.ConfigObj.logger.debug(
                        f"[helpers.txhelpers.build_transaction_with_gas] Transaction after access list: {transaction}"
                    )
                    estimated_gas_after = (
                        self.web3.eth.estimate_gas(transaction=transaction_after)
                        + self.ConfigObj.DEFAULT_GAS_SAFETY_OFFSET
                    )
                    self.ConfigObj.logger.debug(
                        f"[helpers.txhelpers.build_transaction_with_gas] gas before access list: {estimated_gas}, after access list: {estimated_gas_after}"
                    )
                    if estimated_gas_after is not None:
                        if estimated_gas_after < estimated_gas:
                            transaction = transaction_after
                            estimated_gas = estimated_gas_after
                else:
                    self.ConfigObj.logger.info(
                        f"[helpers.txhelpers.build_transaction_with_gas] Failed to apply access list to transaction"
                    )
        except Exception as e:
            self.ConfigObj.logger.info(
                f"[helpers.txhelpers.build_transaction_with_gas] Failed to add Access List to transaction. This should not invalidate the transaction. Exception: {e}"
            )
        transaction["gas"] = estimated_gas
        return transaction

    def get_nonce(self):
        """
        Returns the nonce of the wallet address.
        """
        return self.web3.eth.get_transaction_count(self.wallet_address)

    def build_tx(
            self,
            nonce: int,
            gas_price: int = 0,
            max_priority_fee: int = 0,
            value: int = 0
    ) -> Dict[str, Any]:
        """
        Builds the transaction to be submitted to the blockchain.

        maxFeePerGas: the maximum gas price to be paid for the transaction
        maxPriorityFeePerGas: the maximum miner tip to be given for the transaction
        value: The amount of ETH to send - only relevant if not using Flashloans
        The following condition must be met:
        maxFeePerGas <= baseFee + maxPriorityFeePerGas

        returns: the transaction to be submitted to the blockchain
        """
        max_priority_fee = int(max_priority_fee)
        base_gas_price = int(gas_price)
        max_gas_price = base_gas_price + max_priority_fee

        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            self.wallet_address = self.ConfigObj.BINANCE14_WALLET_ADDRESS
            
        # if "tenderly" in self.web3.provider.endpoint_uri:
        #     print("Tenderly network detected: Manually setting maxFeePerFas and maxPriorityFeePerGas")
        #     max_gas_price = 3
        #     max_priority_fee = 3

        if self.ConfigObj.NETWORK in ["ethereum", "coinbase_base"]:
            tx_details = {
                "type": "0x2",
                "maxFeePerGas": max_gas_price,
                "maxPriorityFeePerGas": max_priority_fee,
                "from": self.wallet_address,
                "nonce": nonce,
            }
        else:
            tx_details =  {
                "gasPrice": max_gas_price,
                "from": self.wallet_address,
                "nonce": nonce,
            }
        tx_details["value"] = value
        return tx_details

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
            headers=self._get_headers,
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

    def sign_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Signs the transaction.

        transaction: the transaction to be signed

        returns: the signed transaction
        """
        return self.web3.eth.account.sign_transaction(
            transaction, self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL
        )

    @property
    def _get_alchemy_url(self):
        """
        Returns the Alchemy API URL with attached API key
        """
        return self.alchemy_api_url

    @property
    def _get_headers(self):
        """
        Returns the headers for the API call
        """
        return {"accept": "application/json", "content-type": "application/json"}

    @staticmethod
    def _get_payload(method: str, params: [] = None) -> Dict:
        """
        Generates the request payload for the API call. If the method is "eth_estimateGas", it attaches the params
        :param method: the API method to call
        """

        if method == "eth_estimateGas" or method == "eth_sendPrivateTransaction":
            return {"id": 1, "jsonrpc": "2.0", "method": method, "params": params}
        else:
            return {"id": 1, "jsonrpc": "2.0", "method": method}

    def _query_alchemy_api_gas_methods(self, method: str, params: list = None):
        """
        This queries the Alchemy API for a gas-related call which returns a Hex String.
        The Hex String can be decoded by casting it as an int like so: int(hex_str, 16)

        :param method: the API method to call
        """
        response = requests.post(
            self.alchemy_api_url,
            json=self._get_payload(method=method, params=params),
            headers=self._get_headers,
        )
        return int(json.loads(response.text)["result"].split("0x")[1], 16)

    def get_max_priority_fee_per_gas_alchemy(self):
        """
        Queries the Alchemy API to get an estimated max priority fee per gas
        """
        result = self._query_alchemy_api_gas_methods(method="eth_maxPriorityFeePerGas")
        return result

    def get_eth_gas_price_alchemy(self):
        """
        Returns an estimated gas price for the upcoming block
        """
        return self._query_alchemy_api_gas_methods(method="eth_gasPrice")

    def check_if_token_approved(self, token_address: str, owner_address = None, spender_address = None) -> bool:
        """
        This function checks if a token has already been approved.
        :param token_address: the token to approve
        :param owner_address: Optional param for specific debugging, otherwise it will be automatically set to the wallet address
        :param spender_address: Optional param for specific debugging, otherwise it will be set to the arb contract address

        returns:
            bool
        """
        owner_address = self.wallet_address if owner_address is None else owner_address
        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            owner_address = self.ConfigObj.BINANCE14_WALLET_ADDRESS

        spender_address = self.arb_contract.address if spender_address is None else spender_address

        token_contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)

        allowance = token_contract.caller.allowance(owner_address, spender_address)
        if type(allowance) == int:
            if allowance > 0:
                return True
            return False
        else:
            return False

    def build_transaction_generic(self, contract_function, *args, **kwargs):
        """Builds a transaction using a contract function with the provided arguments.

        This function attempts to construct a transaction by calling the given contract function
        with the provided arguments and keyword arguments. If an exception occurs during the
        transaction construction, it adjusts the gas price and retries the function call.

        Args:
            self: The instance of the class.
            contract_function: The contract function to be called to construct the transaction.
            *args: Positional arguments to be passed to the contract function.
            **kwargs: Keyword arguments to be passed to the contract function.

        Returns:
            The constructed transaction if successful, otherwise None.

        """
        try:
            transaction = contract_function(*args).build_transaction(self.build_tx(**kwargs))
        except Exception as e:
            new_base_fee = self._handle_function_build_exception(exception=e)
            if new_base_fee is None:
                return None
            try:
                kwargs['gas_price'] = new_base_fee
                transaction = contract_function(*args).build_transaction(self.build_tx(**kwargs))
            except Exception as e:
                self.ConfigObj.logger.warning(
                    f" Error when building transaction, this is expected to happen occasionally, discarding. (***1***)\n"
                    f"Exception: {e.__class__.__name__} {e}"
                )
                return None
        return transaction

    def approve_token_for_arb_contract(self, token_address: str, approval_amount: int = 115792089237316195423570985008687907853269984665640564039457584007913129639935):
        """
        This function submits a token approval to the Arb Contract. The default approval amount is the max approval.
        :param token_address: the token to approve
        :param approval_amount: the amount to approve. This is set to the max possible by default

        returns:
            transaction hash
        """
        current_gas_price = self.web3.eth.get_block("pending").get("baseFeePerGas")
        max_priority = int(self.get_max_priority_fee_per_gas_alchemy()) if self.ConfigObj.NETWORK in ["ethereum", "coinbase_base"] else 0

        token_contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)


        approve_tx = self.build_transaction_generic(
            token_contract.functions.approve,
            self.arb_contract.address,
            approval_amount,
            gas_price=current_gas_price,
            max_priority_fee=max_priority,
            nonce=self.get_nonce(),
            )
        if approve_tx is None:
            self.ConfigObj.logger.info(f"*****Failed to submit approval for token: {token_address}!*****")
            return None
        self.ConfigObj.logger.info(f"Submitting approval for token: {token_address}")

        return self.submit_regular_transaction(self.sign_transaction(approve_tx))

    def _get_layer_one_gas_fee(self, raw_transaction) -> Decimal:
        """
        Returns the expected layer one gas fee for a Mantle, Base, and Optimism transaction

        Args:
            raw_transaction: the raw transaction

        Returns:
            Decimal: the expected layer one gas fee
        """

        l1_data_fee = asyncio.get_event_loop().run_until_complete(
            asyncio.gather(self.ConfigObj.GAS_ORACLE_CONTRACT.caller.getL1Fee(raw_transaction)))[0]
        # Dividing by 10 ** 18 in order to convert from wei resolution to native-token resolution
        return Decimal(f"{l1_data_fee}e-18")
