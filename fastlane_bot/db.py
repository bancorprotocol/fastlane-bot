"""
Database manager object for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio
from typing import Dict, List, Tuple, Type

import brownie
import pandas as pd
from brownie import Contract
from joblib import parallel_backend, Parallel, delayed
from sqlalchemy import func, MetaData
from sqlalchemy.orm import Session
from web3._utils.filters import LogFilter
from web3.datastructures import AttributeDict

from fastlane_bot.abi import *
from fastlane_bot.models import *
from fastlane_bot.models import Pool
from fastlane_bot.utils import initialize_contract

from dataclasses import dataclass, field, InitVar


@dataclass
class DatabaseManager:
    """
    Factory class for creating and managing pools.

    backend: BACKEND_POSTGRES, [BACKEND_SQLITE]
        The database backend to use.
    """

    BACKEND_SQLITE = "sqlite"
    BACKEND_POSTGRES = "postgres"

    backend: str = None
    MULTICALL_CONTRACT_ADDRESS: str = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    use_multicall: bool = True
    mode: str = "production"
    drop_tables: InitVar = False

    _carbon_v1_controller: Any = None

    def __post_init__(self, drop_tables: bool = False):
        if self.backend is None:
            self.backend = self.BACKEND_POSTGRES

        if drop_tables:
            self.drop_all_tables()
            try:
                self.create_ethereum_chain()
                self.create_supported_exchanges()
            except Exception as e:
                print(e)
                session.rollback()

        self.data = self.data.sort_values("exchange", ascending=False)

    def delete_all_carbon(self):
        """
        Deletes all the pools in the database
        """
        pool = session.query(Pool).filter(Pool.exchange_name == CARBON_V1_NAME).all()
        while len(pool) > 0:
            session.delete(pool[0])
            pool = (
                session.query(Pool).filter(Pool.exchange_name == CARBON_V1_NAME).all()
            )
        session.commit()

    def refresh_session(self):
        """
        Refreshes the database session
        """
        global session
        session.close()
        session = Session(engine)

    def update_db(self):
        """
        Updates the database with the latest pools and pairs
        """
        self.refresh_session()
        self.update_pools()

    def drop_all_tables(self):
        """
        Drops all tables in the database
        """
        metadata = MetaData()
        metadata.reflect(bind=engine)
        for table in reversed(metadata.sorted_tables):
            table.drop(bind=engine, checkfirst=False)
        self.create_tables()
        self.create_ethereum_chain()
        self.create_supported_exchanges()

    @staticmethod
    def create_supported_exchanges():
        """
        Creates the supported exchanges in the database
        """
        for exchange in SUPPORTED_EXCHANGES:
            session.add(Exchange(name=exchange, blockchain_name="Ethereum"))
        session.commit()

    @staticmethod
    def create_ethereum_chain():
        """
        Creates the Ethereum chain in the database
        """
        blockchain = Blockchain(name="Ethereum")
        blockchain.update_block()
        session.add(blockchain)
        session.commit()

    @staticmethod
    def create_tables():
        """
        Creates all tables in the database
        """
        mapper_registry.metadata.create_all(engine)

    @property
    @staticmethod
    def next_cid(self):
        """
        Returns the next cid
        """
        max_idxs = session.query(Pool).all()
        if not max_idxs:
            return 0
        max_idx = max(int(x.cid) for x in max_idxs)
        return max_idx + 1 if max_idx is not None else 0

    @property
    def next_id(self):
        """
        Returns the next id
        """
        max_idx = session.query(func.max(Pool.id)).first()[0]
        return max_idx + 1 if max_idx is not None else 0

    def update_pools(self):
        """
        Updates all pools
        """
        carbon_pools, other_pools, v3_pools = self.get_pool_lists()

        if self.use_multicall:
            self.update_all_carbon_strategies()

            if v3_pools:
                self.update_liquidity_multicall(v3_pools, bancor_network_info)

        with parallel_backend("threading", n_jobs=1):
            Parallel()(
                delayed(self.update_pool)(exchange, pool_address)
                for exchange, pool_address in other_pools
            )

    def update_pool(self, exchange_name: str, pool_address: str):
        """
        Updates a pool in the database
        :param pool_address: The address of the pool to update
        :param exchange_name: The name of the exchange to update the pool for
        """
        try:
            pool = session.query(Pool).filter_by(address=pool_address).first()
            pool_contract = self.contract_from_address(exchange_name, pool_address)
            updated_params = self.get_pool_fee_and_liquidity(
                exchange_name, pool_contract, pool_address
            )
            pool.update(updated_params)
            session.commit()
        except Exception as e:
            logger.warning(
                f"Failed to update pool for {exchange_name} {pool_address} {e}"
            )

    def seed_pools(self):
        """
        Adds pools to the database
        """
        carbon_pools, other_pools, v3_pools = self.get_pool_lists()

        if self.use_multicall:
            self.update_all_carbon_strategies()

            if v3_pools:
                self.update_liquidity_multicall(v3_pools, bancor_network_info)

        if self.mode == "test":
            with parallel_backend("threading", n_jobs=1):
                Parallel()(
                    delayed(self.get_or_create_pool)(exchange, pool_address)
                    for exchange, pool_address in other_pools
                )

    def get_pool_lists(
        self,
    ) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Returns a list of pools for each exchange
        """
        pools = list(self.data[["exchange", "address"]].values)
        v3_pools = carbon_pools = other_pools = []
        for pool in pools:
            if pool[0] == BANCOR_V3_NAME:
                v3_pools.append(pool)
            elif pool[0] == CARBON_V1_NAME:
                carbon_pools.append(pool)
            else:
                other_pools.append(pool)
        return carbon_pools, other_pools, v3_pools

    @staticmethod
    def remove_eth_from_tokens(tokens: List[str]) -> List[str]:
        """
        Removes ETH from the list of tokens and adds it to the end of the list
        :param tokens: A list of token addresses
        :return: A list of token addresses
        """
        if WETH_ADDRESS in tokens:
            tokens.remove(WETH_ADDRESS)
        if ETH_ADDRESS not in tokens:
            tokens.append(ETH_ADDRESS)
        return tokens

    @staticmethod
    def address_to_key(address: str) -> str:
        """
        Converts an address to a key
        :param address:  The address to convert
        :return:  The Token key
        """
        return session.query(Token).filter(Token.address == address).first().key

    def _deprecated_get_or_create_pool(
        self, exchange_name: str = None, pool_address: str = None
    ) -> Pool:
        """
        Creates a pool in the database
        :param exchange_name: The name of the exchange to create the pool for
        :param pool_address: The address of the pool to create
        """
        try:
            pool = session.query(Pool).filter_by(address=pool_address).first()
            if pool:
                return pool

            pool_contract = self.contract_from_address(exchange_name, pool_address)
            tkn0_address, tkn1_address = self.get_token_addresses_for_pool(
                exchange_name, pool_address, pool_contract
            )
            tkn0 = self.get_or_create_token(tkn0_address)
            tkn1 = self.get_or_create_token(tkn1_address)
            pair = self.get_or_create_pair(tkn0_address, tkn1_address)
            common_data = self.get_common_data_for_pool(
                cid=str(self.next_cid),
                exchange_name=exchange_name,
                pair_name=pair.name,
                pool_address=pool_address,
                tkn0_address=tkn0_address,
                tkn1_address=tkn1_address,
                tkn0_key=tkn0.key,
                tkn1_key=tkn1.key,
            )
            other_params = self.get_pool_fee_and_liquidity(
                exchange_name, pool_contract, tkn1_address
            )
            self.commit_pool(common_data, other_params)

        except Exception as e:
            logger.warning(
                f"Failed to create pool for {exchange_name}, {pool_address}, {e}"
            )

    @staticmethod
    def get_token_addresses_for_pool(
        exchange_name: str, pool_address: str, pool_contract: Contract
    ) -> Tuple[str, str]:
        """
        Gets the token addresses for a pool

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool
        pool_contract : Contract
            The pool contract

        Returns
        -------
        Tuple[str, str]
            The token addresses
        """
        if exchange_name == BANCOR_V3_NAME:
            tkn0_address = w3.toChecksumAddress(BNT_ADDRESS)
            tkn1_address = w3.toChecksumAddress(pool_address)
        else:
            try:
                tkn0_address = w3.toChecksumAddress(pool_contract.caller.token0())
                tkn1_address = w3.toChecksumAddress(pool_contract.caller.token1())
            except Exception as e:
                logger.debug(f"Error getting tokens for pool {pool_address} - {e}")
                reserve_tokens = pool_contract.caller.reserveTokens()
                tkn0_address = w3.toChecksumAddress(reserve_tokens[0])
                tkn1_address = w3.toChecksumAddress(reserve_tokens[1])
        return tkn0_address, tkn1_address

    @staticmethod
    def commit_pool(common_data: Dict[str, Any], other_params: Dict[str, Any]):
        """
        Commits a pool to the database
        :param common_data:  The common data for the pool
        :param other_params:  The other parameters for the pool
        """
        pool_params = {
            **common_data,
            **other_params,
        }
        try:
            pool = Pool(**pool_params)
            session.add(pool)
            session.commit()
        except Exception as e:
            session.rollback()
            try:
                pool = Pool(**pool_params)
                session.commit()
            except Exception as e:
                logger.warning(
                    f"Failed to commit pool pool_params={pool_params}, - {e}, {e.__traceback__}, skipping..."
                )

    @staticmethod
    def create_tasks_and_run(updater):
        tasks = []
        logger.info("Creating tasks")
        for args in updater.filters:
            exchange, _filter = args["exchange"], args["_filter"]
            updater._log_loop_noasync(exchange, _filter)
            logger.info(f"Created task for {exchange}, {_filter}")

    # def get_common_data_for_pool(
    #     self,
    #     cid: str,
    #     exchange_name: str,
    #     pair_name: str,
    #     pool_address: str = None,
    #     tkn0_address: str = None,
    #     tkn1_address: str = None,
    #     tkn0_key: str = None,
    #     tkn1_key: str = None,
    # ) -> Dict[str, Any]:
    #     """
    #     Returns the common data for a pool
    #     """
    #     return {
    #         "id": self.next_id,
    #         "cid": cid,
    #         "exchange_name": exchange_name,
    #         "tkn0_key": tkn0_key,
    #         "tkn1_key": tkn1_key,
    #         "tkn0_address": tkn0_address,
    #         "tkn1_address": tkn1_address,
    #         "address": pool_address,
    #         "pair_name": pair_name,
    #         "last_updated_block": w3.eth.blockNumber,
    #     }

    def get_common_data_for_pool(
        self,
        cid: str,
        exchange_name: str,
        pair_name: str,
        pool_address: str = None,
        tkn0_address: str = None,
        tkn1_address: str = None,
        tkn0_key: str = None,
        tkn1_key: str = None,
        last_updated_block: str = None,
    ) -> Dict[str, Any]:
        """
        Returns the common data for a pool
        """
        if last_updated_block is None:
            last_updated_block = w3.eth.blockNumber
        return {
            "id": self.next_id,
            "cid": cid,
            "exchange_name": exchange_name,
            "tkn0_key": tkn0_key,
            "tkn1_key": tkn1_key,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
            "address": pool_address,
            "pair_name": pair_name,
            "last_updated_block": last_updated_block,
        }

    @staticmethod
    def contract_from_address(exchange_name: str, pool_address: str) -> Contract:
        """
        Returns the contract for a given exchange and pool address
        :param exchange_name:  The name of the exchange
        :param pool_address:  The address of the pool
        :return:  The address and contract
        """
        if exchange_name == BANCOR_V2_NAME:
            return initialize_contract(
                web3=w3,
                address=w3.toChecksumAddress(pool_address),
                abi=BANCOR_V2_CONVERTER_ABI,
            )
        elif exchange_name == BANCOR_V3_NAME:
            return initialize_contract(
                web3=w3,
                address=w3.toChecksumAddress(pool_address),
                abi=BANCOR_V3_POOL_COLLECTION_ABI,
            )
        elif exchange_name in UNIV2_FORKS:
            return initialize_contract(
                web3=w3,
                address=w3.toChecksumAddress(pool_address),
                abi=UNISWAP_V2_POOL_ABI,
            )
        elif exchange_name == UNISWAP_V3_NAME:
            return initialize_contract(
                web3=w3,
                address=w3.toChecksumAddress(pool_address),
                abi=UNISWAP_V3_POOL_ABI,
            )
        elif CARBON_V1_NAME in exchange_name:
            return initialize_contract(
                web3=w3,
                address=w3.toChecksumAddress(pool_address),
                abi=CARBON_CONTROLLER_ABI,
            )
        else:
            raise NotImplementedError(f"Exchange {exchange_name} not implemented")

    @staticmethod
    def get_pool_fee_and_liquidity(
        exchange_name: str,
        pool_contract: Contract,
        tkn1_address: str,
        processed_event: Any = None,
    ) -> Dict[str, Any]:
        """
        Gets the pool info for a given pair of tokens on Bancor V3
        :param exchange_name:  The name of the exchange
        :param pool_contract:  The contract of the pool
        :param tkn1_address:  The address of the second token in the pair
        :return:  The pool information as a dictionary
        """
        if exchange_name == BANCOR_V3_NAME:
            pool_balances = pool_contract.tradingLiquidity(tkn1_address)
            if pool_balances:
                return {
                    "fee": "0.000",
                    "tkn0_balance": pool_balances[0],
                    "tkn1_balance": pool_balances[1],
                }
        elif exchange_name == BANCOR_V2_NAME:
            reserve0, reserve1 = pool_contract.caller.reserveBalances()
            return {
                "fee": pool_contract.caller.conversionFee(),
                "tkn0_balance": reserve0,
                "tkn1_balance": reserve1,
            }
        elif exchange_name == UNISWAP_V3_NAME:
            slot0 = pool_contract.caller.slot0()
            return {
                "tick": slot0[1],
                "sqrt_price_q96": slot0[0],
                "liquidity": pool_contract.caller.liquidity(),
                "fee": pool_contract.caller.fee(),
                "tick_spacing": pool_contract.caller.tickSpacing(),
            }
        elif exchange_name in UNIV2_FORKS:
            reserve_balance = pool_contract.caller.getReserves()
            return {
                "fee": "0.003",
                "tkn0_balance": reserve_balance[0],
                "tkn1_balance": reserve_balance[1],
            }
        elif exchange_name == CARBON_V1_NAME:
            if processed_event is not None:
                return {
                    "y_0": processed_event["order0"][0],
                    "z_0": processed_event["order0"][1],
                    "A_0": processed_event["order0"][2],
                    "B_0": processed_event["order0"][3],
                    "y_1": processed_event["order1"][0],
                    "z_1": processed_event["order1"][1],
                    "A_1": processed_event["order1"][2],
                    "B_1": processed_event["order1"][3],
                }

    @staticmethod
    def get_or_create_pair(tkn0_address: str, tkn1_address: str) -> Pair:
        """
        Adds pairs to the database

        :param tkn0_address:  The address of the first token in the pair
        :param tkn1_address:  The address of the second token in the pair
        :return:  The pair object
        """
        tkn0_key = (
            session.query(Token).filter(Token.address == tkn0_address).first().key
        )
        tkn1_key = (
            session.query(Token).filter(Token.address == tkn1_address).first().key
        )
        pair_name = f"{tkn0_key}/{tkn1_key}"
        pair = session.query(Pair).filter(Pair.name == pair_name).first()
        if pair:
            return pair
        pair = Pair(
            name=pair_name,
            tkn0_key=tkn0_key,
            tkn1_key=tkn1_key,
            tkn0_address=tkn0_address,
            tkn1_address=tkn1_address,
        )
        session.add(pair)
        session.commit()
        return session.query(Pair).filter(Pair.name == pair_name).first()

    @staticmethod
    def tkn_from_address(address: str) -> Token:
        """
        Creates a token object from an address

        :param address:  The address of the token
        :return:  token object
        """
        address = w3.toChecksumAddress(address)
        tkn = session.query(Token).filter(Token.address == address).first()
        if tkn:
            return tkn
        if address == MKR_ADDRESS:
            return Token(symbol="MKR", address=address, decimals=18, name="Maker")
        elif address == ETH_ADDRESS:
            return Token(symbol="ETH", address=address, decimals=18, name="Ethereum")
        else:
            contract = initialize_contract(
                address=w3.toChecksumAddress(address), abi=ERC20_ABI, web3=w3
            )
            return Token(
                symbol=contract.caller.symbol(),
                address=address,
                decimals=contract.caller.decimals(),
                name=contract.caller.name(),
            )

    @staticmethod
    def get_or_create_token(address: str) -> Token:
        """
        Gets or creates a token in the database
        :param address:  The address of the token
        :return:  The token object
        """
        tkn = session.query(Token).filter(Token.address == address).first()
        if tkn:
            return tkn
        tkn = DatabaseManager.tkn_from_address(address)
        tkn.key = f"{tkn.symbol}-{tkn.address[-4:]}"
        session.add(tkn)
        session.commit()
        return tkn

    @staticmethod
    def get_last_block_updated(name: str) -> Blockchain or None:
        """
        Get the last block from which we collected 0.0-data-archive. This can be used to check the starting point from where we should gather 0.0-data-archive.
        name: The name of the blockchain. (unique) (non-null)
        """
        try:
            last_block = (
                session.query(Blockchain).filter(Blockchain.name == name).last_block
            )
        except AttributeError:
            return None

        return last_block

    @staticmethod
    def get_latest_block_for_pair(pair_name: str, exchange_name: str) -> int or str:
        """
        Get the last block from which we collected 0.0-data-archive for a specific token pair on a specific exchange.

        :param pair_name: The name of the pair. (unique) (non-null)
        :param exchange_name: The name of the exchange. (unique) (non-null)

        :return: The last block from which we collected events for the pair on the exchange.
        """
        try:
            return (
                session.query(Pool)
                .filter(
                    Pool.pair_name == pair_name, Pool.exchange_name == exchange_name
                )
                .first()
                .last_updated_block
            )
        except AttributeError:
            return "latest"

    @staticmethod
    def get_pool_by_address(address: str) -> Pool:
        """
        Get a pool by address.
        address: The address of the pool.
        """
        return session.query(Pool).filter(Pool.address == address).first()

    def update_liquidity_multicall(
        self, pools: List[Tuple[str, str]], contract: Contract
    ):
        """
        Setup Bancor V3 pools with multicall to improve efficiency

        :param contract: The contract to use for multicall
        :param pools: List of Bancor V3 pools

        :return: List of pools (including Bancor V3 pools) combined
        """
        if not pools:
            return
        with brownie.multicall(address=self.MULTICALL_CONTRACT_ADDRESS):
            for exchange, pool_address in pools:

                try:
                    p = (
                        session.query(Pool)
                        .filter(
                            Pool.address == pool_address, Pool.exchange_name == exchange
                        )
                        .first()
                    )
                    if p:
                        continue

                    if exchange == BANCOR_V3_NAME:
                        print("updating bancor v3 pool")
                        tkn0_address, tkn1_address = BNT_ADDRESS, pool_address
                        self.get_or_create_token(tkn0_address)
                        self.get_or_create_token(tkn1_address)
                        self.get_or_create_pair(tkn0_address, tkn1_address)
                        self.get_or_create_pool(
                            exchange_name=exchange,
                            pool_identifier=pool_address,
                            processed_event=None,
                        )
                except Exception as e:
                    logger.warning(
                        f"Error updating pool {pool_address} on {exchange}, {e}, continuing..."
                    )
                    continue

    @staticmethod
    def get_carbon_pairs() -> List[Tuple[str, str]]:
        """
        Returns a list of all Carbon token pairs
        """
        return carbon_controller.pairs()

    @staticmethod
    def get_carbon_strategy(strategy_id: int) -> Any:
        """
        :param strategy_id: the id of the strategy
        Returns the specified Carbon Strategy
        """
        return carbon_controller.strategy(strategy_id)

    @staticmethod
    def get_strategies_count_by_pair(token0: str, token1: str) -> int:
        """
        Returns the number of strategies in the specified token pair
        :param token0: the token address of the first token
        :param token1: the token address of the second token
        """
        return carbon_controller.strategiesByPairCount(token0, token1)

    @staticmethod
    def get_strategies_by_pair(
        token0: str, token1: str, start_idx: int, end_idx: int
    ) -> List[int]:
        """
        Returns a list of strategy ids for the specified pair, given a start and end index
        :param token0: the token address of the first token
        :param token1: the token address of the second token
        :param start_idx: the index to start from
        :param end_idx: the index to end
        The index flexibility enables chunking results if there are an enormous number of strategies.
        """
        return carbon_controller.strategiesByPair(token0, token1, start_idx, end_idx)

    def get_all_carbon_strategies(self):
        """
        Gets every Carbon Strategy
        """
        all_pairs = self.get_carbon_pairs()

        strats = []

        with brownie.multicall(address=self.MULTICALL_CONTRACT_ADDRESS):
            for i in all_pairs:
                num_strategies = self.get_strategies_count_by_pair(i[0], i[1])
                all_strategies_this_pair = self.get_strategies_by_pair(
                    token0=i[0], token1=i[1], start_idx=0, end_idx=num_strategies
                )
                strats += list(all_strategies_this_pair)

        return strats

    def update_all_carbon_strategies(self):
        """
        Finds and updates all Carbon strategies
        """
        all_strategies = self.get_all_carbon_strategies()
        self.update_raw_carbon_strategies(strategies=all_strategies)

    @staticmethod
    def chunker(seq, size: int) -> Any:
        """
        Splits a list into chunks of a specified size
        :param seq:  the list to split up
        :param size: the size of the chunks
        :return: a generator of the chunks
        """
        return (seq[pos : pos + size] for pos in range(0, len(seq), size))

    def get_carbon_strategies_multicall(self, strategy_ids: []):
        """
        Returns raw Carbon strategies of the specified ids.
        The return format is:
        Strategy {
            uint256 id;
            address owner;
            Token[2] tokens;
            Order[2] orders;
            }
        """
        strategies = []

        for group in self.chunker(strategy_ids, CARBON_STRATEGY_CHUNK_SIZE):
            with brownie.multicall(address=self.MULTICALL_CONTRACT_ADDRESS):
                strategies += [
                    self.get_carbon_strategy(strat_id[0]) for strat_id in group
                ]
        return strategies

    def update_raw_carbon_strategies(self, strategies: List[Any]):
        """
        Takes a list of Carbon Strategies in the raw contract format, processes them, and inserts them into the database.
        :param strategies: a list of raw Carbon strategies
        """
        for strategy in strategies:
            try:
                strategy_id = strategy[0]
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
                tkn0_address = w3.toChecksumAddress(tkn0_address)
                tkn1_address = w3.toChecksumAddress(tkn1_address)
                tkn0 = self.get_or_create_token(tkn0_address)
                tkn1 = self.get_or_create_token(tkn1_address)
                pair = self.get_or_create_pair(tkn0_address, tkn1_address)
                common_data = self.get_common_data_for_pool(
                    cid=str(strategy_id),
                    exchange_name=CARBON_V1_NAME,
                    pair_name=pair.name,
                    pool_address=CARBON_CONTROLLER_ADDRESS,
                    tkn0_address=tkn0_address,
                    tkn1_address=tkn1_address,
                    tkn0_key=tkn0.key,
                    tkn1_key=tkn1.key,
                )
                other_params = {
                    "y_0": y_0,
                    "z_0": z_0,
                    "A_0": A_0,
                    "B_0": B_0,
                    "y_1": y_1,
                    "z_1": z_1,
                    "A_1": A_1,
                    "B_1": B_1,
                }
                self.commit_pool(common_data, other_params)
            except Exception as e:
                logger.warning(f"Error updating Carbon strategy: {str(strategy_id)}")
                logger.warning(e)
                continue

    @staticmethod
    def get_latest_block_for_exchange(exchange_name: str) -> int or str:
        """
        Get the last block from which we collected 0.0-data-archive for a specific exchange.


        :param exchange_name: The name of the exchange. (unique) (non-null)

        :return: The last block from which we collected events for the exchange.
        """
        try:
            last_block = (
                session.query(Exchange)
                .filter(exchange_name == Exchange.name)
                .first()
                .last_updated_block
            )

            return last_block

        except AttributeError:
            return "latest"

    def get_pool_from_identifier(
        self, exchange_name: str = None, pool_identifier: Any = None
    ) -> Optional[Pool or None]:
        """
        Gets a Pool object using different identifiers. For Carbon, it uses the pool's CID. For Bancor V3, it uses TKN 1 address.
        For other exchanges, it uses the liquidity pool address.
        """

        if exchange_name == BANCOR_V3_NAME:
            return (
                session.query(Pool)
                .filter(
                    Pool.exchange_name == BANCOR_V3_NAME,
                    Pool.tkn1_address == pool_identifier,
                )
                .first()
            )
        elif CARBON_V1_NAME in exchange_name:
            return session.query(Pool).filter(Pool.cid == str(pool_identifier)).first()
        else:
            return session.query(Pool).filter(Pool.address == pool_identifier).first()

    def get_or_create_pool(
        self,
        exchange_name: str = None,
        pool_identifier: str = None,
        processed_event: Dict[str, Any] = None,
    ) -> Pool:
        """
        Creates a pool in the database
        :param exchange_name: The name of the exchange to create the pool for
        :param pool_identifier: The address of the pool to create. For Bancor V3 this is the address of TKN1. For Carbon, this is the Strategy id.
        """
        try:
            if processed_event is None:
                return self._deprecated_get_or_create_pool(
                    exchange_name, pool_identifier
                )

            pool = self.get_pool_from_identifier(
                exchange_name=exchange_name, pool_identifier=pool_identifier
            )
            if pool:
                return pool

            (
                block_number,
                cid,
                pool_address,
                pool_contract,
                tkn0_address,
                tkn1_address,
                exchange_name,
            ) = DatabaseManager._parse_processed_event(
                exchange_name, pool_identifier, processed_event
            )
            tkn0 = self.get_or_create_token(tkn0_address)
            tkn1 = self.get_or_create_token(tkn1_address)
            pair = self.get_or_create_pair(tkn0_address, tkn1_address)
            common_data = self.get_common_data_for_pool(
                cid=str(cid),
                exchange_name=exchange_name,
                pair_name=pair.name,
                tkn0_address=tkn0_address,
                tkn1_address=tkn1_address,
                tkn0_key=tkn0.key,
                tkn1_key=tkn1.key,
                pool_address=pool_address,
                last_updated_block=block_number,
            )
            other_params = {"fee": self.get_pool_fee(exchange_name, pool_contract)}
            carbon_params = (
                {
                    "y_0": processed_event["order0"][0],
                    "z_0": processed_event["order0"][1],
                    "A_0": processed_event["order0"][2],
                    "B_0": processed_event["order0"][3],
                    "y_1": processed_event["order1"][0],
                    "z_1": processed_event["order1"][1],
                    "A_1": processed_event["order1"][2],
                    "B_1": processed_event["order1"][3],
                }
                if exchange_name == CARBON_V1_NAME
                else {}
            )
            all_params = {**common_data, **other_params, **carbon_params}
            logger.debug(f"all_params={all_params}")
            try:
                pool = Pool(**all_params)
                session.add(pool)
                session.commit()
                logger.info(f"Successfully created pool!!!: {all_params}")
                return None
            except Exception as e:
                logger.warning(e)
                return None

        except Exception as e:
            logger.warning(e)
            return None

    @staticmethod
    def _parse_processed_event(
        exchange_name: str, pool_identifier: str, processed_event: Dict[str, Any]
    ):
        block_number = processed_event["block_number"]
        if CARBON_V1_NAME in exchange_name:
            exchange_name = CARBON_V1_NAME
            pool_contract = carbon_controller
            tkn0_address, tkn1_address = (
                processed_event["token0"],
                processed_event["token1"],
            )
            pool_address = CARBON_CONTROLLER_ADDRESS
            cid = processed_event["id"]
        elif exchange_name == BANCOR_V3_NAME:
            pool_address = BANCOR_V3_NETWORK_INFO_ADDRESS
            pool_contract = bancor_network_info
            tkn0_address = BNT_ADDRESS
            tkn1_address = processed_event["pool"]
            cid = DatabaseManager.next_cid
        else:
            pool_address = pool_identifier
            pool_contract = DatabaseManager.contract_from_address(
                exchange_name, pool_identifier
            )
            tkn0_address, tkn1_address = DatabaseManager.get_token_addresses_for_pool(
                exchange_name, pool_identifier, pool_contract
            )
            cid = DatabaseManager.next_cid
        return (
            block_number,
            cid,
            pool_address,
            pool_contract,
            tkn0_address,
            tkn1_address,
            exchange_name,
        )

    @staticmethod
    def get_pool_fee(
        exchange_name: str,
        pool_contract: Contract,
    ) -> str:
        """
        Gets the pool info for a given pair of tokens on Bancor V3
        :param exchange_name:  The name of the exchange
        :param pool_contract:  The contract of the pool
        :return:  The pool information as a dictionary
        """
        if exchange_name == BANCOR_V3_NAME:
            return "0.000"
        elif exchange_name == BANCOR_V2_NAME:
            return str(pool_contract.caller.conversionFee())
        elif exchange_name == UNISWAP_V3_NAME:
            return str(pool_contract.caller.fee())
        elif exchange_name in UNIV2_FORKS:
            return "0.003"
        elif CARBON_V1_NAME in exchange_name:
            return "0.002"

    @staticmethod
    def delete_carbon_strategy(strategy_id: int) -> Any:
        """
        :param strategy_id: the id of the strategy
        Deletes the specified Carbon Strategy
        """
        strategy = session.query(Pool).filter_by(cid=strategy_id).first()
        session.delete(strategy)
        session.commit()


