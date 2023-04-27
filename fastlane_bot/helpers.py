"""
This module contains the helper classes for the FastLaneArbBot.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import copy
import glob
import itertools
import json
import os
import random
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from decimal import *
from functools import reduce
from typing import List, Any, Dict, Tuple, Union

import web3.exceptions

from fastlane_bot.data.token_lookup import (
    get_token_decimals_from_address,
    get_token_symbol_from_address,
    check_if_tkn_in_table_address,
    check_if_tkn_in_table_symbol,
    get_token_decimals_from_symbol,
    get_token_address_from_symbol,
    liquid_tkn_addresses_bancor_3,
)
import brownie
import numpy as np
import pandas as pd
import requests
from joblib import parallel_backend, Parallel, delayed
from tabulate import tabulate
from web3.exceptions import TimeExhausted
from alchemy import Alchemy, Network
from fastlane_bot.exceptions import ResultLoggingException
from fastlane_bot.networks import *
from fastlane_bot.pools import LiquidityPool, UniswapV3LiquidityPool, CarbonV1Order
from fastlane_bot.routes import (
    Route,
    ConstantProductRoute,
    ConstantFunctionRoute,
    OrderBookDexRoute,
)
from fastlane_bot.token import ERC20Token
from fastlane_bot.utils import (
    format_amt,
    convert_decimals_to_wei_format,
    convert_weth_to_eth,
    EncodedOrder,
)

logger = ec.DEFAULT_LOGGER


@dataclass
class BaseHelper:
    """
    This class is the main user interface for the FastLaneArbBot. It is responsible for collecting data from the
    Ethereum blockchain, and then finding arbitrage opportunities between the supported exchanges.
    """

    wallet_address: str = None
    filetype: str = field(default=ec.DEFAULT_FILETYPE)
    base_path: str = field(default=ec.BASE_PATH)
    search_results: List[Route] = field(default_factory=list)
    web3: Any = field(init=False)
    bancor_network_info: Any = field(init=False)
    unique_pools: List[LiquidityPool] = field(default_factory=list)
    _best_route_report: pd.DataFrame or None = field(init=False, default=None)

    @property
    def block_number(self) -> int:
        """
        Returns the current block number
        """
        return self.web3.eth.block_number

    def create_route_report(self, idx: int = 0) -> pd.DataFrame or None:
        """
        Creates a report of the route at index `idx` in the list of routes sorted by profit

        :param idx: The index of the route to report on

        :return: A pandas dataframe of the route report
        """

        # Sort the list of routes by profit
        self.search_results.sort(reverse=True, key=lambda x: x.profit)

        # Get the route at index `idx`
        best_route = self.search_results[idx]

        # Get the current block number
        block_number = best_route.block_number

        # Get the trade path amounts
        amts = best_route.trade_path_amts

        # Create a list of tuples of the trade path amounts
        amts = [(amts[i], amts[i + 1]) for i in range(len(amts) - 1)]

        # Create a list of dictionaries of the trade path amounts
        args = [
            {"idx": i, "amt_in": amts[i][0], "amt_out": amts[i][1]}
            for i in range(len(amts))
        ]

        # Create a list of pandas dataframes of the trade path amounts
        data_frames = [
            best_route.trade_path[i].to_pandas(**args[i])
            for i in range(len(best_route.trade_path))
        ]

        # Merge the pandas dataframes into one dataframe
        route_report = reduce(
            lambda x, y: pd.merge(x, y, left_index=True, right_index=True), data_frames
        )

        # Add the profit and block number to the dataframe
        route_report["profit"] = best_route.profit

        # Add the block number to the dataframe
        route_report["block_number"] = block_number

        # Set the best route report if it is the first route idx
        if idx == 0:
            self._best_route_report = route_report

        # Return the best route report
        return route_report

    @property
    def cached_trade_routes(self) -> pd.DataFrame or None:
        """
        Gets the trade routes from the collection path
        """
        collections_path = os.path.normpath(f"{ec.COLLECTION_PATH}/*.{self.filetype}")
        logger.debug(f"Looking for cached trade routes in {collections_path}")
        filenames = list(glob.glob(collections_path))
        return pd.concat([pd.read_csv(f) for f in filenames]) if filenames else None

    @property
    def ts(self) -> Tuple[datetime, str]:
        real_ts = datetime.now()
        return real_ts, (
            str(real_ts)
            .replace(" ", "_", 10)
            .replace(":", "_", 10)
            .replace(".", "_", 10)
        )


@dataclass
class CacheHelpers(BaseHelper):
    """
    This class is used to cache the trade routes.
    """

    def archive_trade_routes(self):
        """
        Archives trade routes that have been read
        """
        readpath = os.path.normpath(f"{ec.COLLECTION_PATH}/*.{self.filetype}")
        files = glob.glob(readpath)
        [shutil.move(file, ec.ARCHIVE_PATH) for file in files]

    def trade_to_pandas(
        self,
        tx_hash,
        transaction_success: bool,
        block_number: int,
        flash_loan_amt: int,
        profit: int,
        routes: Dict[str, Any],
    ):
        """
        Exports values for inspection...

        :param tx_hash: The transaction hash
        :param transaction_success: Whether the transaction was successful
        :param block_number: The block number
        :param flash_loan_amt: The flash loan amount
        :param routes: The routes

        :return: None
        """
        dtts, ts = self.ts
        tx_path = f"{ec.DATA_PATH}/transactions"
        results_path = os.path.normpath(
            f"{tx_path}/{block_number}_{ts}.{self.filetype}"
        )
        trades = {
            "tx": tx_hash,
            "success": transaction_success,
            "block": block_number,
            "flash_loan_amt": flash_loan_amt,
            "profit": profit,
        }
        for i in range(len(routes)):
            route = routes[i]
            route = {f"{k}_{i}": v for k, v, in route.items()}
            trades = {**trades, **route}

        # Write to file
        df = pd.DataFrame(trades, index=[0])
        df["timestamp"] = [dtts for _ in range(len(df))]
        df.to_csv(results_path)


@dataclass
class TransactionHelpers(BaseHelper):
    """
    This class is used to organize web3/brownie transaction tools.
    """

    alchemy_api_url = ec.ALCHEMY_API_URL
    network_name: str = None
    arb_contract: Contract = None
    nonce: int = 0
    transactions_submitted = []
    transaction_routes_submitted = []
    network = Network.ETH_MAINNET
    alchemy = Alchemy(
        api_key=ec.WEB3_ALCHEMY_PROJECT_ID,
        network=network,
        max_retries=ec.DEFAULT_NUM_RETRIES,
    )

    def get_gas_price(self) -> int:
        """
        Returns the current gas price
        """
        return self.web3.eth.gas_price

    def get_bnt_eth_liquidity(self) -> tuple:
        """
        Return the current liquidity of the Bancor V3 BNT + ETH pool
        """
        return self.bancor_network_info.tradingLiquidity(ec.ETH_ADDRESS)

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
        logger.info(f"Attempting to submit trade on Tenderly")
        return self.web3.eth.wait_for_transaction_receipt(
            self.arb_contract.functions.execute(routes, src_amt).transact(
                {
                    "maxFeePerGas": 0,
                    "gas": ec.DEFAULT_GAS,
                    "from": self.wallet_address,
                    "nonce": nonce,
                }
            )
        )

    def build_transaction_with_gas(
        self,
        routes: List[Dict[str, Any]],
        src_amt: int,
        gas_price: int,
        max_priority: int,
        nonce: int,
        src_token=ec.BNT_ADDRESS,
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
                routes, src_token, src_amt
            ).build_transaction(
                self.build_tx(
                    gas_price=gas_price, max_priority_fee=max_priority, nonce=nonce
                )
            )
        except (ValueError, web3.exceptions.ContractLogicError) as e:
            if e.__class__.__name__ == "ValueError":
                message = str(e).split("baseFee: ")
                split_fee = message[1].split(" (supplied gas ")
                baseFee = int(int(split_fee[0]) * ec.DEFAULT_GAS_PRICE_OFFSET)
                transaction = self.arb_contract.functions.flashloanAndArb(
                    routes, src_token, src_amt
                ).build_transaction(
                    self.build_tx(
                        gas_price=baseFee, max_priority_fee=max_priority, nonce=nonce
                    )
                )
            else:
                logger.error(
                    f"Contract logic error - likely an invalid transaction: {e}"
                )
                return None

        try:
            estimated_gas = (
                self.web3.eth.estimate_gas(transaction=transaction)
                + ec.DEFAULT_GAS_SAFETY_OFFSET
            )
        except Exception as e:
            logger.info(
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
        logger.info(f"Attempting to submit tx {arb_tx}")
        signed_arb_tx = self.sign_transaction(arb_tx)
        logger.info(f"Attempting to submit tx {signed_arb_tx}")
        tx = self.web3.eth.send_raw_transaction(signed_arb_tx.rawTransaction)
        tx_hash = self.web3.toHex(tx)
        self.transactions_submitted.append(tx_hash)
        try:
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx)
            return tx_receipt
        except TimeExhausted as e:
            logger.info(f"Transaction is stuck in mempool, exception: {e}")
            return None

    def submit_private_transaction(self, arb_tx, block_number: int) -> Any:
        """
        Submits the transaction privately through Alchemy -> Flashbots RPC to mitigate frontrunning.

        :param arb_tx: the transaction to be submitted to the blockchain
        :param block_number: the current block number

        returns: The transaction receipt, or None if the transaction failed
        """
        logger.info(f"Attempting to submit private tx {arb_tx}")
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
        logger.info(f"Submitted to Flashbots RPC, response: {response}")
        if response != 400:
            tx_hash = response.get("result")
            try:
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                return tx_receipt
            except TimeExhausted as e:
                logger.info(f"Transaction is stuck in mempool, exception: {e}")
                return None
        else:
            logger.info(f"Failed to submit transaction to Flashbots RPC")
            return None

    def sign_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Signs the transaction.

        transaction: the transaction to be signed

        returns: the signed transaction
        """
        return self.web3.eth.account.sign_transaction(transaction, ec.ETH_PRIVATE_KEY)

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

    def get_gas_estimate_alchemy(self, params: []):
        """
        :param params: The already-built TX, with the estimated gas price included
        """
        return self._query_alchemy_api_gas_methods(
            method="eth_estimateGas", params=params
        )


class HexbytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Hexbytes):
            return obj.hex()
        return super().default(obj)


class Hexbytes:
    def __init__(self, value):
        self.value = value

    def hex(self):
        return self.value.hex()


@dataclass
class SearchHelpers(BaseHelper):
    """
    This class is used to organize web3/brownie search tools.
    """

    backend: str = ec.DEFAULT_BACKEND
    n_jobs: int = ec.DEFAULT_N_JOBS
    trade_paths: List[List[str]] = field(default_factory=list)
    candidate_routes: List[Route] = field(default_factory=list)
    unique_pools_raw: List[Dict[str, Any]] = field(default_factory=list)
    number_of_retries: int = ec.DEFAULT_NUM_RETRIES

    def search_candidate_routes(self, initial_search: bool = True):
        """
        Searches for profitable arbitrage routes.
        """
        logger.info(
            f"Searching for profitable arbitrage routes... initial_search={initial_search}"
        )
        if initial_search:
            arb_ops = self.create_routes()
            self.set_candidate_routes(arb_ops)

        with parallel_backend(backend=self.backend, n_jobs=self.n_jobs):
            results = Parallel(n_jobs=self.n_jobs)(
                delayed(op.simulate)(**{"trade_path": op.trade_path})
                for op in self.candidate_routes
            )
        results = [result for result in results if result is not None]
        self.search_results = results
        self.log_results()

    def log_results(self):
        """
        Logs the results of the search
        """
        if not self.search_results:
            logger.info("No results found")
            return
        if len(self.search_results) == 0:
            logger.info("No results found")
            return
        block_number = self.block_number
        real_ts, ts = self.ts
        filetype = self.filetype
        lst = [self.create_route_report(idx) for idx in range(len(self.search_results))]
        results_path = os.path.normpath(
            f"{ec.COLLECTION_PATH}/{str(block_number)}_{ts}.{filetype}"
        )
        output = pd.concat(lst)
        output["ts"] = [real_ts for _ in range(len(output))]
        self.handle_log_for_filetype(filetype, output, results_path, ts)

    @staticmethod
    def handle_log_for_filetype(
        filetype: str, output: pd.DataFrame, results_path: str, ts: str
    ) -> None:
        """
        Handles the logging for the filetype provided

        :param filetype: The filetype
        :param output: The output dataframe
        :param results_path: The results path
        :param ts: The timestamp

        :return: None
        """
        if len(output) == 0:
            return None
        if filetype == "csv":
            output.to_csv(results_path)
            logger.debug(f"writing results to: {results_path}")
        elif filetype == "parquet":
            try:
                output.to_parquet(results_path, compression="gzip")
                logger.debug(f"writing results to: {results_path}")
            except Exception as e:
                new_path = results_path.replace(".parquet", ".csv")
                logger.warning(f"{e}")
                try:
                    output.to_csv(new_path)
                    logger.debug(f"writing results to: {new_path}")
                except Exception as e:
                    logger.error(f"{e}")
                    raise ResultLoggingException(ts=ts, path=new_path) from e
        else:
            raise TypeError("filetype must be one of ['csv', 'parquet']")

    @staticmethod
    def extract_trade_path_key(path: str, index: int = 0) -> str:
        """
        This function returns a list of valid paths for the token pairs / exchanges
        """
        if path and path[0] and len(path[0]) > index:
            return f"{path[0][index]['pair']}*{path[0][index]['exchange']}*{path[0][index]['fee']}"
        return None

    def get_unique_pools(self):
        """
        This function returns a list of valid paths for the token pairs / exchanges
        """
        unique_pools = self.unique_pools_raw
        pools = [
            LiquidityPool(
                tkn0=_id[0],
                tkn1=_id[1],
                exchange=_id[2],
                fee=_id[3],
                pair=_id[4],
                pair_reverse=_id[5],
                id=idx,
                connection=self.web3,
            )
            for idx, _id in enumerate(unique_pools)
        ]
        crosscheck = []
        unique_pools = []
        for pool in pools:
            key1 = f"{pool.pair}*{pool.exchange}"
            key2 = f"{pool.pair_reverse}*{pool.exchange}"
            if key1 not in crosscheck and key2 not in crosscheck:
                crosscheck.extend((key1, key2))
                unique_pools.append(pool)

        unique_pools = [p for p in unique_pools if p is not None]
        self.unique_pools = unique_pools

    def update_pool_liquidity(self):
        """
        This function returns a list of valid paths for the token pairs / exchanges
        """
        pools = self.unique_pools
        non_v3_pools = [p for p in pools if p.exchange != ec.BANCOR_V3_NAME]
        v3_pools = [p for p in pools if p.exchange == ec.BANCOR_V3_NAME]
        non_v3_pools = self.setup_pools_multiprocessing(non_v3_pools)

        return self.setup_pools_multicall(non_v3_pools, v3_pools)

    def setup_pools_multicall(
        self, other_pools: List[LiquidityPool], v3_pools: List[LiquidityPool]
    ) -> List[LiquidityPool]:
        """
        Setup Bancor V3 pools with multicall to improve efficiency

        :param other_pools: List of pools (excluding Bancor V3 pools)
        :param v3_pools: List of Bancor V3 pools

        :return: List of pools (including Bancor V3 pools) combined
        """
        v3_pools_init = []

        if v3_pools:
            # Initialize the Bancor Network Info contract only 1x
            contract = self.bancor_network_info

            # Then with multicall, update the liquidity for all pools in 1 call
            with brownie.multicall(address=ec.MULTICALL_CONTRACT_ADDRESS):
                v3_pools_init.extend(
                    pool.update_liquidity(contract, pool.tkn0, pool.tkn1)
                    for pool in v3_pools
                )

        return other_pools + v3_pools_init

    def setup_pools_multiprocessing(
        self, non_bancor3_pools: List[LiquidityPool] = None
    ):
        """
        Setup the pools in parallel using the specified backend for all pools except Bancor V3

        param: backend: the backend to use
        param: n_jobs: the number of jobs to use
        param: pools: the list of pools which will be setup (except Bancor V3) via the .setup() method

        Returns:
        A list of pools with the setup() method called (i.e. liquidity and reserves updated)
        """
        for _ in range(self.number_of_retries):
            try:
                with parallel_backend(n_jobs=self.n_jobs, backend=self.backend):
                    pools = Parallel(n_jobs=self.n_jobs)(
                        delayed(p.update_liquidity)() for p in non_bancor3_pools
                    )
            except Exception as e:
                logger.warning(f"Failed to setup pools. Retrying in 3 seconds...{e}")
                time.sleep(3)

        return pools

    @staticmethod
    def map_pools_to_paths(
        trade_paths: List[List], pools: List[LiquidityPool]
    ) -> List[List[LiquidityPool]]:
        """
        This function returns a list of valid paths for the token pairs / exchanges

        param: trade_paths: the list of trade paths
        param: pools: the list of pools

        Returns:
        A list of valid trade paths with the pool objects
        """
        trade_paths_new = []
        for path in trade_paths:
            p1, p2, p3 = None, None, None

            for pool in pools:
                if (
                    path[0][4] in [pool.pair, pool.pair_reverse]
                    and path[0][2] == pool.exchange
                ):
                    p1 = copy.deepcopy(pool)
                if (
                    path[1][4] in [pool.pair, pool.pair_reverse]
                    and path[1][2] == pool.exchange
                ):
                    p2 = copy.deepcopy(pool)
                if (
                    path[2][4] in [pool.pair, pool.pair_reverse]
                    and path[2][2] == pool.exchange
                ):
                    p3 = copy.deepcopy(pool)
            if p1 and p2 and p3:
                if p1.tkn1 != p2.tkn0 or p2.tkn1 != p3.tkn0:
                    p2.reverse_tokens()

                trade_paths_new.append([p1, p2, p3])

        return trade_paths_new

    def match_routes_carbon(
        self, carbon_pools: [CarbonV1Order], other_pools: [LiquidityPool]
    ):
        """
        This function builds triangular routes of Constant Product pool -> Carbon Order -> Constant Product pool.
        :param carbon_pools: a list of carbon orders
        :param other_pools: a list of constant product liquidity pools
        """
        triangular_carbon_routes = []

        for idx, pool in enumerate(carbon_pools):
            if pool.tkn0.symbol == ec.BNT_SYMBOL or pool.tkn1.symbol == ec.BNT_SYMBOL:
                # Skip routes with BNT for triangular calculations
                continue
            first_tkn_match = None
            pool1 = None
            pool2 = pool
            pool3 = None
            for _pool in other_pools:
                if (
                    _pool.tkn0.symbol == pool2.tkn0.symbol
                    or _pool.tkn1.symbol == pool2.tkn0.symbol
                ):
                    pool1 = _pool
                    first_tkn_match = pool2.tkn0.symbol
                    break
            if pool1:
                for __pool in other_pools:
                    if (
                        __pool.tkn0.symbol == pool2.tkn1.symbol
                        and __pool.tkn1.symbol != first_tkn_match
                    ) or (
                        __pool.tkn1.symbol == pool2.tkn1.symbol
                        and __pool.tkn1.symbol != first_tkn_match
                    ):
                        pool3 = __pool
                        break
            else:
                continue
            if pool3:
                route = OrderBookDexRoute(id=idx, trade_path=[pool1, pool2, pool3])
                route_copy = route.copy_route()

                if route_copy.p3.tkn0.symbol == ec.BNT_SYMBOL:
                    t0, t1 = route_copy.p3.tkn0, route_copy.p3.tkn1
                    route_copy.p3.tkn0 = t1
                    route_copy.p3.tkn1 = t0
                triangular_carbon_routes.append(route_copy)

        return triangular_carbon_routes

    def generate_carbon_pair_dict(
        self, pairs: List[Tuple[str, str]], carbon_orders: [CarbonV1Order]
    ) -> dict:
        """
        This function creates a dictionary of Carbon token pairs with their initialized Carbon Orders, divided into two arrays that contain directional orders. IE an array of TKN 0 -> TKN 1 and an array of TKN1 -> TKN 0.
        :param pairs: a list of initialized Carbon pairs.
        :param carbon_orders: a list of initialized Carbon Order objects.
        """
        forwards = "forwards"
        inverted = "inverted"
        pair_dict = {}

        # Build a dict of all pairs
        for pair in pairs:
            pair_combined = pair[0] + "_" + pair[1]
            pair_dict[pair_combined] = {forwards: [], inverted: []}

        pair_keys = pair_dict.keys()
        # validate that all pairs have been added to the dict
        assert len(pair_keys) == len(pairs)

        for order in carbon_orders:
            tkn0_tkn1 = order.tkn0.address + "_" + order.tkn1.address
            tkn1_tkn0 = order.tkn1.address + "_" + order.tkn0.address
            key = ""
            direction = ""
            if tkn0_tkn1 in pair_keys:
                direction = forwards
                key = tkn0_tkn1
            elif tkn1_tkn0 in pair_keys:
                direction = inverted
                key = tkn1_tkn0
            else:
                raise Exception(
                    "Key not found in token pairs. Something went wrong in generate_carbon_pair_dict function."
                )
            pair_dict[key][direction] += [order]

        # sort carbon order arrays by marginal price - the second one is inverted so that they use the same token as the numerator.
        for key in pair_keys:
            pair_dict[key][forwards].sort(key=lambda x: x.marg_price, reverse=True)
            pair_dict[key][forwards].sort(
                key=lambda x: x.marg_price_inverted, reverse=True
            )

        return pair_dict

    def carbon_pair_route_generator(self, orders_forwards: [], orders_inverted: []):
        if len(orders_forwards) == 0 or len(orders_inverted == 0):
            return None

        routes = []

        for order in orders_forwards:
            pass

    def get_carbon_pairs_with_one_non_flash_tkn(self, pairs: List[Tuple[str, str]]):
        """
        Returns token pairs that have one token that can be flash loaned from Bancor V3, and one token that cannot.
        """
        pairs_with_one_flash_token = []
        non_bancor_v3_tokens = []
        for pair in pairs:
            tkn0 = pair[0]
            tkn1 = pair[1]

            if tkn0 and tkn1 in liquid_tkn_addresses_bancor_3:
                continue
            elif tkn0 in liquid_tkn_addresses_bancor_3:
                pairs_with_one_flash_token.append(pair)
                non_bancor_v3_tokens.append(tkn1)

            elif tkn1 in liquid_tkn_addresses_bancor_3:
                pairs_with_one_flash_token.append(pair)
                non_bancor_v3_tokens.append(tkn0)
            else:
                # Neither token in Bancor V3
                continue
        print(pairs_with_one_flash_token)
        return pairs_with_one_flash_token, non_bancor_v3_tokens

    def create_routes_carbon(self):
        """
        Generates arbitrage trade routes, focusing on Carbon Orders.
        """
        # returns a list of all Carbon Orders that are active and have liquidity.
        all_pairs = self.get_carbon_pairs()

        (
            pairs_with_one_bancor_v3_token,
            non_bancor_v3_tokens,
        ) = self.get_carbon_pairs_with_one_non_flash_tkn(pairs=all_pairs)

        carbon_orders = self.get_all_carbon_strategies(carbon_pairs=all_pairs)

        carbon_pair_dict = self.generate_carbon_pair_dict(
            pairs=all_pairs, carbon_orders=carbon_orders
        )

        self.unique_pools = self.get_bancor_v3_pools(
            tokens=liquid_tkn_addresses_bancor_3
        )
        bancor_v3_pools = self.update_pool_liquidity()

        routes = self.match_routes_carbon(
            carbon_pools=carbon_orders, other_pools=bancor_v3_pools
        )
        routes = [route for route in routes if route is not None]

        with parallel_backend(backend=self.backend, n_jobs=self.n_jobs):
            results = Parallel(n_jobs=self.n_jobs)(
                delayed(op.simulate)(**{"trade_path": op.trade_path}) for op in routes
            )

        results = [result for result in results if result is not None]

        return results

    def create_routes(self) -> List[Route]:
        """
        This function returns a list of valid paths for the token pairs / exchanges
        """
        self.update_pool_liquidity()
        trade_paths_new = self.map_pools_to_paths(self.trade_paths, self.unique_pools)
        routes = [
            self.build_route_from_path(idx, i[0], i[1], i[2])
            for idx, i in enumerate(trade_paths_new)
        ]
        routes = [route for route in routes if route is not None]
        route_ids = list({r.id for r in routes})
        return [r for r in routes if r.id in route_ids]

    def build_candidate_routes_carbon(self):
        pass

    def build_candidate_routes(
        self,
        exchanges: List[str] = ec.SUPPORTED_EXCHANGE_VERSIONS,
        tokens: List[str] = ec.SUPPORTED_TOKENS,
    ):
        """
        Builds the candidate routes for the bot to search through

        param: exchanges: a list of exchanges to search through
        param: tokens: a list of tokens to search through

        Returns: A list of candidate routes and a list of external pools
        """

        if exchanges is None:
            self.candidate_routes = []
            return
        if tokens is None:
            self.candidate_routes = []
            return

        df = ec.DB
        if ec.BANCOR_V2_NAME not in exchanges:
            exchanges.append(ec.BANCOR_V2_NAME)
        df = df[df["exchange"].isin(exchanges)]
        tokens = [token.upper() for token in tokens]
        tokens.extend(("BNT", "ETH", "WETH"))
        tokens = list(set(tokens))
        df = df[(df["symbol0"].isin(tokens)) & (df["symbol1"].isin(tokens))]
        self.find_trade_paths(df, exchanges, tokens)
        self.get_unique_pools()
        arb_ops = self.create_routes()
        self.set_candidate_routes(arb_ops)

    def set_candidate_routes(self, arb_ops: List[Route]) -> None:
        """
        Sets the candidate routes for the bot to search through
        """
        routes = [
            i
            for i in arb_ops
            if type(i)
            in [ConstantProductRoute, ConstantFunctionRoute, OrderBookDexRoute]
        ]
        candidate_routes = [
            r
            for r in routes
            if r.p1 is not None or r.p2 is not None or r.p3 is not None
        ]
        self.candidate_routes = [
            r
            for r in candidate_routes
            if r.p1 is not None or r.p2 is not None or r.p3 is not None
        ]

    @staticmethod
    def build_route_from_path(
        idx: int, p1: LiquidityPool, p2: LiquidityPool, p3: LiquidityPool
    ) -> Union[Route, None]:
        """
        Initializes and fetches the liquidity for each pool in a route. This function is intended to run in a joblib loop asynchronously.

        param: p1: the first liquidity pool in the route
        param: p2: the second liquidity pool in the route
        param: p3: the third liquidity pool in the route

        Returns:
        An initialized route of 3 liquidity pools with their liquidity, sorted to ensure BNT is the first and last token
        """

        if p1 is None or p2 is None or p3 is None:
            return None

        # Initialize the Route object
        route = Route(id=idx, trade_path=[p1, p2, p3])

        # Reverse the tokens if necessary
        route.assert_logical_path()
        if route.p2.is_reversed and isinstance(route, ConstantFunctionRoute):
            return None

        # return the route
        return route

    def find_trade_paths(
        self,
        pdf: pd.DataFrame,
        exchanges: List[str] = ec.SUPPORTED_EXCHANGE_VERSIONS,
        tokens: List[str] = ec.SUPPORTED_TOKENS,
    ):
        """
        This function returns a list of valid paths for the token pairs / exchanges

        param: pdf: the dataframe containing the pairs

        Returns: A list of valid paths
        """

        if "BNT" not in tokens:
            tokens.append("BNT")
        if "ETH" not in tokens:
            tokens.append("ETH")
        if "WETH" not in tokens:
            tokens.append("WETH")

        df1 = pdf[
            (pdf["exchange"] == ec.BANCOR_BASE)
            & ((pdf["symbol0"] == "BNT") | (pdf["symbol1"] == "BNT"))
            & (pdf["symbol0"].isin(tokens))
            & (pdf["symbol1"].isin(tokens))
        ]
        p1_paths1 = [
            (s1, s2, exchange, fee, pair, pair_reverse)
            for s1, s2, exchange, fee, pair, pair_reverse in df1[
                ["symbol0", "symbol1", "exchange", "fee", "pair", "pair_reverse"]
            ].values
            if s1 == "BNT"
        ]
        p1_paths2 = [
            (s1, s2, exchange, fee, pair, pair_reverse)
            for s1, s2, exchange, fee, pair, pair_reverse in df1[
                ["symbol1", "symbol0", "exchange", "fee", "pair", "pair_reverse"]
            ].values
            if s1 == "BNT"
        ]
        p1_paths = p1_paths1 + p1_paths2
        p1_paths = list(set(p1_paths))

        df2 = pdf[
            (pdf["exchange"] != ec.BANCOR_BASE)
            & (pdf["exchange"].isin(exchanges))
            & ((pdf["symbol0"] != "BNT") & (pdf["symbol1"] != "BNT"))
            & (pdf["symbol0"].isin(tokens))
            & (pdf["symbol1"].isin(tokens))
        ]
        p2_paths1 = [
            tuple(convert_weth_to_eth(p))
            for p in df2[
                ["symbol0", "symbol1", "exchange", "fee", "pair", "pair_reverse"]
            ].values
            if p[0] != "BNT" and p[1] != "BNT"
        ]
        p2_paths2 = [
            tuple(convert_weth_to_eth(p))
            for p in df2[
                ["symbol1", "symbol0", "exchange", "fee", "pair", "pair_reverse"]
            ].values
            if p[0] != "BNT" and p[1] != "BNT"
        ]
        p2_paths = p2_paths1 + p2_paths2
        p2_paths = list(set(p2_paths))

        df3 = pdf[
            (pdf["exchange"] == ec.BANCOR_BASE)
            & ((pdf["symbol0"] == "BNT") | (pdf["symbol1"] == "BNT"))
            & (pdf["symbol0"].isin(tokens))
            & (pdf["symbol1"].isin(tokens))
        ]
        p3_paths1 = [
            (s1, s2, exchange, fee, pair, pair_reverse)
            for s1, s2, exchange, fee, pair, pair_reverse in df3[
                ["symbol0", "symbol1", "exchange", "fee", "pair", "pair_reverse"]
            ].values
            if s1 != "BNT"
        ]
        p3_paths2 = [
            (s1, s2, exchange, fee, pair, pair_reverse)
            for s1, s2, exchange, fee, pair, pair_reverse in df3[
                ["symbol1", "symbol0", "exchange", "fee", "pair", "pair_reverse"]
            ].values
            if s1 != "BNT"
        ]
        p3_paths = p3_paths1 + p3_paths2
        p3_paths = list(set(p3_paths))

        p1_tkns = [p[1] for p in p1_paths]
        p3_tkns = [p[0] for p in p3_paths]
        unique_combinations = list(itertools.product(p1_tkns, p3_tkns))
        p2_paths = [p for p in p2_paths if (p[0], p[1]) in unique_combinations]

        indexes = []
        for idx2, p2 in enumerate(p2_paths):
            if p2[0] in p1_tkns and p2[1] in p3_tkns:
                idx1 = [i for i, x in enumerate(p1_tkns) if x == p2[0]][0]
                idx3 = [i for i, x in enumerate(p3_tkns) if x == p2[1]][0]
                indexes.append((idx1, idx2, idx3))
            elif p2[1] in p1_tkns and p2[0] in p3_tkns:
                idx1 = [i for i, x in enumerate(p1_tkns) if x == p2[1]][0]
                idx3 = [i for i, x in enumerate(p3_tkns) if x == p2[0]][0]
                indexes.append((idx1, idx2, idx3))

        trade_paths = []
        unique_pools = []
        for idx1, idx2, idx3 in indexes:
            trade_paths.append((p1_paths[idx1], p2_paths[idx2], p3_paths[idx3]))
            unique_pools.extend((p1_paths[idx1], p2_paths[idx2], p3_paths[idx3]))
        self.trade_paths = trade_paths
        unique_pools = list(set(unique_pools))
        self.unique_pools_raw = unique_pools

    def get_pair_from_symbols(self, tkn0: str, tkn1: str) -> str:
        """
        Combines token symbols to form a pair string
        """
        assert type(tkn0) == str
        assert type(tkn1) == str

        return tkn0 + "_" + tkn1

    def get_pair_from_address(self, tkn0: str, tkn1: str) -> str:
        """
        Looks up token symbols from their address and combines token symbols to form a pair string
        :param tkn0: the token address of token 0
        :param tkn1: the token address of token 1
        """

        return (
            get_token_symbol_from_address(tkn0)
            + "_"
            + get_token_symbol_from_address(tkn1)
        )

    def get_pair(self, tkn0, tkn1):
        tkn0 = self.web3.toChecksumAddress(tkn0)
        tkn1 = self.web3.toChecksumAddress(tkn1)
        if not check_if_tkn_in_table_address(tkn0):
            logger.error(f"Error looking up token: {tkn0}")
            return None
        if not check_if_tkn_in_table_address(tkn1):
            logger.error(f"Error looking up token: {tkn1}")
            return None
        pair = self.get_pair_from_address(tkn0=tkn0, tkn1=tkn1)
        assert type(pair) == str
        return pair

    def get_erc20_from_address(self, token_address):
        """
        Returns and ERC20 object from a token address
        :param token_address: the address of the token
        """
        token_address = self.web3.toChecksumAddress(token_address)
        if not check_if_tkn_in_table_address(token_address):
            logger.error(f"Error looking up token: {token_address}")
            return None
        return ERC20Token(
            address=token_address,
            symbol=get_token_symbol_from_address(token_address),
            decimals=get_token_decimals_from_address(token_address),
        )

    def get_erc20_from_symbol(self, token_symbol):
        """
        Returns and ERC20 token object from a token symbol
        :param token_symbol: the symbol of the token, for example ETH, WBTC, BNT
        """
        if not check_if_tkn_in_table_symbol(token_symbol):
            logger.error(f"Error looking up token: {token_symbol}")
            return None
        return ERC20Token(
            address=get_token_address_from_symbol(token_symbol),
            symbol=token_symbol,
            decimals=get_token_decimals_from_symbol(token_symbol),
        )

    def get_bancor_v3_pools(self, tokens: [ERC20Token]):
        """
        Returns a list of initialized Bancor V3 liquidity pools
        :param tokens: the tokens for which to get liquidity pools
        """
        pools = [
            LiquidityPool(
                tkn0=self.get_erc20_from_address(ec.BNT_ADDRESS),
                tkn1=self.get_erc20_from_address(token),
                exchange=ec.BANCOR_V3_NAME,
                fee=Decimal("0.00"),
                pair=self.get_pair(ec.BNT_ADDRESS, token),
                pair_reverse=self.get_pair(token, ec.BNT_ADDRESS),
                id=idx,
                connection=self.web3,
                # address=ec.BANCOR_V3_NETWORK_INFO_ADDRESS
            )
            for idx, token in enumerate(tokens)
            if token != ec.BNT_SYMBOL
        ]
        pools = [pool for pool in pools if pool is not None]
        return pools

    def get_all_carbon_strategies(
        self, carbon_pairs: List[Tuple[str, str]]
    ) -> [CarbonV1Order]:
        """
        Gets every Carbon Strategy given a list of token pairs
        """

        with brownie.multicall(address=ec.MULTICALL_CONTRACT_ADDRESS):
            strats = [
                strategy
                for pair in carbon_pairs
                for strategy in self.get_strategies(pair)
            ]
            block_number = brownie.web3.eth.block_number

        return self.process_raw_carbon_strategies(
            strategies=strats, block_updated=block_number
        )

    @staticmethod
    def get_carbon_pairs() -> List[Tuple[str, str]]:
        """
        Returns a list of all Carbon token pairs

        Returns
        -------
        List[Tuple[str, str]]
            A list of all Carbon token pairs

        """
        return ec.CARBON_CONTROLLER_CONTRACT.caller.pairs()

    @staticmethod
    def get_carbon_strategy(
        strategy_id: int,
    ) -> Tuple[str, str, str, str, str, str, str]:
        """
        Returns a tuple of the strategy's data

        Parameters
        ----------
        strategy_id : int
            The id of the strategy

        Returns
        -------
        Tuple[str, str, str, str, str, str, str]
            A tuple of the strategy's data
        """
        return ec.CARBON_CONTROLLER_CONTRACT.caller.strategy(strategy_id)

    @staticmethod
    def get_strategies_count_by_pair(token0: str, token1: str) -> int:
        """
        Returns the number of strategies in the specified token pair

        Parameters
        ----------
        token0 : str
            The token address of the first token
        token1 : str
            The token address of the second token

        Returns
        -------
        int
            The number of strategies in the specified token pair
        """
        return ec.CARBON_CONTROLLER_CONTRACT.caller.strategiesByPairCount(
            token0, token1
        )

    @staticmethod
    def get_strategies_by_pair(
        token0: str, token1: str, start_idx: int, end_idx: int
    ) -> List[int]:
        """
        Returns a list of strategy ids for the specified pair, given a start and end index

        Parameters
        ----------
        token0 : str
            The token address of the first token
        token1 : str
            The token address of the second token
        start_idx : int
            The start index
        end_idx : int
            The end index

        Returns
        -------
        List[int]
            A list of strategy ids for the specified pair, given a start and end index
        """
        return ec.CARBON_CONTROLLER_CONTRACT.caller.strategiesByPair(
            token0, token1, start_idx, end_idx
        )

    def get_strategies(self, pair: Tuple[str, str]) -> List[int]:
        """
        Returns a list of strategy ids for the specified pair

        Parameters
        ----------
        pair : Tuple[str, str]
            The token pair

        Returns
        -------
        List[int]
            A list of strategy ids for the specified pair
        """
        num_strategies = self.get_strategies_count_by_pair(pair[0], pair[1])
        return self.get_strategies_by_pair(pair[0], pair[1], 0, num_strategies)

    def update_all_carbon_strategies(self):
        """
        Finds and updates all Carbon strategies
        """
        all_strategies = self.get_all_carbon_strategies()
        block = self.web3.eth.block_number
        return self.process_raw_carbon_strategies(
            strategies=all_strategies, block_updated=block
        )

    @staticmethod
    def chunker(seq: Any, size: int) -> Any:
        """
        Splits a list into chunks of a specified size

        Parameters
        ----------
        seq : Any
            The list to split
        size : int
            The size of each chunk

        Returns
        -------
        Any
            A generator of the chunks
        """
        return (seq[pos : pos + size] for pos in range(0, len(seq), size))

    def get_carbon_strategies_multicall(self, strategy_ids: List[int]) -> List[Any]:
        """
        Returns raw Carbon strategies of the specified ids.

        Parameters
        ----------
        strategy_ids : List[int]
            A list of strategy ids

        Returns
        -------
        List[Any]
            A list of raw Carbon strategies
        """
        strategies = []
        for group in self.chunker(strategy_ids, ec.CARBON_STRATEGY_CHUNK_SIZE):
            with brownie.multicall(address=ec.MULTICALL_CONTRACT_ADDRESS):
                strategies += [
                    self.get_carbon_strategy(strat_id[0]) for strat_id in group
                ]
        return strategies

    def process_raw_carbon_strategies(
        self, strategies: List[int], block_updated: int
    ) -> [CarbonV1Order]:
        """
        Takes a list of Carbon Strategies in the raw contract format, processes them, and inserts them into the database.

        Parameters
        ----------
        strategies : List[Any]
            A list of raw Carbon strategies
        block_updated : int, optional
            The last block that was updated, by default None

        """

        carbon_orders = []

        for strategy in strategies:
            # try:
            strategy_id = str(strategy[0])
            tkn0_address, tkn1_address = strategy[2][0], strategy[2][1]
            order0, order1 = strategy[3][0], strategy[3][1]
            y_0, z_0, A_0, B_0 = (
                order0[0],
                order0[1],
                order0[2],
                order0[3],
            )
            y_1, z_1, A_1, B_1 = (
                order1[0],
                order1[1],
                order1[2],
                order1[3],
            )
            tkn0_address = self.web3.toChecksumAddress(tkn0_address)
            tkn1_address = self.web3.toChecksumAddress(tkn1_address)

            if not check_if_tkn_in_table_address(tkn0_address):
                logger.info(f"Token not found in database: {tkn0_address}")
                continue
            if not check_if_tkn_in_table_address(tkn1_address):
                logger.info(f"Token not found in database: {tkn1_address}")
                continue
            tkn0_decimals = get_token_decimals_from_address(tkn0_address)

            tkn1_decimals = get_token_decimals_from_address(tkn1_address)
            token0_symbol = get_token_symbol_from_address(tkn0_address)
            token1_symbol = get_token_symbol_from_address(tkn1_address)

            tkn0 = ERC20Token(
                address=tkn0_address, symbol=token0_symbol, decimals=tkn0_decimals
            )
            tkn1 = ERC20Token(
                address=tkn1_address, symbol=token1_symbol, decimals=tkn1_decimals
            )

            if y_0 and y_0 > 0 and B_0 > 0:
                order0 = EncodedOrder(
                    y=y_0, z=z_0, A=A_0, B=B_0, token_in=tkn1, token_out=tkn0
                )
                order0 = CarbonV1Order(
                    tkn_in=tkn1,
                    tkn_out=tkn0,
                    encoded_order=order0,
                    order_id=strategy_id,
                    block_updated=block_updated,
                )
                carbon_orders.append(order0)

            if y_1 and y_1 > 0 and B_1 > 0:
                order1 = EncodedOrder(
                    y=y_1, z=z_1, A=A_1, B=B_1, token_in=tkn0, token_out=tkn1
                )
                order1 = CarbonV1Order(
                    tkn_in=tkn0,
                    tkn_out=tkn1,
                    encoded_order=order1,
                    order_id=strategy_id,
                    block_updated=block_updated,
                )
                carbon_orders.append(order1)

            # except Exception as e:
            #     logger.error(f"Error updating Carbon strategy {strategy} [{e}]")
            #     continue
        return carbon_orders


