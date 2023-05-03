"""
Brownie-related transaction handlers for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__="01/May/2023"

# import itertools
# import random
# import time
from dataclasses import dataclass, asdict
from typing import List, Union, Any, Dict, Tuple, Optional

# import eth_abi
# import math
# import pandas as pd
import requests
from _decimal import Decimal
from alchemy import Network, Alchemy
from brownie.network.transaction import TransactionReceipt
from eth_utils import to_hex
from web3 import Web3
from web3._utils.threads import Timeout
from web3._utils.transactions import fill_nonce
from web3.contract import ContractFunction
from web3.exceptions import TimeExhausted
from web3.types import TxParams, TxReceipt

from fastlane_bot.data.abi import *  # TODO: PRECISE THE IMPORTS or from .. import abi
#from fastlane_bot.config import *  # TODO: PRECISE THE IMPORTS or from .. import config
from fastlane_bot.db.models import Token, Pool
#import fastlane_bot.config as c
# from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.config import Config
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
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
    ConfigObj: Config
    usd_gas_limit: float = 20 #TODO this needs to be dynamic
    gas_price_multiplier: float = 1.2


    def __post_init__(self):
        self.PRIVATE_KEY: str = self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL
        self.COINGECKO_URL: str = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true'
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
        return balance, self.w3.fromWei(balance, 'ether')

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
        return self.ConfigObj.w3.eth.getTransactionCount(self.ConfigObj.LOCAL_ACCOUNT.address)

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
        return data['ethereum']['usd']

    @property
    def deadline(self):
        return self.ConfigObj.w3.eth.getBlock('latest')['timestamp'] + self.ConfigObj.DEFAULT_BLOCKTIME_DEVIATION

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

    XS_WETH = "weth"
    XS_TRANSACTION = "transaction_built"
    XS_SIGNED = "transaction_signed"

    def submit_flashloan_arb_tx(self,
                                arb_data: List[Dict[str, Any]],
                                flashloan_token_address: str,
                                flashloan_amount: int or float,
                                verbose: bool = True,
                                result = None) -> str:
        """Submit a flashloan arbitrage transaction.

        Parameters
        ----------
        arb_data : List[Dict[str, Any]]
            The arbitrage data.
        flashloan_token_address : str
            The flashloan token address.
        flashloan_amount : int or float
            The flashloan amount.
        verbose : bool, optional
            Whether to print the transaction details, by default True
        result: XS_XXX or None
            What intermediate result to return (default: None)
        Returns
        -------
        str
            The transaction hash.
        """

        if not isinstance(flashloan_amount, int):
            flashloan_amount = int(flashloan_amount)

        if flashloan_token_address == self.ConfigObj.WETH_ADDRESS:
            flashloan_token_address = self.ConfigObj.ETH_ADDRESS

        if result == self.XS_WETH:
            return flashloan_token_address

        assert flashloan_token_address != arb_data[0]['targetToken'], \
            "The flashloan token address must be different from the first targetToken address in the arb data."

        if verbose:
            self._print_verbose(
                flashloan_amount, flashloan_token_address
            )
        # Set the gas price (gwei)
        gas_price = int(self.base_gas_price * self.gas_price_multiplier)

        # Prepare the transaction
        transaction = self.arb_contract.functions.flashloanAndArb(
            arb_data, flashloan_token_address, flashloan_amount
        ).buildTransaction(
            {
                'gas': self.gas_limit,
                'gasPrice': gas_price,
                'nonce': self.nonce,
            }
        )
        if result == self.XS_TRANSACTION:
            return transaction


        # Sign the transaction
        signed_txn = self.ConfigObj.w3.eth.account.signTransaction(
            transaction, self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL
        )
        if result == self.XS_SIGNED:
            return signed_txn
        # Send the transaction
        tx_hash = self.ConfigObj.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Transaction sent with hash: {tx_hash}")
        return tx_hash.hex()

    def _print_verbose(self, flashloan_amount: int or float, flashloan_token_address: str):
        """
        Print the transaction details.

        Parameters
        ----------
        flashloan_amount : int or float
            The flashloan amount.
        flashloan_token_address : str
            The flashloan token address.

        """
        print(f"flashloan amount: {flashloan_amount}")
        print(f"flashloan token address: {flashloan_token_address}")
        print(f"Gas price: {self.gas_price_gwei} gwei")
        print(f"Gas limit in USD ${self.usd_gas_limit} "
              f"Gas limit: {self.gas_limit} ")

        balance = self.ConfigObj.w3.eth.getBalance(self.ConfigObj.LOCAL_ACCOUNT.address)
        print(f"Balance of the sender's account: \n"
              f"{balance} Wei \n"
              f"{self.ConfigObj.w3.fromWei(balance, 'ether')} Ether")

@dataclass
class TxHelpers:
    """
    This class is used to organize web3/brownie transaction tools.
    """
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
    ConfigObj: Config
    # This is used for the Alchemy SDK
    network = Network.ETH_MAINNET


    def __post_init__(self):

        if self.ConfigObj.network.DEFAULT_PROVIDER != "tenderly":
            self.alchemy = Alchemy(api_key=self.ConfigObj.WEB3_ALCHEMY_PROJECT_ID, network=self.network, max_retries=3)
        self.arb_contract = self.ConfigObj.BANCOR_ARBITRAGE_CONTRACT
        self.web3 = self.ConfigObj.w3
        # Set the local account
        self.local_account = self.web3.eth.account.from_key(self.ConfigObj.ETH_PRIVATE_KEY_BE_CAREFUL)

        # Set the public address
        self.wallet_address = str(self.local_account.address)

        self.alchemy_api_url = self.ConfigObj.RPC_URL
        self.nonce = self.get_nonce()



    XS_API_CALLS = "various_api_calls"
    XS_TRANSACTION = "transaction_built"
    XS_GAS_IN_BNT = "gas_in_bnt"
    XS_MIN_PROFIT_CHECK = "min_profit_check"
    def validate_and_submit_transaction(
        self,
        route_struct: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        expected_profit: Decimal,
        result: str = None,
        verbose: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Validates and submits a transaction to the arb contract.

        Parameters
        ----------

        """

        if expected_profit < self.ConfigObj.DEFAULT_MIN_PROFIT:
            self.ConfigObj.logger.info(f"Transaction below minimum profit, reverting... /*_*\\")
            return None

        current_gas_price = int(
            self.get_eth_gas_price_alchemy() * self.ConfigObj.DEFAULT_GAS_PRICE_OFFSET
        )
        if verbose:
            self.ConfigObj.logger.info("Found a trade. Executing...")
            self.ConfigObj.logger.info(
                f"\nRoute to execute: routes: {route_struct}, sourceAmount: {src_amt}, source token: {src_address}, expected_profit {expected_profit} \n\n"
            )
        current_max_priority_gas = self.get_max_priority_fee_per_gas_alchemy()

        block_number = self.web3.eth.get_block("latest")["number"]

        nonce = self.get_nonce()

        if result == self.XS_API_CALLS:
            return current_gas_price, current_max_priority_gas, block_number, nonce

        arb_tx = self.build_transaction_with_gas(
            routes=route_struct,
            src_address=src_address,
            src_amt=src_amt,
            gas_price=current_gas_price,
            max_priority=current_max_priority_gas,
            nonce=nonce,
            test_fake_gas=True if result is not None else False
        )
        if result == self.XS_TRANSACTION:
            return arb_tx

        if arb_tx is None:
            return None
        gas_estimate = arb_tx["gas"]
        current_gas_price = arb_tx["maxFeePerGas"] + arb_tx["maxPriorityFeePerGas"]
        gas_estimate = int(gas_estimate + self.ConfigObj.DEFAULT_GAS_SAFETY_OFFSET)
        self.ConfigObj.logger.info(f"gas estimate = {gas_estimate}")
        current_gas_price = int(current_gas_price * self.ConfigObj.DEFAULT_GAS_PRICE_OFFSET)

        # Calculate the number of BNT paid in gas
        bnt, eth = self.get_bnt_tkn_liquidity()
        gas_in_src = self.estimate_gas_in_bnt(
            gas_price=current_gas_price,
            gas_estimate=gas_estimate,
            bnt=bnt,
            eth=eth,
        )

        adjusted_reward = Decimal(Decimal(expected_profit) * self.ConfigObj.DEFAULT_REWARD_PERCENT)

        if result == self.XS_MIN_PROFIT_CHECK:
            return adjusted_reward, gas_in_src

        if adjusted_reward > gas_in_src:
            self.ConfigObj.logger.info(
                f"Expected profit of {expected_profit} BNT vs cost of {gas_in_src} BNT in gas, executing"
            )

            # Submit the transaction
            tx_receipt = self.submit_private_transaction(
                arb_tx=arb_tx, block_number=block_number
            )
            return tx_receipt.hex or None
        else:
            self.ConfigObj.logger.info(
                f"Gas price too expensive! profit of {adjusted_reward} BNT vs gas cost of {gas_in_src} BNT. Abort, abort!"
            )
            return None

    def get_gas_price(self) -> int:
        """
        Returns the current gas price
        """
        return self.ConfigObj.w3.eth.gas_price

    def get_bnt_tkn_liquidity(self) -> Tuple[int, int]:
        """
        Return the current liquidity of the Bancor V3 BNT + ETH pool
        """
        pool = (
            self.ConfigObj.db.get_pool(Pool.exchange_name == self.ConfigObj.BANCOR_V3_NAME, Pool.tkn1_address == self.ConfigObj.ETH_ADDRESS)
        )
        return pool.tkn0_balance, pool.tkn1_balance

    @staticmethod
    def get_break_even_gas_price(bnt_profit: int, gas_estimate: int, bnt: int, eth):
        """
        get the maximum gas price which can be used without causing a fiscal loss

        bnt_profit: the minimum profit required for the transaction to be profitable
        gas_estimate: the estimated gas cost of the transaction
        bnt: the current BNT liquidity in the Bancor V3 BNT + ETH pool
        eth: the current ETH liquidity in the Bancor V3 BNT + ETH pool

        returns: the maximum gas price which can be used without causing a fiscal loss
        """
        profit_wei = int(bnt_profit * 10**18)
        return profit_wei * eth // (gas_estimate * bnt)

    @staticmethod
    def estimate_gas_in_bnt(
        gas_price: int, gas_estimate: int, bnt: int, eth: int
    ) -> Decimal:
        """
        Converts the expected cost of the transaction into BNT.
        This is for comparing to the minimum profit required for the transaction to ensure that the gas cost isn't
        greater than the profit.

        gas_price: the gas price of the transaction
        gas_estimate: the estimated gas cost of the transaction
        bnt: the current BNT liquidity in the Bancor V3 BNT + ETH pool
        eth: the current ETH liquidity in the Bancor V3 BNT + ETH pool

        returns: the expected cost of the transaction in BNT
        """
        eth_cost = gas_price * gas_estimate
        return Decimal(eth_cost * bnt) / (eth * 10**18)

    @staticmethod
    def estimate_gas_in_src(
        gas_price: int, gas_estimate: int, src: int, eth: int
    ) -> Decimal:
        eth_cost = gas_price * gas_estimate
        return Decimal(eth_cost * src / eth)

    def get_gas_estimate(self, transaction: TxReceipt) -> int:
        """
        Returns the estimated gas cost of the transaction

        transaction: the transaction to be submitted to the blockchain

        returns: the estimated gas cost of the transaction
        """
        return self.web3.eth.estimate_gas(transaction=transaction)

    def build_transaction_tenderly(
        self,
        routes: List[Dict[str, Any]],
        src_amt: int,
        nonce: int,
    ):
        self.ConfigObj.logger.info(f"Attempting to submit trade on Tenderly")
        return self.web3.eth.wait_for_transaction_receipt(
            self.arb_contract.functions.execute(routes, src_amt).transact(
                {
                    "maxFeePerGas": 0,
                    "gas": self.ConfigObj.DEFAULT_GAS,
                    "from": self.wallet_address,
                    "nonce": nonce,
                }
            )
        )

    def build_transaction_with_gas(
        self,
        routes: List[Dict[str, Any]],
        src_amt: int,
        src_address: str,
        gas_price: int,
        max_priority: int,
        nonce: int,
        test_fake_gas: bool = False
    ):
        """
        Builds the transaction to be submitted to the blockchain.

        routes: the routes to be used in the transaction
        src_amt: the amount of the source token to be sent to the transaction
        gas_price: the gas price to be used in the transaction

        returns: the transaction to be submitted to the blockchain
        """
        try:
            transaction = self.arb_contract.functions.flashloanAndArb(
                routes, src_address, src_amt
            ).build_transaction(
                self.build_tx(
                    gas_price=gas_price, max_priority_fee=max_priority, nonce=nonce
                )
            )
        except ValueError as e:
            print(f'ValueError when building transaction: {e}')
            message = str(e).split("baseFee: ")
            split_fee = message[1].split(" (supplied gas ")
            baseFee = int(int(split_fee[0]) * self.ConfigObj.DEFAULT_GAS_PRICE_OFFSET)
            transaction = self.arb_contract.functions.execute(
                routes, src_amt
            ).build_transaction(
                self.build_tx(
                    gas_price=baseFee, max_priority_fee=max_priority, nonce=nonce
                )
            )
        if test_fake_gas:
            transaction["gas"] = self.ConfigObj.DEFAULT_GAS
            return transaction

        try:
            estimated_gas = (
                self.web3.eth.estimate_gas(transaction=transaction)
                + self.ConfigObj.DEFAULT_GAS_SAFETY_OFFSET
            )
        except Exception as e:
            self.ConfigObj.logger.info(
                f"Failed to estimate gas due to exception {e}, scrapping transaction :(."
            )
            return None
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
        max_priority_fee: int = None,
    ) -> Dict[str, Any]:
        """
        Builds the transaction to be submitted to the blockchain.

        maxFeePerGas: the maximum gas price to be paid for the transaction
        maxPriorityFeePerGas: the maximum miner tip to be given for the transaction

        returns: the transaction to be submitted to the blockchain
        """
        return {
            "type": "0x2",
            "maxFeePerGas": gas_price,
            "maxPriorityFeePerGas": max_priority_fee,
            "from": self.wallet_address,
            "nonce": nonce,
        }

    def submit_transaction(self, arb_tx: str) -> Any:
        """
        Submits the transaction to the blockchain.

        arb_tx: the transaction to be submitted to the blockchain

        returns: the transaction hash of the submitted transaction
        """
        self.ConfigObj.logger.info(f"Attempting to submit tx {arb_tx}")
        signed_arb_tx = self.sign_transaction(arb_tx)
        self.ConfigObj.logger.info(f"Attempting to submit tx {signed_arb_tx}")
        tx = self.web3.eth.send_raw_transaction(signed_arb_tx.rawTransaction)
        tx_hash = self.web3.toHex(tx)
        self.transactions_submitted.append(tx_hash)
        try:
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx)
            return tx_receipt
        except TimeExhausted as e:
            self.ConfigObj.logger.info(f"Transaction is stuck in mempool, exception: {e}")
            return None

    def submit_private_transaction(self, arb_tx, block_number: int) -> Any:
        """
        Submits the transaction privately through Alchemy -> Flashbots RPC to mitigate frontrunning.

        :param arb_tx: the transaction to be submitted to the blockchain
        :param block_number: the current block number

        returns: The transaction receipt, or None if the transaction failed
        """
        self.ConfigObj.logger.info(f"Attempting to submit private tx {arb_tx}")
        signed_arb_tx = self.sign_transaction(arb_tx).rawTransaction
        signed_tx_string = signed_arb_tx.hex()

        max_block_number = hex(block_number + 10)

        params = [
            {
                "tx": signed_tx_string,
                "maxBlockNumber": max_block_number,
                "preferences": {"fast": True},
            }
        ]
        response = self.alchemy.core.provider.make_request(
            method="eth_sendPrivateTransaction",
            params=params,
            method_name="eth_sendPrivateTransaction",
            headers=self._get_headers,
        )
        self.ConfigObj.logger.info(f"Submitted to Flashbots RPC, response: {response}")
        if response != 400:
            tx_hash = response.get("result")
            try:
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                return tx_receipt
            except TimeExhausted as e:
                self.ConfigObj.logger.info(f"Transaction is stuck in mempool, exception: {e}")
                return None
        else:
            self.ConfigObj.logger.info(f"Failed to submit transaction to Flashbots RPC")
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

    # def get_gas_estimate_alchemy(self, params: []):
    #     """
    #     :param params: The already-built TX, with the estimated gas price included
    #     """
    #     return self._query_alchemy_api_gas_methods(
    #         method="eth_estimateGas", params=params
    #     )