@dataclass
class EventUpdater:
    """
    Processes events from the Ethereum network and updates the database accordingly

    Parameters
    ----------
    db: DatabaseManager
        The database manager to use
    poll_interval: int
        The number of seconds to wait between polling the Ethereum network for new events
    test_sample_size: int
        The number of pools to use for testing. If None, all pools will be used.

    """

    db: DatabaseManager
    poll_interval: int = 12
    test_mode: bool = False

    _carbon_v1_contract: Optional[Contract] = None
    filters: List[Any] = field(default_factory=list)

    def __post_init__(self):
        self.exchange_list = [
            exchange.name for exchange in session.query(Exchange).all()
        ]

        self.exchange_list = [
            CARBON_V1_NAME,
            UNISWAP_V2_NAME,
            UNISWAP_V3_NAME,
            BANCOR_V3_NAME,
            BANCOR_V2_NAME
        ]

        logger.debug(f"post init on EventUpdater, exchanges = {self.exchange_list}")
        if (
            UNISWAP_V2_NAME in self.exchange_list
            and SUSHISWAP_V2_NAME in self.exchange_list
        ):
            self.exchange_list.remove(SUSHISWAP_V2_NAME)

        if self.test_mode:
            self.log_tasks = [
                {
                    "exchange": exchange_name,
                    "_filter": self._get_log_loop_tasks(exchange_name),
                }
                for exchange_name in self.exchange_list
            ]
        else:
            self._get_event_filters(self.exchange_list)
            logger.info(self.filters)

        logger.info(self.exchange_list)

    def _get_event_filters(self, exchanges: [str]) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        Parameters
        ----------
        exchanges: [str]
            The list of exchanges to get the filters for

        Returns
        -------
        None
        """

        if BANCOR_V2_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(BANCOR_V2_NAME)
            contract = self._get_contract_for_exchange(exchange=BANCOR_V2_NAME)
            self.filters.append(
                {
                    "exchange": BANCOR_V2_NAME,
                    "_filter": contract.events.TokenRateUpdate.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
        if BANCOR_V3_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(BANCOR_V3_NAME)
            contract = self._get_contract_for_exchange(exchange=BANCOR_V3_NAME)
            self.filters.append(
                {
                    "exchange": BANCOR_V3_NAME,
                    "_filter": contract.events.TradingLiquidityUpdated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
        if UNISWAP_V2_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(UNISWAP_V2_NAME)
            contract = self._get_contract_for_exchange(exchange=UNISWAP_V2_NAME)
            self.filters.append(
                {
                    "exchange": UNISWAP_V2_NAME,
                    "_filter": contract.events.Sync.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

        if UNISWAP_V3_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(UNISWAP_V3_NAME)
            contract = self._get_contract_for_exchange(exchange=UNISWAP_V3_NAME)
            self.filters.append(
                {
                    "exchange": UNISWAP_V3_NAME,
                    "_filter": contract.events.Swap.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

        if CARBON_V1_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(CARBON_V1_NAME)
            contract = self._get_contract_for_exchange(exchange=CARBON_V1_NAME)
            self.filters.append(
                {
                    "exchange": CARBON_STRATEGY_CREATED,
                    "_filter": contract.events.StrategyCreated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
            self.filters.append(
                {
                    "exchange": CARBON_STRATEGY_DELETED,
                    "_filter": contract.events.StrategyDeleted.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
            self.filters.append(
                {
                    "exchange": CARBON_STRATEGY_UPDATED,
                    "_filter": contract.events.StrategyUpdated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

    def _handle_event(self, exchange: str, event_log: Any, event_type: str = None):
        """
        Handles an event log from the Ethereum network

        Parameters
        ----------
        exchange: str
            The name of the exchange the event came from
        event_log: Any
            The event log to process
        event_type: str
            The type of event to process
        """
        # try:
        processed_event = self.build_processed_event(event_log, exchange)
        pool_identifier = self._get_pool_identifier(event_log, exchange)
        (
            block_number,
            cid,
            pool_address,
            pool_contract,
            tkn0_address,
            tkn1_address,
            exchange,
        ) = DatabaseManager._parse_processed_event(
            exchange, pool_identifier, processed_event
        )

        logger.debug(
            f"Getting or creating pool for processed_event= {processed_event}, pool_identifier = {pool_identifier}"
        )
        pool = self.db.get_or_create_pool(
            exchange_name=exchange,
            pool_identifier=pool_identifier,
            processed_event=processed_event,
        )
        if pool:
            logger.debug(
                f"updating pool for exchange = {exchange}, event = {event_log}, event_type = {event_type}"
            )
            pool.last_updated_block = block_number

            if pool.exchange_name == BANCOR_V3_NAME:
                pool = self._update_bancor3_liquidity(pool, processed_event)

            elif pool.exchange_name == UNISWAP_V3_NAME:
                pool = self._update_uni3_liquidity(pool, processed_event)

            elif pool.exchange_name in UNIV2_FORKS + [BANCOR_V2_NAME]:
                pool = self._update_other_liquidity(pool, processed_event)

            elif CARBON_V1_NAME in pool.exchange_name:
                pool = self._update_carbon_liquidity(
                    cid, event_type, pool, processed_event
                )

            is_created = session.query(Pool).filter(Pool.cid == cid).first()
            if not is_created:
                session.add(pool)
            session.commit()
            logger.info(
                f"Successfully updated event for {exchange} {pool.pair_name} {pool.fee} at block {block_number}..."
            )

    def _update_carbon_liquidity(self, cid, event_type, pool, processed_event):
        if event_type == "delete":
            self.db.delete_carbon_strategy(cid)
        else:
            pool = self._handle_carbon_pool_update(cid, pool, processed_event)
        return pool

    def _update_other_liquidity(self, pool, processed_event) -> Pool:
        pool.tkn0_balance = processed_event["tkn0_balance"]
        pool.tkn1_balance = processed_event["tkn1_balance"]
        return pool

    def _update_uni3_liquidity(self, pool, processed_event) -> Pool:
        pool.sqrt_price_q96 = processed_event["sqrt_price_q96"]
        pool.liquidity = processed_event["liquidity"]
        pool.tick = processed_event["tick"]
        return pool

    def _update_bancor3_liquidity(self, pool, processed_event) -> Pool:
        if processed_event["token"] == BNT_ADDRESS:
            pool.tkn0_balance = processed_event["newLiquidity"]
        else:
            pool.tkn1_balance = processed_event["newLiquidity"]
        return pool

    def _get_pool_identifier(self, event_log, exchange):
        if CARBON_V1_NAME in exchange:
            pool_identifier = event_log["args"].get("id")

        elif exchange == BANCOR_V3_NAME:
            pool_identifier = event_log["args"].get("pool")
        else:
            pool_identifier = event_log["address"]
        return pool_identifier

    def _handle_carbon_pool_update(
        self, cid: int, pool: Pool, processed_event: Dict[str, Any]
    ) -> Pool:
        pool.cid = str(cid)
        pool.y_0 = processed_event["order0"][0]
        pool.z_0 = processed_event["order0"][1]
        pool.A_0 = processed_event["order0"][2]
        pool.B_0 = processed_event["order0"][3]
        pool.y_1 = processed_event["order1"][0]
        pool.z_1 = processed_event["order1"][1]
        pool.A_1 = processed_event["order1"][2]
        pool.B_1 = processed_event["order1"][3]
        return pool

    @staticmethod
    def build_processed_event(
        event_log: AttributeDict, exchange: str
    ) -> Dict[str, Any]:
        """
        Builds a processed event from the event log and exchange name
        :param event_log:  event log from web3 Contract.events
        :param exchange: exchange name
        :return: processed event
        """
        logger.debug(f"event_log = {event_log}")
        block_number = event_log["blockNumber"]
        logger.debug(f"exchange = {exchange}, blocknumber = {block_number}")
        processed_event = {"block_number": block_number}
        if exchange == BANCOR_V3_NAME:
            processed_event["pool"] = event_log["args"].get("pool")
            processed_event["token"] = event_log["args"].get("token")
            processed_event["newLiquidity"] = event_log["args"].get("newLiquidity")
        elif exchange in UNIV2_FORKS + [BANCOR_V2_NAME]:
            processed_event["tkn0_balance"] = event_log["args"].get("reserve0")
            processed_event["tkn1_balance"] = event_log["args"].get("reserve1")
        elif exchange == UNISWAP_V3_NAME:
            processed_event["sqrt_price_q96"] = event_log["args"].get("sqrtPriceX96")
            processed_event["liquidity"] = event_log["args"].get("liquidity")
            processed_event["tick"] = event_log["args"].get("tick")
            processed_event["tick_spacing"] = event_log["args"].get("tickSpacing")
        elif CARBON_V1_NAME in exchange:
            processed_event["token0"] = event_log["args"].get("token0")
            processed_event["token1"] = event_log["args"].get("token1")
            if event_log["args"].get("pairId"):
                return processed_event
            else:
                processed_event["id"] = event_log["args"].get("id")
                processed_event["order0"] = event_log["args"].get("order0")
                processed_event["order1"] = event_log["args"].get("order1")

        return processed_event

    def _get_contract_for_exchange(
        self, exchange: str = None, pool_address: str = None, init_contract=True
    ) -> Contract:
        """
        Get the relevant ABI for the exchange
        """
        if exchange == BANCOR_V2_NAME:
            return w3.eth.contract(abi=BANCOR_V2_CONVERTER_ABI, address=pool_address)

        elif exchange == BANCOR_V3_NAME:
            if init_contract:
                return w3.eth.contract(
                    abi=BANCOR_V3_POOL_COLLECTION_ABI,
                    address=w3.toChecksumAddress(BANCOR_V3_POOL_COLLECTOR_ADDRESS),
                )
            else:
                return bancor_network_info

        elif exchange in UNIV2_FORKS:
            return w3.eth.contract(abi=UNISWAP_V2_POOL_ABI, address=pool_address)

        elif exchange == UNISWAP_V3_NAME:
            return w3.eth.contract(abi=UNISWAP_V3_POOL_ABI, address=pool_address)

        elif CARBON_V1_NAME in exchange:
            return carbon_controller

    def get_pair_name_from_contract(self, exchange: str, contract: Contract) -> str:
        """
        Get the pair name from the contract

        :param exchange: exchange name
        :param contract: contract object

        :return: pair name in the format of tkn0_key/tkn1_key
        """
        tkn0_address = contract.caller.token0()
        tkn0_key = self.db.tkn_from_address(tkn0_address).key
        tkn1_address = contract.caller.token1()
        tkn1_key = self.db.tkn_from_address(tkn1_address).key
        return f"{tkn0_key}/{tkn1_key}"

    def _get_logs(self, exchange: str, contract: Contract) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        :param exchange: exchange name
        :param contract: contract object
        :return: filter for the relevant event
        """

        # pair_name = self.get_pair_name_from_contract(exchange, contract)
        # from_block = self.db.get_latest_block_for_pair(pair_name, exchange)
        from_block = self.db.get_latest_block_for_exchange(exchange)

        # logger.info(f"Starting from block {from_block} for {pair_name} on {exchange}")
        logger.info(f"Starting from block {from_block} on {exchange}")
        if exchange == BANCOR_V2_NAME:
            return contract.events.TokenRateUpdate.get_logs(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == BANCOR_V3_NAME:
            return contract.events.TradingLiquidityUpdated.get_logs(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange in UNIV2_FORKS:
            return contract.events.Sync.get_logs(fromBlock=from_block, toBlock="latest")
        elif exchange == UNISWAP_V3_NAME:
            return contract.events.Swap.get_logs(fromBlock=from_block, toBlock="latest")
        elif CARBON_V1_NAME in exchange:
            return [
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.PairCreated.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyCreated.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyDeleted.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyUpdated.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
            ]

    def _get_event_filter(self, exchange: str, contract: Contract) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        :param exchange: exchange name
        :param contract: contract object
        :return: filter for the relevant event
        """
        pair_name = self.get_pair_name_from_contract(exchange, contract)
        from_block = self.db.get_latest_block_for_pair(pair_name, exchange)
        logger.info(f"Starting from block {from_block} for {pair_name} on {exchange}")
        if exchange == BANCOR_V2_NAME:
            return contract.events.TokenRateUpdate.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == BANCOR_V3_NAME:
            return contract.events.TradingLiquidityUpdated.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange in UNIV2_FORKS:
            return contract.events.Sync.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == UNISWAP_V3_NAME:
            return contract.events.Swap.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif CARBON_V1_NAME in exchange:
            return [
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.PoolCreated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyCreated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyDeleted.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyUpdated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "filter": contract.events.TokensTraded.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
            ]

    def _log_loop_noasync(self, exchange: str, _filter: LogFilter):
        """
        Polls for new events and processes them
        :param exchange: exchange name
        :param _filter: filter for the relevant event
        """
        # while True:
        for event in _filter.get_new_entries():
            try:
                self._handle_event(exchange=exchange, event_log=event)
            except Exception as e:
                logger.warning(
                    f"_log_loop: {exchange}, {_filter}, Failed to handle event: {e}"
                )

    async def _update_current_block(self):
        while True:
            self.current_block = w3.eth.blockNumber
            await asyncio.sleep(self.poll_interval)

    async def _get_log_loop_tasks(self, _exchange):
        """
        Polls for new events and processes them
        :param _exchange: exchange name
        """
        logger.debug(f"log loop tasks, exchange = {_exchange}")
        contract = self._get_contract_for_exchange(exchange=_exchange)
        while True:
            from_block = self.db.get_latest_block_for_exchange(_exchange)
            if from_block == self.current_block:
                await asyncio.sleep(self.poll_interval)
                continue
            logger.info(f"Starting from block {from_block} on {_exchange}")

            event_type = "None"
            events = []
            delete_events = []
            if _exchange == BANCOR_V3_NAME:
                events = contract.events.TradingLiquidityUpdated.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )

            elif CARBON_V1_NAME in _exchange:

                events += contract.events.StrategyCreated.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )
                delete_events += contract.events.StrategyDeleted.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )
                events += contract.events.StrategyUpdated.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )
                for event in delete_events:
                    logger.debug(
                        f"event = {event}, type = {event_type}, exchange = {_exchange}, from_block = {from_block}"
                    )
                    self._handle_event(
                        exchange=_exchange, event_log=event, event_type="delete"
                    )

            for event in events:
                logger.debug(
                    f"event = {event}, type = {event_type}, exchange = {_exchange}, from_block = {from_block}"
                )
                if event is None or len(event) == 0:
                    continue
                self._handle_event(exchange=_exchange, event_log=event)

            await asyncio.sleep(self.poll_interval)

    async def _log_loop(self, exchange: str, _filter: LogFilter):
        """
        Polls for new events and processes them
        :param exchange: exchange name
        :param _filter: filter for the relevant event
        """
        while True:
            for event in _filter.get_new_entries():
                try:
                    self._handle_event(exchange=exchange, event_log=event)
                except Exception as e:
                    logger.warning(
                        f"_log_loop: {exchange}, {_filter}, Failed to handle event: {e}"
                    )
            await asyncio.sleep(1)

    @staticmethod
    def stop():
        """
        Stops the event updater
        """
        w3.provider.disconnect()
        session.close()

    def __repr__(self):
        return f"EventUpdater({self.filters})"