@dataclass
class ValidationHelpers(BaseHelper):
    """
    This class is used to organize bot validation tools.
    """

    tokens: List[str] = field(default_factory=list)
    exchanges: List[str] = field(default_factory=list)
    max_slippage: Decimal = field(default=ec.DEFAULT_MAX_SLIPPAGE)
    blocktime_deviation: int = field(default=ec.DEFAULT_BLOCKTIME_DEVIATION)

    def get_and_validate_trade_routes(
        self, df: pd.DataFrame
    ) -> Tuple[int, int, int, List[LiquidityPool]] or None:
        """
        Validate the cached arbitrage routes. Returns the amount in, expected profit, and deadline, and the trade path.

        :param df: The dataframe to validate

        :return: The amount in, expected profit, and deadline, and the trade path
        """
        df["profit"] = df["profit"].astype(float)
        df = df.sort_values(by="profit", ascending=False)

        # Check that the block number is the same as the current block number
        current_block_number = self.block_number

        # Split the valid and invalid routes
        already_validated, requires_validation = self._split_valid_from_invalid(
            current_block_number, df
        )
        already_validated = already_validated.sort_values(by="profit", ascending=False)
        requires_validation = requires_validation.sort_values(
            by="profit", ascending=False
        )

        is_validated = False
        if df["profit"].max() == already_validated["profit"].max():
            is_validated = True
        elif already_validated["profit"].max() > requires_validation["profit"].max():
            is_validated = True

        logger.debug(
            f"Validating {len(requires_validation)} routes, {len(already_validated)} already validated"
        )

        # Validate the routes that require validation
        valid_routes = []

        # Build the already validated routes
        input_df = already_validated if is_validated else requires_validation
        for i in input_df.index:
            outputs = self.build_or_validate_route(
                i,
                input_df.iloc[[i]],
                is_validated=is_validated,
            )
            if outputs is not None:
                src_amt, route_struct, profit = outputs
                # Extend the valid routes with the already validated routes
                valid_routes.append([src_amt, route_struct, profit])
                break

        # Return the valid routes
        return valid_routes

    def validate_tokens_and_exchanges(self):
        """
        Validates the tokens and exchanges provided by the user
        """
        assert all(tkn in ec.SUPPORTED_TOKENS for tkn in self.tokens), logger.error(
            "Invalid token(s)"
        )
        assert all(
            exchange in ec.SUPPORTED_EXCHANGE_VERSIONS for exchange in self.exchanges
        ), logger.error("Invalid exchange(s)")

    def build_or_validate_route(
        self,
        idx: int,
        df: pd.DataFrame,
        is_validated: bool = False,
    ) -> Tuple[int, List[Dict[str, Any]]] or None:
        """
        Builds or validates a route. If `is_validated` is `True`, then the route is validated. Otherwise, the route is
        built.

        :param idx: The index of the route
        :param df: The dataframe containing the pool information
        :param is_validated: Whether or not the route is validated

        :return: The route if it is validated, otherwise `None`
        """

        try:
            # Extract the attributes from the dataframe
            vars = self.df_to_pool_attributes(df=df)
            if vars:
                (
                    block_number,
                    amts_in,
                    liquidity0,
                    liquidity1,
                    liquidity2,
                    min_return_amts,
                    p1,
                    p2,
                    p3,
                    profit,
                    tkn0_0_amt,
                    tkn0_1_amt,
                    tkn1_0_amt,
                    tkn1_1_amt,
                    tkn2_0_amt,
                    tkn2_1_amt,
                ) = vars
            else:
                logger.error("No variables found")
                return None

            # Handle assertions if the route is not validated
            if not is_validated:
                self.handle_assertions(
                    df,
                    liquidity0,
                    liquidity1,
                    liquidity2,
                    self.min_profit,
                    p1,
                    p2,
                    p3,
                    profit,
                    tkn0_0_amt,
                    tkn0_1_amt,
                    tkn1_0_amt,
                    tkn1_1_amt,
                    tkn2_0_amt,
                    tkn2_1_amt,
                )

            # Calculate the deadline
            deadline = (
                self.web3.eth.getBlock(self.web3.eth.block_number).timestamp
                + self.blocktime_deviation
            )

            # Define the trade path
            web3 = self.web3

            # Create the route object in order to use the to_trade_struct method
            route: Route = Route(id=idx, trade_path=[p1, p2, p3])

            # Convert the trade path to a trade struct
            route_struct: List[Dict[str, Any]] = [
                route.to_trade_struct(
                    i, min_return_amts[i], deadline, web3, self.max_slippage
                )
                for i in range(3)
            ]

            # Convert the src amount to wei format
            src_amt = convert_decimals_to_wei_format(amts_in[0], 18)

            # Log the route struct
            if route_struct[0]["targetToken"] == route_struct[1]["targetToken"]:
                return None

            # If all checks pass, return the trade route. Includes the src_amt, and trade path (solidity trade struct)
            return src_amt, route_struct, profit

        except AssertionError as e:
            logger.warning(f"{e}")
            return None

    def df_to_pool_attributes(
        self,
        df: pd.DataFrame,
    ) -> Tuple[
        Decimal,
        List[Decimal],
        Decimal,
        Decimal,
        Decimal,
        List[Decimal],
        LiquidityPool,
        LiquidityPool,
        LiquidityPool,
        Decimal,
        Decimal,
        Decimal,
        Decimal,
        Decimal,
        Decimal,
        Decimal,
    ]:
        """
        Converts the dataframe to the pool attributes.

        :param df: The dataframe

        :return: The pool attributes
        """
        logger.debug(tabulate(df.T, headers="keys", tablefmt="psql"))
        block_number = df["block_number"].values[0]
        amt_in_0 = df["0_amt_in"].values[0]
        amt_in_1 = df["1_amt_in"].values[0]
        amt_in_2 = df["2_amt_in"].values[0]
        amts_in = [amt_in_0, amt_in_1, amt_in_2]
        amt_out_0 = df["0_amt_out"].values[0]
        amt_out_1 = df["1_amt_out"].values[0]
        amt_out_2 = df["2_amt_out"].values[0]
        amt_out_0 = (
            Decimal(amt_out_0)
            * (Decimal("100") - Decimal(self.max_slippage))
            / Decimal("100")
        )
        amt_out_1 = (
            Decimal(amt_out_1)
            * (Decimal("100") - Decimal(self.max_slippage))
            / Decimal("100")
        )
        amt_out_2 = (
            Decimal(amt_out_2)
            * (Decimal("100") - Decimal(self.max_slippage))
            / Decimal("100")
        )
        min_return_amts = [amt_out_0, amt_out_1, amt_out_2]
        profit = df["profit"].values[0]
        liquidity0 = df["0_liquidity"].values[0]
        liquidity1 = df["1_liquidity"].values[0]
        liquidity2 = df["2_liquidity"].values[0]
        tkn0_0_amt = df["0_tkn0_amt"].values[0]
        tkn0_1_amt = df["0_tkn1_amt"].values[0]
        tkn1_0_amt = df["1_tkn0_amt"].values[0]
        tkn1_1_amt = df["1_tkn1_amt"].values[0]
        tkn2_0_amt = df["2_tkn0_amt"].values[0]
        tkn2_1_amt = df["2_tkn1_amt"].values[0]

        p1_id = df["0_id"].values[0]
        p2_id = df["1_id"].values[0]
        p3_id = df["2_id"].values[0]

        p1 = [p for p in self.unique_pools if p.id == p1_id][0]
        p2 = [p for p in self.unique_pools if p.id == p2_id][0]
        p3 = [p for p in self.unique_pools if p.id == p3_id][0]
        ps = [p1, p2, p3]
        pools = []
        for p in ps:
            if p.exchange == ec.BANCOR_V3_NAME:
                p.update_liquidity(contract=self.bancor_network_info)
            else:
                p.update_liquidity()
            pools.append(p)
        p1, p2, p3 = pools

        if p1 is None or p2 is None or p3 is None:
            return None
        if p1.tkn0.symbol != "BNT":
            p1.reverse_tokens()
        if p3.tkn1.symbol != "BNT":
            p3.reverse_tokens()
        if p2.tkn0.symbol != p1.tkn1.symbol:
            p2.reverse_tokens()
        return (
            block_number,
            amts_in,
            liquidity0,
            liquidity1,
            liquidity2,
            min_return_amts,
            p1,
            p2,
            p3,
            profit,
            tkn0_0_amt,
            tkn0_1_amt,
            tkn1_0_amt,
            tkn1_1_amt,
            tkn2_0_amt,
            tkn2_1_amt,
        )

    @staticmethod
    def _split_valid_from_invalid(
        current_block_number: int, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df["current_block_number"] = [current_block_number for _ in range(len(df))]
        df["requires_validation"] = np.where(
            df["block_number"] == df["current_block_number"], False, True
        )
        requires_validation = df[df["requires_validation"] == True]
        already_validated = df[df["requires_validation"] == False]
        return already_validated, requires_validation

    @staticmethod
    def handle_assertions(
        df: pd.DataFrame,
        liquidity0: int,
        liquidity1: int,
        liquidity2: int,
        min_profit: int or Decimal,
        p1: LiquidityPool,
        p2: LiquidityPool,
        p3: LiquidityPool,
        profit: int or Decimal,
        tkn0_0_amt: int,
        tkn0_1_amt: int,
        tkn1_0_amt: int,
        tkn1_1_amt: int,
        tkn2_0_amt: int,
        tkn2_1_amt: int,
    ) -> None:
        """
        Handles the assertions for the trade route

        :param df: The dataframe containing the pool information
        :param liquidity0: The liquidity of the first pool
        :param liquidity1: The liquidity of the second pool
        :param liquidity2: The liquidity of the third pool
        :param min_profit: The minimum profit
        :param p1: The first pool
        :param p2: The second pool
        :param p3: The third pool
        :param profit: The profit
        :param tkn0_0_amt: The amount of token 0 in the first pool
        :param tkn0_1_amt: The amount of token 0 in the second pool
        :param tkn1_0_amt: The amount of token 1 in the first pool
        :param tkn1_1_amt: The amount of token 1 in the second pool
        :param tkn2_0_amt: The amount of token 2 in the first pool
        :param tkn2_1_amt: The amount of token 2 in the second pool

        :return: None
        """

        # Check that the profit is greater than the minimum profit
        assert profit >= min_profit, f"Profit: {profit} < min profit: {min_profit}"

        # Check that the logged sqrt_price_q96 is equal to the current sqrt_price_q96
        if type(p2) == UniswapV3LiquidityPool:
            sqrt_price_q96 = df["1_sqrt_price_q96"].values[0]
            assert format_amt(sqrt_price_q96) == format_amt(
                p2.sqrt_price_q96
            ), f"p2.sqrt_price_q96: {p2.sqrt_price_q96} != sqrt_price_q96: {sqrt_price_q96}"

        # Check that the logged token amounts are equal to the current token amounts
        cached_amounts = [
            tkn0_0_amt,
            tkn0_1_amt,
            tkn1_0_amt,
            tkn1_1_amt,
            tkn2_0_amt,
            tkn2_1_amt,
        ]
        cached_amounts_reverse = [
            tkn0_1_amt,
            tkn0_0_amt,
            tkn1_1_amt,
            tkn1_0_amt,
            tkn2_1_amt,
            tkn2_0_amt,
        ]
        for val1, val2, val3, val4 in zip(
            [
                p1.tkn0.amt,
                p1.tkn1.amt,
                p2.tkn0.amt,
                p2.tkn1.amt,
                p3.tkn0.amt,
                p3.tkn1.amt,
            ],
            cached_amounts,
            cached_amounts_reverse,
            [
                "p1.tkn0.amt",
                "p1.tkn1.amt",
                "p2.tkn0.amt",
                "p2.tkn1.amt",
                "p3.tkn0.amt",
                "p3.tkn1.amt",
            ],
        ):
            val1 = format_amt(val1)
            val2 = format_amt(val2)
            val3 = format_amt(val3)
            test_1 = val1 == val2
            test_2 = val1 == val3
            assert test_1 or test_2, f"for {val4}: {val1} != {val3} or {val2}"

        # Check that the logged liquidity amounts are equal to the current liquidity amounts
        cached_aamounts = [liquidity0, liquidity1, liquidity2]
        cached_amounts_reverse = [liquidity2, liquidity1, liquidity0]
        for val1, val2, val3, val4 in zip(
            [p1.liquidity, p2.liquidity, p3.liquidity],
            cached_aamounts,
            cached_amounts_reverse,
            ["p1.liquidity", "p2.liquidity", "p3.liquidity"],
        ):
            test_1 = format_amt(val1) == format_amt(val2)
            test_2 = format_amt(val1) == format_amt(val3)
            assert test_1 or test_2, f"for {val4}: {val1} != {val3} or {val2}"


@dataclass
class TestingHelpers(BaseHelper):
    """
    A class for helping with bot testing.
    """

    @staticmethod
    def get_random_pool_for_testing(
        unique_pools: List[LiquidityPool] = None,
    ) -> Tuple[Any, int]:
        """
        Gets a random pool from the list of exchanges.
        """

        pool = random.choice(unique_pools)
        tkn_in = random.choice([pool.tkn0.symbol, pool.tkn1.symbol])
        amount = random.randint(1, 25000)

        if tkn_in == "WBTC":
            amount = random.randint(1, 11)
        elif tkn_in == "WETH":
            amount = random.randint(1, 200)

        decimal_in = ec.DECIMAL_FROM_SYMBOL[tkn_in]
        decimal_adjusted_amount = int(
            Decimal(str(amount)) * Decimal("10") ** Decimal(str(decimal_in))
        )
        return pool, decimal_adjusted_amount

    def execute_random_swaps(
        self, num: int, web3: Web3, unique_pools: List[LiquidityPool] = None
    ):
        """
        Executes a random number of swaps.

        :param num: The number of swaps to execute.
        :param web3: The web3 instance.
        :param unique_pools: The list of unique pools.
        """
        random_pools = []
        random_amounts = []

        if len(unique_pools) > 0:
            for _ in range(num):
                pool, amt = TestingHelpers.get_random_pool_for_testing(
                    unique_pools=unique_pools
                )
                random_pools.append(pool)
                random_amounts.append(amt)

            with parallel_backend(n_jobs=ec.DEFAULT_N_JOBS, backend=ec.DEFAULT_BACKEND):
                Parallel(n_jobs=ec.DEFAULT_N_JOBS, backend=ec.DEFAULT_BACKEND)(
                    delayed(self.change_tenderly_pool_values)(
                        web3=web3, pool=random_pools[idx], tkn_amt=random_amounts[idx]
                    )
                    for idx, k in enumerate(random_pools)
                )

    def change_tenderly_pool_values(self, web3, pool: Any, tkn_amt: int):
        """
        Changes the values of the pool for the tenderly simulation.

        :param web3: Web3 instance
        :param pool: The pool to change the values for
        :param tkn_amt: The amount of tokens to change the values to

        :return: None
        """
        # Testing Addresses
        BINANCE8_WALLET_ADDRESS = "0xF977814e90dA44bFA03b6295A0616a897441aceC"
        BINANCE14_WALLET_ADDRESS = "0x28C6c06298d514Db089934071355E5743bf21d60"

        try:
            tkn_in_address = web3.toChecksumAddress(pool.tkn0.address)
            tkn_out_address = web3.toChecksumAddress(pool.tkn1.address)
            token_contract = web3.eth.contract(address=tkn_in_address, abi=ec.ERC20_ABI)
            tx_details = {
                "gasPrice": ec.DEFAULT_GAS_PRICE,
                "gas": ec.DEFAULT_GAS,
                "from": BINANCE8_WALLET_ADDRESS,
                "nonce": web3.eth.get_transaction_count(BINANCE8_WALLET_ADDRESS),
            }

            deadline = (
                web3.eth.getBlock(web3.eth.block_number).timestamp
                + ec.DEFAULT_BLOCKTIME_DEVIATION
            )
            router_address = web3.toChecksumAddress(
                ec.__getattribute__(f"{pool.exchange.upper()}_ROUTER_ADDRESS")
            )
            router_contract = web3.eth.contract(
                address=router_address,
                abi=ec.__getattribute__(f"{pool.exchange.upper()}_ROUTER_ABI"),
            )

            swap_tx = "0"
            if pool.exchange != ec.BANCOR_BASE:
                path = [tkn_in_address, tkn_out_address]
            function_call = token_contract.functions.approve(
                router_address, tkn_amt
            ).transact(tx_details)
            tx_reciept = web3.eth.wait_for_transaction_receipt(function_call)
            tx_hash = web3.toHex(dict(tx_reciept)["transactionHash"])

            if pool.exchange in [ec.UNISWAP_V2_NAME, ec.SUSHISWAP_NAME]:
                if pool.tkn0.is_eth():
                    transfer_tx = token_contract.functions.transfer(
                        router_address, tkn_amt
                    ).transact(tx_details)
                    web3.eth.wait_for_transaction_receipt(transfer_tx)
                    swap_tx = router_contract.functions.swapExactETHForTokens(
                        ec.ZERO_INT, path, BINANCE8_WALLET_ADDRESS, deadline
                    ).transact(tx_details)

                elif pool.tkn1.is_eth():
                    swap_tx = router_contract.functions.swapExactTokensForETH(
                        tkn_amt, ec.ZERO_INT, path, BINANCE8_WALLET_ADDRESS, deadline
                    ).transact(tx_details)
                else:
                    swap_tx = router_contract.functions.swapExactTokensForTokens(
                        tkn_amt, ec.ZERO_INT, path, BINANCE8_WALLET_ADDRESS, deadline
                    ).transact(tx_details)

            elif pool.exchange == ec.UNISWAP_V3_NAME:
                if path is None or pool.fee is None:
                    logger.error("Path or Fee is None")

                uni3_input = (
                    path[0],
                    path[1],
                    int(pool.fee),
                    BINANCE8_WALLET_ADDRESS,
                    tkn_amt,
                    0,
                    0,
                )
                swap_tx = router_contract.functions.exactInputSingle(
                    uni3_input
                ).transact(tx_details)
            if swap_tx != "0":
                tx_receipt = web3.eth.wait_for_transaction_receipt(swap_tx)
                msg = f"Random swap STATUS on {pool.exchange}!, token in = {pool.tkn0.symbol}, token out = {pool.tkn1.symbol}"
                if dict(tx_receipt)["status"] != 1:
                    logger.info(msg.replace("STATUS", "FAILED"))
                else:
                    logger.info(msg.replace("STATUS", "SUCCESS"))
                return tx_hash
            else:
                logger.info("Problem creating swap tx for Tenderly swaps")

        except Exception as e:
            logger.error(f"Error in change_tenderly_pool_values: {e}")
            return None
