"""
Database manager object for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import Dict, List, Tuple

import brownie
import pandas as pd
from joblib import parallel_backend, Parallel, delayed
from sqlalchemy import func
from sqlalchemy.orm import Session

from carbon.abi import *
from carbon.models import *
from carbon.utils import initialize_contract


@dataclass
class DatabaseManager:
    """
    Factory class for creating and managing pools.

    backend: The database backend to use. (default: sqlite) (options are: sqlite, postgres)
    """

    backend: str = "sqlite"
    MULTICALL_CONTRACT_ADDRESS: str = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    drop_tables: bool = False
    use_multicall: bool = True

    _uniswap_v2_factory: Contract = None
    _uniswap_v3_factory: Any = None
    _bancor_v2_registry: Any = None
    _bancor_v3_collector: Any = None
    _carbon_v1_controller: Any = None

    def __post_init__(self):
        if self.drop_tables:
            self.drop_all_tables()

        try:
            self.create_ethereum_chain()
            self.create_supported_exchanges()
        except Exception as e:
            print(e)
            session.rollback()

        self.data = self.data.sort_values("exchange", ascending=False)

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
        self.update_pairs()
        self.update_tokens()
        self.update_exchanges()

    def drop_all_tables(self):
        """
        Drops all tables in the database
        """
        # Blockchain.__table__.drop(engine)
        # Exchange.__table__.drop(engine)
        # Token.__table__.drop(engine)
        # Pool.__table__.drop(engine)
        # Pair.__table__.drop(engine)
        # self.create_tables()
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

    def get_or_create_pool(
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
            logger.warning(e)

    @staticmethod
    def get_token_addresses_for_pool(
        exchange_name: str, pool_address: str, pool_contract: Contract
    ) -> Tuple[str, str]:
        """
        Gets the token addresses for a pool
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
            logger.warning(e)

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
    ) -> Dict[str, Any]:
        """
        Returns the common data for a pool
        """
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
            "last_updated_block": w3.eth.blockNumber,
        }

    def contract_from_address(self, exchange_name: str, pool_address: str) -> Contract:
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
        elif (exchange_name == BANCOR_V3_NAME) and not self.use_multicall:
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
        elif exchange_name == CARBON_V1_NAME:
            return initialize_contract(
                web3=w3,
                address=w3.toChecksumAddress(pool_address),
                abi=CARBON_CONTROLLER_ABI,
            )
        elif exchange_name == BANCOR_V3_NAME:
            return bancor_network_info
        else:
            raise NotImplementedError(f"Exchange {exchange_name} not implemented")

    @staticmethod
    def get_pool_fee_and_liquidity(
        exchange_name: str,
        pool_contract: Contract,
        tkn1_address: str,
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
            raise NotImplementedError

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
                        tkn0_address, tkn1_address = BNT_ADDRESS, pool_address
                        self.get_or_create_token(tkn0_address)
                        self.get_or_create_token(tkn1_address)
                        self.get_or_create_pair(tkn0_address, tkn1_address)
                        self.get_or_create_pool(
                            exchange_name=exchange, pool_address=pool_address
                        )
                except Exception as e:
                    logger.warning(e)
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
                logger.warning(e)
                continue
