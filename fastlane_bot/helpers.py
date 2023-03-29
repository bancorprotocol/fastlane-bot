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
from fastlane_bot.pools import LiquidityPool, UniswapV3LiquidityPool
from fastlane_bot.routes import Route, ConstantProductRoute, ConstantFunctionRoute
from fastlane_bot.utils import (
    format_amt,
    convert_decimals_to_wei_format,
    convert_weth_to_eth,
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
    ):
        """
        Builds the transaction to be submitted to the blockchain.

        routes: the routes to be used in the transaction
        src_amt: the amount of the source token to be sent to the transaction
        gas_price: the gas price to be used in the transaction

        returns: the transaction to be submitted to the blockchain
        """
        try:
            transaction = self.arb_contract.functions.execute(
                routes, src_amt
            ).build_transaction(
                self.build_tx(
                    gas_price=gas_price, max_priority_fee=max_priority, nonce=nonce
                )
            )
        except ValueError as e:
            message = str(e).split("baseFee: ")
            split_fee = message[1].split(" (supplied gas ")
            baseFee = int(int(split_fee[0]) * ec.DEFAULT_GAS_PRICE_OFFSET)
            transaction = self.arb_contract.functions.execute(
                routes, src_amt
            ).build_transaction(
                self.build_tx(
                    gas_price=baseFee, max_priority_fee=max_priority, nonce=nonce
                )
            )

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
        logger.debug(
            f"Searching for profitable arbitrage routes... initial_search={initial_search}"
        )
        if not initial_search:
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
            if type(i) in [ConstantProductRoute, ConstantFunctionRoute]
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
