"""
Submit handler for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__="01/May/2023"

import json
from dataclasses import dataclass, asdict
from typing import List, Any, Dict

import requests
from brownie.network.transaction import TransactionReceipt
from eth_utils import to_hex
from web3._utils.threads import Timeout
from web3._utils.transactions import fill_nonce
from web3.contract import ContractFunction
from web3.exceptions import TimeExhausted
from web3.types import TxParams

#import fastlane_bot.config as c
from .routehandler import RouteStruct
from ..data.abi import ERC20_ABI
from fastlane_bot.config import Config

@dataclass
class TxSubmitHandlerBase:
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
@dataclass
class TxSubmitHandler(TxSubmitHandlerBase):
    """
    A class that handles the submission of transactions to the blockchain.

    Attributes
    ----------
    route_struct: List[str]
        The route structure for a transaction. As required by the `BancorArbitrage` contract.
    src_amount: int
        The source amount for a transaction. (in wei)
    src_address: str
        The source address for a transaction. (checksummed)

    Methods
    -------
    _get_deadline(self) -> int:
        Gets the deadline for a transaction.
    _get_transaction(self, tx_details: TxParams) -> TxParams:
        Gets the transaction details for a given transaction.
    _get_transaction_receipt(self, tx_hash: str, timeout: int = DEFAULT_TIMEOUT) -> TransactionReceipt:
        Gets the transaction receipt for a given transaction.
    _get_transaction_receipt_with_timeout(self, tx_hash: str, timeout: int = DEFAULT_TIMEOUT) -> TransactionReceipt:
        Gets the transaction receipt for a given transaction with a timeout.

    """
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
    ConfigObj: Config
    route_struct: List[RouteStruct] = None
    src_address: str = None
    src_amount: int = None




    def __post_init__(self):
        self.w3 = self.ConfigObj.w3
        self.arb_contract = self.ConfigObj.BANCOR_ARBITRAGE_CONTRACT
        self.bancor_network_info = self.ConfigObj.BANCOR_NETWORK_INFO_CONTRACT
        # self.token_contract = Contract.from_abi(
        #     name="Token",
        #     address=self.src_address,
        #     abi=ERC20_ABI,
        # )
        self.token_contract = self.ConfigObj.w3.eth.contract(address=self.src_address, abi=ERC20_ABI)

    def _get_deadline(self) -> int:
        """
        Gets the deadline for a transaction.

        Returns
        -------
        int
            The deadline.
        """
        return (
            self.w3.eth.getBlock(self.w3.eth.block_number).timestamp
            + self.ConfigObj.DEFAULT_BLOCKTIME_DEVIATION
        )

    def _get_transaction(self, tx_details: TxParams) -> TxParams:
        """
        Gets the transaction details for a given transaction.

        Parameters
        ----------
        tx_details: TxParams
            The transaction details.

        Returns
        -------
        TxParams
            The transaction details.
        """
        return fill_nonce(self.ConfigObj.w3, tx_details)

    def _get_transaction_receipt(
        self, tx_hash: str, timeout: int
    ) -> TransactionReceipt:
        """
        Gets the transaction receipt for a given transaction hash.

        Parameters
        ----------
        tx_hash: str
            The transaction hash.
        timeout: int
            The timeout for the transaction receipt.

        Returns
        -------
        TransactionReceipt
            The transaction receipt.
        """
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

    def _get_transaction_receipt_with_timeout(
        self, tx_hash: str, timeout: int, poll_latency: int = 0.1
    ) -> TransactionReceipt:
        """
        Gets the transaction receipt for a given transaction hash.

        Parameters
        ----------
        tx_hash: str
            The transaction hash.
        timeout: int
            The timeout for the transaction receipt.
        poll_latency: int
            The poll latency for the transaction receipt.

        Returns
        -------
        TransactionReceipt
            The transaction receipt.
        """
        with Timeout(timeout) as _timeout:
            while True:
                tx_receipt = self.ConfigObj.w3.eth.getTransactionReceipt(tx_hash)
                if tx_receipt is not None:
                    return tx_receipt
                _timeout.sleep(poll_latency)

    def _get_transaction_receipt_with_timeout_and_retries(
        self,
        tx_hash: str,
        timeout: int,
        poll_latency: int = 0.1,
        retries: int = 5,
    ) -> TransactionReceipt:
        """
        Gets the transaction receipt for a given transaction hash.

        Parameters
        ----------
        tx_hash: str
            The transaction hash.
        timeout: int
            The timeout for the transaction receipt.
        poll_latency: int
            The poll latency for the transaction receipt.
        retries: int
            The number of retries for the transaction receipt.

        Returns
        -------
        TransactionReceipt
            The transaction receipt.
        """
        for _ in range(retries):
            try:
                return self._get_transaction_receipt_with_timeout(
                    tx_hash, timeout, poll_latency
                )
            except TimeExhausted:
                continue
        raise TimeExhausted(f"Transaction {tx_hash} not found after {retries} retries")

    def _get_gas_price(self) -> int:
        """
        Gets the gas price for the transaction.

        Returns
        -------
        int
            The gas price for the transaction.
        """
        return int(self.ConfigObj.w3.eth.gas_price * self.ConfigObj.DEFAULT_GAS_PRICE_OFFSET)

    def _get_gas(self, tx_function: ContractFunction, address: str) -> int:
        """
        Gets the gas for the transaction.

        Parameters
        ----------
        tx_function: ContractFunction
            The transaction function.

        Returns
        -------
        int
            The gas for the transaction.
        """
        return tx_function.estimateGas({"from": address}) + 10000

    @property
    def headers(self):
        return {"accept": "application/json", "content-type": "application/json"}

    @staticmethod
    def _get_payload(method: str, params: [] = None) -> Dict:
        if method in {"eth_estimateGas", "eth_sendPrivateTransaction"}:
            return {"id": 1, "jsonrpc": "2.0", "method": method, "params": params}
        else:
            return {"id": 1, "jsonrpc": "2.0", "method": method}

    def _get_max_priority_fee_per_gas_alchemy(self):
        return self._query_alchemy_api_gas_methods(method="eth_maxPriorityFeePerGas")

    def _get_eth_gas_price_alchemy(self):
        return self._query_alchemy_api_gas_methods(method="eth_gasPrice")

    def _get_gas_estimate_alchemy(self, params: []):
        return self._query_alchemy_api_gas_methods(
            method="eth_estimateGas", params=params
        )

    def _query_alchemy_api_gas_methods(self, method: str, params: list = None):
        response = requests.post(
            self.ConfigObj.ALCHEMY_API_URL,
            json=self._get_payload(method=method, params=params),
            headers=self.headers,
        )
        return int(json.loads(response.text)["result"].split("0x")[1], 16)

    def _get_tx_details(self):
        """
        Gets the transaction details for the transaction. (testing purposes)
        """
        return {
            "gasPrice": self.ConfigObj.DEFAULT_GAS_PRICE,
            "gas": self.ConfigObj.DEFAULT_GAS,
            "from": self.w3.toChecksumAddress(self.ConfigObj.FASTLANE_CONTRACT_ADDRESS),
            "nonce": self.w3.eth.get_transaction_count(
                self.w3.toChecksumAddress(self.ConfigObj.FASTLANE_CONTRACT_ADDRESS)
            ),
        }

    def submit_transaction_tenderly(
        self, route_struct: List[RouteStruct], src_address: str, src_amount: int
    ) -> Any:
        """
        Submits a transaction to the network.

        Parameters
        ----------
        tx_details: TxParams
            The transaction details.
        key: str
            The private key.

        Returns
        -------
        str
            The transaction hash.
        """
        # route_struct = [asdict(r) for r in route_struct]
        #for r in route_struct:
            #print(r)
        #     print("\n")
        # print(
        #     f"Submitting transaction to Tenderly...src_amount={src_amount} src_address={src_address}"
        #)
        address = self.ConfigObj.w3.toChecksumAddress(self.ConfigObj.BINANCE14_WALLET_ADDRESS)
        return self.arb_contract.functions.flashloanAndArb(
            route_struct, src_address, src_amount
        ).transact(
            {
                "gas": self.ConfigObj.DEFAULT_GAS,
                "from": address,
                "nonce": self._get_nonce(address),
                "gasPrice": 0,
            }
        )

    def _get_transaction_details(
        self,
        tx_function: ContractFunction,
        tx_params: TxParams,
        from_address: str,
        to_address: str,
    ) -> TxParams:
        """
        Gets the transaction details for the transaction.

        Parameters
        ----------
        tx_function: ContractFunction
            The transaction function.
        tx_params: TxParams
            The transaction parameters.

        Returns
        -------
        TxParams
            The transaction details.
        """
        return {
            "from": from_address,
            "to": to_address,
            "gas": self._get_gas(tx_function),
            "gasPrice": self._get_gas_price(),
            "value": tx_params.get("value", 0),
            "nonce": tx_params.get("nonce", None),
            "chainId": self.w3.eth.chain_id,
        }

    def _get_transaction_hash(self, tx_details: TxParams, key: str) -> str:
        """
        Gets the transaction hash for the transaction.

        Parameters
        ----------
        tx_details: TxParams
            The transaction details.
        key: str
            The private key.

        Returns
        -------
        str
            The transaction hash.
        """
        return self.ConfigObj.w3.eth.send_raw_transaction(
            to_hex(self.ConfigObj.w3.eth.account.sign_transaction(tx_details, key).rawTransaction)
        )

    def _get_nonce(self, address: str) -> int:
        """
        Gets the nonce for the transaction.

        Parameters
        ----------
        address: str
            The address.

        Returns
        -------
        int
            The nonce for the transaction.
        """
        return self.ConfigObj.w3.eth.getTransactionCount(address)

    _get_gas_estimate = _get_gas

    # build transaction
    def _build_transaction(
        self,
        tx_function: ContractFunction,
        tx_params: TxParams,
        from_address: str,
        to_address: str,
    ) -> TxParams:
        """
        Builds the transaction details for the transaction.

        Parameters
        ----------
        tx_function: ContractFunction
            The transaction function.
        tx_params: TxParams
            The transaction parameters.

        Returns
        -------
        TxParams
            The transaction details.
        """
        return {
            **self._get_transaction_details(
                tx_function, tx_params, from_address, to_address
            ),
            "data": tx_function.buildTransaction(tx_params)["data"],
        }

    # submit transaction
    def _submit_transaction(
        self,
        tx_function: ContractFunction,
        tx_params: TxParams,
        from_address: str,
        to_address: str,
        key: str,
    ) -> str:
        """
        Submits the transaction for the transaction.

        Parameters
        ----------
        tx_function: ContractFunction
            The transaction function.
        tx_params: TxParams
            The transaction parameters.
        from_address: str
            The from address.
        to_address: str
            The to address.
        key: str
            The private key.

        Returns
        -------
        str
            The transaction hash.
        """
        tx_details = self._build_transaction(
            tx_function, tx_params, from_address, to_address
        )
        return self._get_transaction_hash(tx_details, key)
