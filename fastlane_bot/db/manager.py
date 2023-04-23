"""
Database manager object for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass, field, InitVar
from typing import Tuple, List, Dict, Any, Optional

import brownie
import pandas as pd
import sqlalchemy
from brownie import Contract
from joblib import parallel_backend, Parallel, delayed
from sqlalchemy import MetaData, func, text
from sqlalchemy.orm import Session, sessionmaker

from fastlane_bot.data.abi import BANCOR_V2_CONVERTER_ABI, BANCOR_V3_POOL_COLLECTION_ABI, UNISWAP_V2_POOL_ABI, \
    UNISWAP_V3_POOL_ABI, CARBON_CONTROLLER_ABI, ERC20_ABI
import fastlane_bot.db.models as models
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
from fastlane_bot.utils import initialize_contract
import fastlane_bot.config as c


@dataclass
class DatabaseManager:
    """
    Factory class for creating and managing pools.

    Parameters
    ----------
    session : Session
        The database session
    engine : sqlalchemy.engine
        The database engine
    metadata : MetaData
        The database metadata
    data : pd.DataFrame
        The dataframe containing the pools to add to the database

    """

    session: Session = field(init=False)
    engine: sqlalchemy.engine = field(init=False)
    metadata: MetaData = field(init=False)
    data: pd.DataFrame = field(default_factory=pd.DataFrame)
    backend_url: InitVar[str] = None

    def __post_init__(self, backend_url=None):
        self.data = pd.read_csv(c.DATABASE_SEED_FILE)
        self.data = self.data.sort_values("exchange", ascending=False)
        self.connect_db(backend_url=backend_url)

    def connect_db(self, *, backend_url=None):
        """
        Connects to the database. If the database does not exist, it creates it.
        """
        if backend_url is None:
            backend_url = c.DEFAULT_DB_BACKEND_URL
        self.metadata = sqlalchemy.MetaData()
        engine = sqlalchemy.create_engine(backend_url)
        models.mapper_registry.metadata.create_all(engine)
        sesh = sessionmaker(bind=engine)
        self.session = sesh()
        self.engine = engine

    def get_nonzero_liquidity_pools_and_tokens(self) -> List[PoolAndTokens]:
        """
        Returns all pools in the database.

        Returns
        -------
        List[PoolAndTokens]
            A list of PoolAndTokens objects containing the pool and token information.
        """
        raw_sql_query = text('''
                                WITH splits AS (
                                    SELECT *,
                                        split_part(pair_name, '/', 1) AS tkn0,
                                        split_part(pair_name, '/', 2) AS tkn1
                                    FROM pools
                                )
                                
                                SELECT
                                    splits.*,
                                    token0.address AS tkn0_address,
                                    token0.decimals AS tkn0_decimals,
                                    token1.address AS tkn1_address,
                                    token1.decimals AS tkn1_decimals
                                
                                FROM splits
                                    LEFT JOIN tokens AS token0 ON splits.tkn0 = token0."key"
                                    LEFT JOIN tokens AS token1 ON splits.tkn1 = token1."key";
                                ''')
        
        result_proxy= self.session.connection().execute(raw_sql_query)

        # Fetch the results from the executed query. Then add to a dictionary with the column names as keys.
        result = result_proxy.fetchall()
        columns = result_proxy.keys()
        pools_and_tokens = [PoolAndTokens(**dic) for dic in pd.DataFrame(result, columns=columns).to_dict(orient="records")]

        # Filter out pools with (tkn0_balance > 0 or tkn1_balance > 0 or liquidity > 0 or y_0 > 0)
        # Handle the case where the attribute is None type.
        pools_and_tokens = [pool for pool in pools_and_tokens if (
                (pool.tkn0_balance is not None and pool.tkn0_balance > 0) or
                (pool.tkn1_balance is not None and pool.tkn1_balance > 0) or
                (pool.liquidity is not None and pool.liquidity > 0) or
                (pool.y_0 is not None and pool.y_0 > 0)
        )]
        return pools_and_tokens

    def delete_all_carbon(self):
        """
        Deletes all the pools in the database
        """
        pool = self.session.query(models.Pool).filter(models.Pool.exchange_name == c.CARBON_V1_NAME).all()
        while len(pool) > 0:
            self.session.delete(pool[0])
            pool = (
                self.session.query(models.Pool).filter(models.Pool.exchange_name == c.CARBON_V1_NAME).all()
            )
        self.session.commit()

    def refresh_session(self):
        """
        Refreshes the database session
        """
        self.session.close()
        self.session = Session(self.engine)

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
        self.metadata.reflect(bind=self.engine)
        for table in reversed(self.metadata.sorted_tables):
            table.drop(bind=self.engine, checkfirst=False)
        self.create_tables()
        self.create_ethereum_chain()
        self.create_supported_exchanges()

    def create_supported_exchanges(self):
        """
        Creates the supported exchanges in the database
        """
        for exchange in c.SUPPORTED_EXCHANGES:
            self.session.add(models.Exchange(name=exchange, blockchain_name=c.ETHEREUM_BLOCKCHAIN_NAME))
        self.session.commit()

    def create_ethereum_chain(self):
        """
        Creates the Ethereum chain in the database
        """
        blockchain = models.Blockchain(name=c.ETHEREUM_BLOCKCHAIN_NAME)
        blockchain.block_number = c.w3.eth.blockNumber
        self.session.add(blockchain)
        self.session.commit()

    def create_tables(self):
        """
        Creates all tables in the database
        """
        models.mapper_registry.metadata.create_all(self.engine)

    @property
    def exchange_list(self) -> List[str]:
        """
        Returns the list of exchanges
        """
        return [x.name for x in self.session.query(models.Exchange).all()]

    def _get_next_value(self, attribute: str) -> int:
        """
        Returns the next value for the given attribute

        Parameters
        ----------
        attribute : str
            The attribute to get the next value for

        Returns
        -------
        int
            The next value for the given attribute

        """
        if attribute == 'cid':
            max_idxs = self.session.query(models.Pool).all()
            if not max_idxs:
                return 0
            max_idx = max(int(x.cid) for x in max_idxs)
        else:  # attribute == 'id'
            max_idx = self.session.query(func.max(getattr(models.Pool, attribute))).first()[0]

        return max_idx + 1 if max_idx is not None else 0

    @property
    def next_cid(self) -> int:
        """
        Returns the next cid
        """
        return self._get_next_value('cid')

    @property
    def next_id(self) -> int:
        """
        Returns the next id
        """
        return self._get_next_value('id')

    @property
    def bancor_v3_pool_list(self) -> List[Tuple[str, str]]:
        """
        Returns the list of Bancor V3 pools
        """
        return self.get_pool_lists()[2]

    def update_pools(self, drop_tables: bool = False):
        """
        Updates all pools. Used for testing in notebooks only. In production, use the run_events_update.py script.

        Parameters
        ----------
        drop_tables : bool
            Whether to drop all tables before updating pools
        """
        if drop_tables:
            self.drop_all_tables()

        self.update_all_carbon_strategies()

        self.update_liquidity_multicall(self.bancor_v3_pool_list)

        with parallel_backend("threading", n_jobs=1):
            Parallel()(
                delayed(self.update_pool)(exchange, pool_address)
                for exchange, pool_address in self.get_pool_lists()[1]
            )

    def update_pool(self, exchange_name: str, pool_address: str) -> Optional[models.Pool]:
        """
        Updates a pool in the database

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool
        """
        pool = self.get_pool_from_identifier(
            exchange_name=exchange_name, pool_identifier=pool_address
        )
        if not pool:
            return self.get_or_create_pool(exchange_name, pool_address)
        try:
            pool_contract = self.contract_from_address(exchange_name, pool_address)
            updated_params = self.get_pool_fee_and_liquidity(
                exchange_name, pool_contract, pool_address
            )
            self.session.query(models.Pool).filter(models.Pool.address == pool_address).first().update(updated_params)
            self.session.commit()
        except Exception as e:
            c.logger.warning(
                f"Failed to update pool for {exchange_name} {pool_address} {e}"
            )

    def get_pool_lists(self) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Returns a list of pools for each exchange

        Returns
        -------
        Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[Tuple[str, str]]]
            A tuple of lists of pools for each exchange
        """
        pools = list(self.data[["exchange", "address"]].values)

        v3_pools = [(ex, addr) for ex, addr in pools if ex == c.BANCOR_V3_NAME]
        carbon_pools = [(ex, addr) for ex, addr in pools if ex == c.CARBON_V1_NAME]
        other_pools = [(ex, addr) for ex, addr in pools if ex not in {c.BANCOR_V3_NAME, c.CARBON_V1_NAME}]

        return carbon_pools, other_pools, v3_pools

    @staticmethod
    def remove_eth_from_tokens(tokens: List[str]) -> List[str]:
        """
        Removes ETH from the list of tokens and adds it to the end of the list

        Parameters
        ----------
        tokens : List[str]
            The list of tokens to remove ETH from

        Returns
        -------
        List[str]
            The list of tokens with ETH removed
        """
        if c.WETH_ADDRESS in tokens:
            tokens.remove(c.WETH_ADDRESS)
        if c.ETH_ADDRESS not in tokens:
            tokens.append(c.ETH_ADDRESS)
        return tokens

    def address_to_key(self, address: str) -> str:
        """
        Converts an address to a key

        Parameters
        ----------
        address : str
            The address to convert

        Returns
        -------
        str
            The key for the address
        """
        return self.session.query(models.Token).filter(models.Token.address == address).first().key

    def _get_or_create_pool_noevents(
            self, exchange_name: str = None, pool_address: str = None
    ) -> models.Pool:
        """
        Creates a pool in the database. This method is slower because it calls contracts individually instead of using
        the events method. Used for testing in notebooks only. In production, use the run_events_update.py script.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool

        Returns
        -------
        models.Pool
            The created pool

        """
        try:
            pool_contract = self.contract_from_address(exchange_name, pool_address)
            tkn0_address, tkn1_address = self.get_token_addresses_for_pool(
                exchange_name, pool_address, pool_contract
            )
            tkn0 = self.get_or_create_token(tkn0_address)
            tkn1 = self.get_or_create_token(tkn1_address)
            pair = self.get_or_create_pair(tkn0_address, tkn1_address)
            common_data = dict(
                id=self.next_id,
                cid=str(self.next_cid),
                exchange_name=exchange_name,
                pair_name=pair.name,
                address=pool_address,
                tkn0_address=tkn0_address,
                tkn1_address=tkn1_address,
                tkn0_key=tkn0.key,
                tkn1_key=tkn1.key,
                last_updated_block=c.w3.eth.blockNumber
            )
            other_params = self.get_pool_fee_and_liquidity(
                exchange_name, pool_contract, tkn1_address
            )
            self.commit_pool(common_data, other_params)
            return self.session.query(models.Pool).filter(models.Pool.exchange_name == exchange_name,
                                                          models.Pool.address == pool_address).first()

        except Exception as e:
            c.logger.warning(
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
        if exchange_name == c.BANCOR_V3_NAME:
            tkn0_address = c.w3.toChecksumAddress(c.BNT_ADDRESS)
            tkn1_address = c.w3.toChecksumAddress(pool_address)
        else:
            try:
                tkn0_address = c.w3.toChecksumAddress(pool_contract.caller.token0())
                tkn1_address = c.w3.toChecksumAddress(pool_contract.caller.token1())
            except Exception as e:
                c.logger.debug(f"Error getting tokens for pool {pool_address} - {e}")
                reserve_tokens = pool_contract.caller.reserveTokens()
                tkn0_address = c.w3.toChecksumAddress(reserve_tokens[0])
                tkn1_address = c.w3.toChecksumAddress(reserve_tokens[1])
        return tkn0_address, tkn1_address

    def commit_pool(self, common_data: Dict[str, Any], other_params: Dict[str, Any]):
        """
        Commits a pool to the database

        Parameters
        ----------
        common_data : Dict[str, Any]
            The common data for the pool
        other_params : Dict[str, Any]
            The other parameters for the pool

        """
        pool_params = common_data | other_params
        try:
            pool = models.Pool(**pool_params)
            self.session.add(pool)
            self.session.commit()
        except Exception as e:
            c.logger.warning(
                f"Failed to commit pool pool_params={pool_params}, - {e}, {e.__traceback__}, rolling back..."
            )
            self.session.rollback()
            try:
                models.Pool(**pool_params)
                self.session.commit()
            except Exception as e:
                c.logger.warning(
                    f"Failed to commit pool pool_params={pool_params}, - {e}, {e.__traceback__}, skipping..."
                )

    @staticmethod
    def contract_from_address(exchange_name: str, pool_address: str) -> Contract:
        """
        Returns the contract for a given exchange and pool address

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool

        Returns
        -------
        Contract
            The contract for the pool

        """
        if exchange_name == c.BANCOR_V2_NAME:
            return initialize_contract(
                web3=c.w3,
                address=c.w3.toChecksumAddress(pool_address),
                abi=BANCOR_V2_CONVERTER_ABI,
            )
        elif exchange_name == c.BANCOR_V3_NAME:
            # return initialize_contract(
            #     web3=c.w3,
            #     address=c.w3.toChecksumAddress(pool_address),
            #     abi=BANCOR_V3_POOL_COLLECTION_ABI,
            # )
            return c.BANCOR_NETWORK_INFO_CONTRACT
        elif exchange_name in c.UNIV2_FORKS:
            return initialize_contract(
                web3=c.w3,
                address=c.w3.toChecksumAddress(pool_address),
                abi=UNISWAP_V2_POOL_ABI,
            )
        elif exchange_name == c.UNISWAP_V3_NAME:
            return initialize_contract(
                web3=c.w3,
                address=c.w3.toChecksumAddress(pool_address),
                abi=UNISWAP_V3_POOL_ABI,
            )
        elif c.CARBON_V1_NAME in exchange_name:
            return initialize_contract(
                web3=c.w3,
                address=c.w3.toChecksumAddress(pool_address),
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

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_contract : Contract
            The pool contract
        tkn1_address : str
            The address of the second token in the pair
        processed_event : Any, optional
            The processed event, by default None

        Returns
        -------
        Dict[str, Any]
            The pool info

        """
        if exchange_name == c.BANCOR_V3_NAME:
            pool_balances = pool_contract.tradingLiquidity(tkn1_address)
            if pool_balances:
                return {
                    "fee": "0.000",
                    "tkn0_balance": pool_balances[0],
                    "tkn1_balance": pool_balances[1],
                }
        elif exchange_name == c.BANCOR_V2_NAME:
            reserve0, reserve1 = pool_contract.caller.reserveBalances()
            return {
                "fee": pool_contract.caller.conversionFee(),
                "tkn0_balance": reserve0,
                "tkn1_balance": reserve1,
            }
        elif exchange_name == c.UNISWAP_V3_NAME:
            slot0 = pool_contract.caller.slot0()
            return {
                "tick": slot0[1],
                "sqrt_price_q96": slot0[0],
                "liquidity": pool_contract.caller.liquidity(),
                "fee": pool_contract.caller.fee(),
                "tick_spacing": pool_contract.caller.tickSpacing(),
            }
        elif exchange_name in c.UNIV2_FORKS:
            reserve_balance = pool_contract.caller.getReserves()
            return {
                "fee": "0.003",
                "tkn0_balance": reserve_balance[0],
                "tkn1_balance": reserve_balance[1],
            }
        elif exchange_name == c.CARBON_V1_NAME:
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

    def get_or_create_pair(self, tkn0_address: str, tkn1_address: str) -> models.Pair:
        """
        Adds pairs to the database

        Parameters
        ----------
        tkn0_address : str
            The address of the first token in the pair
        tkn1_address : str
            The address of the second token in the pair

        Returns
        -------
        models.Pair
            The pair object
        """
        tkn0_key = (
            self.session.query(models.Token).filter(models.Token.address == tkn0_address).first().key
        )
        tkn1_key = (
            self.session.query(models.Token).filter(models.Token.address == tkn1_address).first().key
        )
        pair_name = self.pair_name_from_token_keys(tkn0_key, tkn1_key)
        pair = self.session.query(models.Pair).filter(models.Pair.name == pair_name).first()
        if pair:
            return pair
        pair = models.Pair(
            name=pair_name,
            tkn0_key=tkn0_key,
            tkn1_key=tkn1_key,
            tkn0_address=tkn0_address,
            tkn1_address=tkn1_address,
        )
        self.session.add(pair)
        self.session.commit()
        return self.session.query(models.Pair).filter(models.Pair.name == pair_name).first()

    @staticmethod
    def pair_name_from_token_keys(tkn0_key: str, tkn1_key: str) -> str:
        """
        Creates a pair name from the token keys

        Parameters
        ----------
        tkn0_key : str
            The key of the first token in the pair
        tkn1_key : str
            The key of the second token in the pair

        Returns
        -------
        str
            The pair name
        """
        return f"{tkn0_key}/{tkn1_key}"

    @staticmethod
    def _initialize_token(address: str, symbol: str, decimals: int, name: str) -> models.Token:
        """
        Initializes a token object with the provided details

        Parameters
        ----------
        address : str
            The address of the token
        symbol : str
            The symbol of the token
        decimals : int
            The decimals of the token
        name : str
            The name of the token

        Returns
        -------
        models.Token
            The token object
        """
        return models.Token(symbol=symbol, address=address, decimals=decimals, name=name)

    def tkn_from_address(self, address: str) -> models.Token:
        """
        Creates a token object from an address

        Parameters
        ----------
        address : str
            The address of the token

        Returns
        -------
        models.Token
            The token object
        """
        address = c.w3.toChecksumAddress(address)
        tkn = self.session.query(models.Token).filter(models.Token.address == address).first()

        if tkn:
            return tkn

        known_tokens = {
            c.MKR_ADDRESS: {"symbol": "MKR", "decimals": 18, "name": "Maker"},
            c.ETH_ADDRESS: {"symbol": "ETH", "decimals": 18, "name": "Ethereum"},
        }

        if address in known_tokens:
            return self._initialize_token(address, **known_tokens[address])

        contract = initialize_contract(
            address=c.w3.toChecksumAddress(address), abi=ERC20_ABI, web3=c.w3
        )

        return self._initialize_token(
            address,
            symbol=contract.caller.symbol(),
            decimals=contract.caller.decimals(),
            name=contract.caller.name(),
        )

    def get_or_create_token(self, address: str) -> models.Token:
        """
        Gets or creates a token in the database

        Parameters
        ----------
        address : str
            The address of the token

        Returns
        -------
        models.Token
            The token object

        """
        tkn = self.session.query(models.Token).filter(models.Token.address == address).first()
        if tkn:
            return tkn
        tkn = self.tkn_from_address(address)
        tkn_symbol = tkn.symbol
        tkn_address = tkn.address
        tkn_key = self.token_key_from_symbol_and_address(tkn_address, tkn_symbol)
        tkn.key = tkn_key
        self.session.add(tkn)
        self.session.commit()
        return tkn

    def token_key_from_symbol_and_address(self, tkn_address: str, tkn_symbol: str) -> str:
        """
        Creates a token key from the token address and symbol. Uses "symbol-[last 4 characters of the address]".

        Parameters
        ----------
        tkn_address : str
            The address of the token
        tkn_symbol : str
            The symbol of the token

        Returns
        -------
        str
            The token key
        """
        return f"{tkn_symbol}-{tkn_address[-4:]}"

    def get_lastest_block_for_blockchain(self, name: str) -> Optional[models.Blockchain]:
        """
        Get the last block from which we collected 0.0-data-archive. This can be used to check the starting point from where we should gather 0.0-data-archive.

        Parameters
        ----------
        name : str
            The name of the blockchain

        Returns
        -------
        Optional[models.Blockchain]
            The last block from which we collected 0.0-data-archive
        """
        try:
            return self.session.query(models.Blockchain).filter(models.Blockchain.name == name).last_block
        except AttributeError:
            c.logger.error(f"Could not find last block for {name}")
            return None

    def get_latest_block_for_pair(self, pair_name: str, exchange_name: str) -> int or str:
        """
        Get the last block from which we collected 0.0-data-archive for a specific token pair on a specific exchange.

        Parameters
        ----------
        pair_name : str
            The name of the token pair
        exchange_name : str
            The name of the exchange

        Returns
        -------
        int or str
            The last block from which we collected 0.0-data-archive

        """
        try:
            return (
                self.session.query(models.Pool)
                .filter(
                    models.Pool.pair_name == pair_name, models.Pool.exchange_name == exchange_name
                )
                .first()
                .last_updated_block
            )
        except AttributeError:
            return "latest"

    def get_pool_by_address(self, address: str) -> models.Pool:
        """
        Get a pool by address.

        Parameters
        ----------
        address : str
            The address of the pool

        Returns
        -------
        models.Pool
            The pool object

        """
        return self.session.query(models.Pool).filter(models.Pool.address == address).first()

    def update_liquidity_multicall(
            self, pools: List[Tuple[str, str]]
    ):
        """
        Setup Bancor V3 pools with multicall to improve efficiency

        Parameters
        ----------
        pools : List[Tuple[str, str]]
            A list of pools to update
        contract : Contract
            The contract to use for the multicall


        """
        if not pools:
            return
        with brownie.multicall(address=c.MULTICALL_CONTRACT_ADDRESS):
            for exchange, pool_address in pools:

                try:
                    p = (
                        self.session.query(models.Pool)
                        .filter(
                            models.Pool.address == pool_address, models.Pool.exchange_name == exchange
                        )
                        .first()
                    )
                    if p:
                        continue

                    if exchange == c.BANCOR_V3_NAME:

                        tkn0_address, tkn1_address = c.BNT_ADDRESS, pool_address
                        self.get_or_create_token(tkn0_address)
                        self.get_or_create_token(tkn1_address)
                        self.get_or_create_pair(tkn0_address, tkn1_address)
                        self.get_or_create_pool(
                            exchange_name=exchange,
                            pool_identifier=pool_address,
                            processed_event=None,
                        )
                except Exception as e:
                    c.logger.warning(
                        f"Error updating pool {pool_address} on {exchange}, {e}, continuing..."
                    )
                    continue

    @staticmethod
    def get_carbon_pairs() -> List[Tuple[str, str]]:
        """
        Returns a list of all Carbon token pairs

        Returns
        -------
        List[Tuple[str, str]]
            A list of all Carbon token pairs

        """
        return c.CARBON_CONTROLLER_CONTRACT.pairs()

    @staticmethod
    def get_carbon_strategy(strategy_id: int) -> Tuple[str, str, str, str, str, str, str]:
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
        return c.CARBON_CONTROLLER_CONTRACT.strategy(strategy_id)

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
        return c.CARBON_CONTROLLER_CONTRACT.strategiesByPairCount(token0, token1)

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
        return c.CARBON_CONTROLLER_CONTRACT.strategiesByPair(token0, token1, start_idx, end_idx)

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

    def get_all_carbon_strategies(self):
        """
        Gets every Carbon Strategy
        """
        all_pairs = self.get_carbon_pairs()
        with brownie.multicall(address=c.MULTICALL_CONTRACT_ADDRESS):
            strats = [strategy for pair in all_pairs for strategy in self.get_strategies(pair)]

        return strats

    def update_all_carbon_strategies(self):
        """
        Finds and updates all Carbon strategies
        """
        all_strategies = self.get_all_carbon_strategies()
        self.update_raw_carbon_strategies(strategies=all_strategies)

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
        return (seq[pos: pos + size] for pos in range(0, len(seq), size))

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
        for group in self.chunker(strategy_ids, c.CARBON_STRATEGY_CHUNK_SIZE):
            with brownie.multicall(address=c.MULTICALL_CONTRACT_ADDRESS):
                strategies += [
                    self.get_carbon_strategy(strat_id[0]) for strat_id in group
                ]
        return strategies


    def update_raw_carbon_strategies(self, strategies: List[int], last_updated_block: int = None):
        """
        Takes a list of Carbon Strategies in the raw contract format, processes them, and inserts them into the database.

        Parameters
        ----------
        strategies : List[Any]
            A list of raw Carbon strategies
        last_updated_block : int, optional
            The last block that was updated, by default None

        """
        for strategy in strategies:
            try:
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
                tkn0_address = c.w3.toChecksumAddress(tkn0_address)
                tkn1_address = c.w3.toChecksumAddress(tkn1_address)
                tkn0 = self.get_or_create_token(tkn0_address)
                tkn1 = self.get_or_create_token(tkn1_address)
                pair = self.get_or_create_pair(tkn0_address, tkn1_address)
                if last_updated_block is None:
                    last_updated_block = c.w3.eth.blockNumber
                common_data = dict(
                    id=self.next_id,
                    cid=strategy_id,
                    exchange_name=c.CARBON_V1_NAME,
                    pair_name=pair.name,
                    address=c.CARBON_CONTROLLER_ADDRESS,
                    tkn0_address=tkn0_address,
                    tkn1_address=tkn1_address,
                    tkn0_key=tkn0.key,
                    tkn1_key=tkn1.key,
                    last_updated_block=last_updated_block,
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
                c.logger.error(f"Error updating Carbon strategy {strategy} [{e}]")
                continue

    def get_latest_block_for_exchange(self, exchange_name: str) -> int or str:
        """
        Get the last block from which we collected 0.0-data-archive for a specific exchange.


        Parameters
        ----------
        exchange_name : str
            The name of the exchange

        Returns
        -------
        int or str
            The last block from which we collected 0.0-data-archive for a specific exchange.
        """
        try:
            return self.session.query(models.Exchange).filter(
                models.Exchange.exchange_name == exchange_name).first().last_updated_block
        except AttributeError:
            return "latest"

    def get_pool_from_identifier(
            self, exchange_name: str = None, pool_identifier: Any = None
    ) -> Optional[models.Pool or None]:
        """
        Gets a Pool object using different identifiers. For Carbon, it uses the pool's CID. For Bancor V3, it uses TKN 1 address.
        For other exchanges, it uses the liquidity pool address.

        Parameters
        ----------
        exchange_name : str, optional
            The name of the exchange, by default None
        pool_identifier : Any, optional
            The identifier of the pool, by default None

        Returns
        -------
        Optional[models.Pool or None]
            The Pool object

        """
        if not isinstance(pool_identifier, str):
            pool_identifier = str(pool_identifier)

        if exchange_name == c.BANCOR_V3_NAME:
            return (
                self.session.query(models.Pool)
                .filter(
                    models.Pool.exchange_name == c.BANCOR_V3_NAME,
                    models.Pool.tkn1_address == pool_identifier,
                )
                .first()
            )
        elif c.CARBON_V1_NAME in exchange_name:
            return self.session.query(models.Pool).filter(models.Pool.cid == pool_identifier).first()
        else:
            return self.session.query(models.Pool).filter(models.Pool.address == pool_identifier).first()

    def get_or_create_pool(self, exchange_name: str = None, pool_identifier: str = None,
                            processed_event: Dict[str, Any] = None) -> models.Pool:
        """
        Creates a pool in the database

        Parameters
        ----------
        exchange_name : str, optional
            The name of the exchange, by default None
        pool_identifier : str, optional
            The identifier of the pool, by default None
        processed_event : Dict[str, Any], optional
            The processed event, by default None

        Returns
        -------
        models.Pool
            The Pool object

        """
        if processed_event is None:
            return self._get_or_create_pool_noevents(exchange_name, pool_identifier)

        return self.get_pool_from_identifier(
            exchange_name=exchange_name, pool_identifier=pool_identifier
        )


    def _rollback_and_log(self, e: Exception):
        """
        Rollbacks the session and logs the error

        Parameters
        ----------
        e : Exception
            The exception
        """
        self.session.rollback()
        c.logger.warning("[_rollback_and_log] {e}")


    def get_pool_from_exchange_and_token_keys(self, other_token: str, src_token: str, exchange_name: str) -> Optional[models.Pool]:
        """
        Gets the pool from the exchange and token keys

        Parameters
        ----------
        other_token : str
            The other token
        src_token : str
            The source token
        exchange_name : str
            The exchange name

        Returns
        -------
        Optional[models.Pool]
            The pool
        """
        return (
            self.session.query(models.Pool)
            .filter(
                models.Pool.exchange_name == exchange_name,
                models.Pool.tkn1_key == src_token,
                models.Pool.tkn0_key == other_token,
            )
            .first()
        )

    def get_nonzero_liquidity_pools(self):
        return (
            self.session.query(models.Pool)
            .filter(
                (models.Pool.tkn0_balance > 0)
                | (models.Pool.tkn1_balance > 0)
                | (models.Pool.liquidity > 0)
                | (models.Pool.y_0 > 0)
            )
            .all()
        )

    def get_token_address_from_token_key(self, tkn_key: str) -> str:
        """
        Gets the token address from the token key

        Parameters
        ----------
        tkn_key : str
            The token key

        Returns
        -------
        str
            The token address
        """
        return self.session.query(models.Token).filter(models.Token.key == tkn_key).first().address


    @staticmethod
    def get_pool_fee(
            exchange_name: str,
            pool_contract: Contract,
    ) -> str:
        """
        Gets the pool info for a given pair of tokens in a given exchange

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_contract : Contract
            The pool contract

        Returns
        -------
        str
            The pool fee
        """
        if exchange_name == c.BANCOR_V3_NAME:
            return "0.000"
        elif exchange_name == c.BANCOR_V2_NAME:
            return str(pool_contract.caller.conversionFee())
        elif exchange_name == c.UNISWAP_V3_NAME:
            return str(pool_contract.caller.fee())
        elif exchange_name in c.UNIV2_FORKS:
            return "0.003"
        elif c.CARBON_V1_NAME in exchange_name:
            return "0.002"

    def _add_or_update(self, block_number: int, cid: int, pool: models.Pool):
        """
        Adds or updates a pool

        Parameters
        ----------
        block_number : int
            The block number
        cid : int
            The cid
        pool : models.Pool
            The pool

        """
        is_created = self.session.query(models.Pool).filter(models.Pool.cid == cid).first()
        if not is_created:
            self.session.add(pool)
        self.session.commit()
        c.logger.info(
            f"Successfully updated event for cid={cid} {pool.pair_name} {pool.fee} at block {block_number}..."
        )

    def delete_carbon_strategy(self, strategy_id: int):
        """
        Deletes the specified Carbon Strategy

        Parameters
        ----------
        strategy_id : int
            The id of the strategy to delete
        """
        strategy = self.session.query(models.Pool).filter(models.Pool.cid == strategy_id).first()
        self.session.delete(strategy)
        self.session.commit()
