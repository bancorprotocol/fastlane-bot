"""
Main DB manager of the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import Any, Dict, Type, Optional, Tuple, List

import brownie
from _decimal import Decimal
from brownie import Contract
from sqlalchemy import or_

from fastlane_bot.db.model_managers import PoolManager, TokenManager, PairManager
import fastlane_bot.db.models as models

import fastlane_bot.data.abi as _abi
from fastlane_bot.config import Config


class DatabaseManager(PoolManager, TokenManager, PairManager):
    """
    DatabaseManager class that inherits from PoolManager, TokenManager, and PairManager
    and provides methods to update the database from events.
    """

    __VERSION__ = "3.0.4"
    __DATE__ = "May-02-2023"

    ConfigObj: Config = None

    c = ConfigObj

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

    def create(self, obj: models.Exchange or models.Blockchain):
        """
        Creates an obj in the database

        Parameters
        ----------
        obj : models.Exchange or models.Blockchain
        """
        self.session.add(obj)
        self.session.commit()

    def create_tables(self):
        """
        Creates all tables in the database
        """
        models.mapper_registry.metadata.create_all(self.engine)

    def create_ethereum_chain(self):
        """
        Creates the Ethereum chain in the database
        """
        blockchain = models.Blockchain(name="Ethereum")  # TODO: blockchain_name="Ethereum" should be a config constant
        blockchain.block_number = self.ConfigObj.w3.eth.blockNumber
        self.session.add(blockchain)
        self.session.commit()

    def create_supported_exchanges(self):
        """
        Creates the supported exchanges in the database
        """
        for exchange in self.ConfigObj.SUPPORTED_EXCHANGES:
            self.session.add(models.Exchange(name=exchange,
                                             blockchain_name="Ethereum"))  # TODO: blockchain_name="Ethereum" should be a config constant
        self.session.commit()

    def update_pools_from_contracts(self, only_carbon: bool = False, top_n: int = None):
        """
        For exchange in supported exchanges,
        get the available pool addresses and contracts
        then call update_pool_from_contract

        Parameters
        ----------
        only_carbon : bool
            Whether to only update carbon pools
        top_n : int
            The number of pools to update

        Returns
        -------
        List[models.Pool]
            The updated pools


        """
        pools = self.session.query(models.Pool).first()
        carbon_tokens = None

        if only_carbon:
            carbon_tokens = self.get_carbon_pairs()

            # Convert list of tuples to list of strings
            carbon_tokens = [token[0] for token in carbon_tokens] + [token[1] for token in carbon_tokens]

        if not pools:
            return self.create_pools_from_contracts(only_carbon=only_carbon, top_n=top_n, carbon_tokens=carbon_tokens)

        for exchange in self.ConfigObj.SUPPORTED_EXCHANGES:
            pools = self.get_pools_from_exchange(exchange, only_carbon=only_carbon, top_n=top_n,
                                                 carbon_tokens=carbon_tokens)
            for pool in pools:
                if pool.exchange_name == exchange:
                    contract = self.get_or_init_contract(exchange_name=exchange, pool_address=pool.address)
                    if pool.exchange_name == self.ConfigObj.CARBON_V1_NAME:
                        strategy = self.get_carbon_strategy(int(pool.cid))
                    else:
                        strategy = None
                    self.update_pool_from_contract(pool=pool, contract=contract, address=pool.address,
                                                   strategy=strategy)

    def update_pool_from_event(self, pool: models.Pool, processed_event: Any):
        """
        Updates the database from an event.

        Parameters
        ----------
        pool : models.Pool
            The pool to update.
        processed_event : Any
            The event to update from.
        """
        if pool.exchange_name == self.ConfigObj.BANCOR_V3_NAME:
            self.update_pool({
                                 "cid": pool.cid,
                                 "last_updated_block": processed_event["block_number"],
                                 "tkn0_balance": processed_event["newLiquidity"]
                             } if processed_event["token"] == self.ConfigObj.BNT_ADDRESS else {
                "cid": pool.cid,
                "tkn1_balance": processed_event["newLiquidity"],
            })

        elif pool.exchange_name == self.ConfigObj.UNISWAP_V3_NAME:
            self.update_pool({
                "cid": pool.cid,
                "last_updated_block": processed_event["block_number"],
                "sqrt_price_q96": processed_event["sqrt_price_q96"],
                "liquidity": processed_event["liquidity"],
                "tick": processed_event["tick"],
            })

        elif pool.exchange_name in self.ConfigObj.UNIV2_FORKS + [self.ConfigObj.BANCOR_V2_NAME]:
            self.update_pool({
                "cid": pool.cid,
                "last_updated_block": processed_event["block_number"],
                "tkn0_balance": processed_event["tkn0_balance"],
                "tkn1_balance": processed_event["tkn1_balance"],
            })

        elif self.ConfigObj.CARBON_V1_NAME in pool.exchange_name:
            self.update_pool({
                "cid": pool.cid,
                "last_updated_block": processed_event["block_number"],
                "y_0": processed_event["order0"][0],
                "z_0": processed_event["order0"][1],
                "A_0": processed_event["order0"][2],
                "B_0": processed_event["order0"][3],
                "y_1": processed_event["order1"][0],
                "z_1": processed_event["order1"][1],
                "A_1": processed_event["order1"][2],
                "B_1": processed_event["order1"][3],
            })
        else:
            raise ValueError(f"[DatabaseManager.update_from_event] Unknown exchange {pool.exchange_name}")

    def update_pool_from_contract(self,
                                  pool: models.Pool or Type[models.Pool],
                                  contract: Contract,
                                  strategy: Optional[Any] = None,
                                  address: Optional[str] = None):
        """
        Updates a pool with the provided strategy.

        Parameters
        ----------
        pool : models.Pool
            The pool object
        contract : Contract
            The contract object
        strategy : Any
            The strategy object
        address : str
            The address of the pool

        """
        common_params = {
            "cid": pool.cid,
            "last_updated_block": self.ConfigObj.w3.eth.block_number,
        }
        liquidity_params = self.get_liquidity_from_contract(exchange_name=pool.exchange_name,
                                                            contract=contract,
                                                            address=address,
                                                            strategy=strategy)
        update_params = {**common_params, **liquidity_params}
        self.update_pool(update_params)

    def get_liquidity_from_contract(self,
                                    exchange_name: str,
                                    contract: Contract,
                                    strategy: Optional[Any] = None,
                                    address: Optional[str] = None):
        """
        Updates a pool with the provided strategy.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        contract : Contract
            The contract object
        strategy : Any
            The strategy object
        address : str
            The address of the pool


        """
        params = {}
        if exchange_name == self.ConfigObj.BANCOR_V3_NAME:
            pool_balances = contract.tradingLiquidity(address)
            params = {
                "fee": "0.000",
                "tkn0_balance": pool_balances[0],
                "tkn1_balance": pool_balances[1],
            }
        elif exchange_name == self.ConfigObj.BANCOR_V2_NAME:
            reserve0, reserve1 = contract.caller.reserveBalances()
            params = {
                "fee": "0.003",
                "tkn0_balance": reserve0,
                "tkn1_balance": reserve1,
            }
        elif exchange_name == self.ConfigObj.UNISWAP_V3_NAME:
            slot0 = contract.caller.slot0()
            params = {
                "tick": slot0[1],
                "sqrt_price_q96": slot0[0],
                "liquidity": contract.caller.liquidity(),
                "fee": contract.caller.fee(),
                "tick_spacing": contract.caller.tickSpacing(),
            }

        elif exchange_name in self.ConfigObj.UNIV2_FORKS:
            reserve_balance = contract.caller.getReserves()
            params = {
                "fee": "0.003",
                "tkn0_balance": reserve_balance[0],
                "tkn1_balance": reserve_balance[1],
            }
        elif self.ConfigObj.CARBON_V1_NAME in exchange_name:
            order0, order1 = strategy[3][0], strategy[3][1]
            params = {
                "fee": "0.000",
                "y_0": order0[0],
                "z_0": order0[1],
                "A_0": order0[2],
                "B_0": order0[3],
                "y_1": order1[0],
                "z_1": order1[1],
                "A_1": order1[2],
                "B_1": order1[3],
            }
        return params

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
        token = self.get_token(address=address)
        if token is None:
            try:
                known_tokens = {
                    self.c.MKR_ADDRESS: {"symbol": "MKR", "decimals": 18, "name": "Maker"},
                    self.c.ETH_ADDRESS: {"symbol": "ETH", "decimals": 18, "name": "Ethereum"},
                }
                if address in known_tokens:
                    tkn = known_tokens[address]
                    token = models.Token(address=address, name=tkn["name"], symbol=tkn["symbol"],
                                         decimals=tkn["decimals"], key=f"{tkn['symbol']}-{address[-4:]}")
                    self.create_token(token)
                    return token

                contract = self.ConfigObj.w3.eth.contract(address=address, abi=_abi.ERC20_ABI)
                symbol = contract.caller.symbol()
                tkn_key = f"{symbol}-{address[-4:]}"
                token = models.Token(address=address, name=contract.caller.name(), symbol=symbol,
                                     decimals=contract.caller.decimals(), key=tkn_key)
                self.create_token(token)
            except Exception as e:
                self.c.logger.error(f"[DatabaseManager.get_or_create_token] {e}")
        return token

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
        pair = self.get_pair(tkn0_address=tkn0_address, tkn1_address=tkn1_address)
        if pair is None:
            try:
                tkn0 = self.get_or_create_token(address=tkn0_address)
                tkn0_key = tkn0.key
                tkn1 = self.get_or_create_token(address=tkn1_address)
                tkn1_key = tkn1.key
                pair = models.Pair(tkn0_address=tkn0_address, tkn1_address=tkn1_address, name=f"{tkn0_key}/{tkn1_key}",
                                   tkn0_key=tkn0_key, tkn1_key=tkn1_key)
                self.create_pair(pair)
            except Exception as e:
                self.c.logger.error(f"[DatabaseManager.get_or_create_pair] {e}")

        return pair

    # @staticmethod
    def get_token_addresses_for_pool(self,
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
        if exchange_name == self.ConfigObj.BANCOR_V3_NAME:
            tkn0_address = self.ConfigObj.w3.toChecksumAddress(self.ConfigObj.BNT_ADDRESS)
            tkn1_address = self.ConfigObj.w3.toChecksumAddress(pool_address)
        elif exchange_name == self.ConfigObj.BANCOR_V2_NAME:
            reserve_tokens = pool_contract.caller.reserveTokens()
            tkn0_address = self.ConfigObj.w3.toChecksumAddress(reserve_tokens[0])
            tkn1_address = self.ConfigObj.w3.toChecksumAddress(reserve_tokens[1])
        else:
            tkn0_address = self.ConfigObj.w3.toChecksumAddress(pool_contract.caller.token0())
            tkn1_address = self.ConfigObj.w3.toChecksumAddress(pool_contract.caller.token1())
        return tkn0_address, tkn1_address

    def create_pool_from_contract(self, exchange_name: str, pool_address: str,
                                  strategy: Optional[Tuple[str, str, str, Any]] = None):
        """
        Creates a pool with the provided strategy.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool
        strategy : Tuple[str, str, str, Any]
            The strategy for the pool

        """
        cid = self.next_cid if strategy is None else str(strategy[0])
        contract = self.contract_from_address(exchange_name=exchange_name, pool_address=pool_address)
        common_params = {
            "cid": cid,
            "last_updated_block": self.ConfigObj.w3.eth.block_number,
            "exchange_name": exchange_name,
            "address": pool_address,
        }
        liquidity_params = self.get_liquidity_from_contract(exchange_name=exchange_name,
                                                            contract=contract,
                                                            address=pool_address,
                                                            strategy=strategy)
        params = {**common_params, **liquidity_params}
        if strategy is not None:
            tkn0_address, tkn1_address = strategy[2][0], strategy[2][1]
        else:
            tkn0_address, tkn1_address = self.get_token_addresses_for_pool(
                exchange_name, pool_address, contract
            )

        tkn0 = self.get_or_create_token(tkn0_address)
        tkn1 = self.get_or_create_token(tkn1_address)
        pair = self.get_or_create_pair(tkn0_address, tkn1_address)

        tkn0_key, tkn1_key = tkn0.key, tkn1.key
        other_params = {
            "tkn0_key": tkn0_key,
            "tkn1_key": tkn1_key,
            "pair_name": pair.name,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
        }
        pool_params = {**params, **other_params}
        self.create_pool(pool_params)

    def update_recently_traded_pools(self, cids: List[int]):
        """
        Updates the recently traded pools

        Parameters
        ----------
        cids : List[int]
            The cids
        """
        self.recently_traded_pools = [self.get_pool(cid=cid) for cid in cids]

        tuples = [(pool.exchange_name, pool.address) for pool in self.recently_traded_pools]
        for exchange_name, pool_address in tuples:
            pool_contract = self.contract_from_address(exchange_name=exchange_name, pool_address=pool_address)
            self.update_pool(exchange_name, pool_address, pool_contract)

    def get_bnt_price_from_tokens(self, price, tkn) -> Decimal:
        """
        Gets the price of a token

        Parameters
        ----------
        tkn0 : str
            The token address
        tkn1 : str
            The token address

        Returns
        -------
        Optional[Decimal]
            The price
        """

        if tkn == 'BNT-FF1C':
            return Decimal(price)

        bnt_price_map_symbols = {token.split('-')[0]: self.bnt_price_map[token] for token in self.bnt_price_map}

        tkn_bnt_price = bnt_price_map_symbols.get(tkn.split('-')[0])

        if tkn_bnt_price is None:
            raise ValueError(f"Missing TKN/BNT price for {tkn}")

        return Decimal(price) * Decimal(tkn_bnt_price)

    def get_genesis_pool_addresses_from_exchange(self, exchange: str, only_carbon: bool = False, top_n: int = None,
                                                 carbon_tokens: List[str] = None) -> List[str]:
        """
        Gets the genesis pools for an exchange

        Parameters
        ----------
        exchange : str
            The exchange name
        top_n : int
            The number of pools to return
        only_carbon : bool
            Whether to only return carbon pools and other exchange compatible pools
        carbon_tokens : List[str]
            The carbon tokens to use

        Returns
        -------
        List[models.Pool]
            The genesis pools
        """
        if only_carbon:
            token_symbols = []
            for tkn in carbon_tokens:
                print(f"Getting or creating carbon_tokens {tkn}")
                tkn_obj = self.get_or_create_token(tkn)
                print(f"Getting or creating carbon_tokens {tkn_obj.symbol}")
                token_symbols.append(tkn_obj.symbol)

            # Filter the df to only include carbon tokens on the given exchange
            return self.data[(self.data['exchange'] == exchange) & (
                        self.data['tkn0_symbol'].isin(token_symbols) | self.data['tkn1_symbol'].isin(token_symbols))][
                'address'].unique().tolist()

        if top_n is None:
            return self.data[self.data['exchange'] == exchange]['address'].unique().tolist()
        else:
            return self.data[self.data['exchange'] == exchange]['address'].unique().tolist()[:top_n]

    def get_pools_from_exchange(self, exchange: str, only_carbon: bool = False, top_n: int = None,
                                carbon_tokens: List[str] = None) -> List[models.Pool]:
        """
        Gets the pools for an exchange

        Parameters
        ----------
        exchange : str
            The exchange name
        top_n : int
            The number of pools to return
        only_carbon : bool
            Whether to only return carbon pools and other exchange compatible pools

        Returns
        -------
        List[models.Pool]
            The pools
        """
        if only_carbon:
            # Get all pools on the given exchange
            exchange_pools = self.session.query(models.Pool).filter(models.Pool.exchange_name == exchange).all()
            exchange_pairs = [pool.pair_name for pool in exchange_pools]
            exchange_pairs = self.session.query(models.Pair).filter(models.Pair.name.in_(exchange_pairs)).all()

            # Filter the pairs which contain carbon at least one carbon token
            exchange_pairs = [pair for pair in exchange_pairs if
                              pair.tkn0_address in carbon_tokens or pair.tkn1_address in carbon_tokens]

            # Return the pools which contain at least one carbon token
            return [pool for pool in exchange_pools if pool.pair_name in [pair.name for pair in exchange_pairs]]

        if top_n is None:
            return self.session.query(models.Pool).filter(models.Pool.exchange_name == exchange).all()
        else:
            return self.session.query(models.Pool).filter(models.Pool.exchange_name == exchange).limit(top_n).all()

    def create_pools_from_contracts(self, only_carbon: bool = None, top_n: int = None, carbon_tokens: List[str] = None):
        """
        Creates pools from contracts

        Parameters
        ----------
        only_carbon : bool
            Whether to only create carbon pools and other exchange compatible pools
        top_n : int
            The number of pools to create
        carbon_tokens : List[str]
            The carbon tokens to create pools for


        """
        for exchange in self.ConfigObj.SUPPORTED_EXCHANGES:
            # try:
            if exchange == self.ConfigObj.CARBON_V1_NAME:
                self.create_or_update_carbon_pools()
                continue

            pool_addresses = self.get_genesis_pool_addresses_from_exchange(exchange, only_carbon=only_carbon,
                                                                           top_n=top_n, carbon_tokens=carbon_tokens)
            assert type(pool_addresses[0]) == str, f"Pool addresses must be strings, not {type(pool_addresses[0])}"

            if exchange == self.ConfigObj.BANCOR_V3_NAME:
                contract = self.c.BANCOR_NETWORK_INFO_CONTRACT
                pools = [(exchange, address, contract) for address in pool_addresses]
                self.create_or_update_pool_with_multicall(pools=pools)
                continue

            for address in pool_addresses:
                self.create_pool_from_contract(exchange_name=exchange, pool_address=address)

            # except Exception as e:
            #     self.c.logger.error(
            #         f"[manager.create_pools_from_contracts] Error creating pool {exchange} {address} [{e}]")
            #     continue

    def create_or_update_carbon_pools(self, pools: List[Any] = None):
        """
        Takes a list of Carbon Strategies in the raw contract format, processes them, and inserts them into the database.

        Parameters
        ----------
        pools : List[Any]
            A list of raw Carbon strategies

        """
        if pools is None:
            pools = self.get_carbon_strategies()

        last_updated_block = self.c.w3.eth.blockNumber
        for strategy in pools:
            strategy_id = str(strategy[0])
            pool = self.get_pool(cid=strategy_id)
            if pool:
                try:
                    self.update_carbon_pool(strategy, last_updated_block)
                except Exception as e:
                    self.c.logger.error(f"[manager.create_or_update_carbon_pools] Error updating Carbon strategy [{e}]")
                    continue
            else:
                try:
                    self.create_carbon_pool(strategy, last_updated_block)
                except Exception as e:
                    self.c.logger.error(
                        f"[manager.create_or_update_carbon_pools] Error creating Carbon strategy {strategy} [{e}]")
                    continue

    def update_carbon_pool(self, strategy: Any, last_updated_block: int):
        """
        Updates a pool with the provided strategy.

        Parameters
        ----------
        strategy : Any
            The strategy object
        last_updated_block : int
            The last block from which we collected 0.0-data-archive

        """
        order0, order1 = strategy[3][0], strategy[3][1]
        updated_params = {
            "y_0": order0[0],
            "z_0": order0[1],
            "A_0": order0[2],
            "B_0": order0[3],
            "y_1": order1[0],
            "z_1": order1[1],
            "A_1": order1[2],
            "B_1": order1[3],
            "last_updated_block": last_updated_block
        }
        self.update_pool(updated_params)

    def create_carbon_pool(self, strategy: Any, last_updated_block: int):
        """
        Creates a pool with the provided strategy.

        Parameters
        ----------
        strategy : Any
            The strategy object
        last_updated_block : int
            The last block from which we collected 0.0-data-archive

        """

        strategy_id = str(strategy[0])
        tkn0_address, tkn1_address = strategy[2][0], strategy[2][1]
        tkn0_key, tkn1_key = self.get_or_create_token(address=tkn0_address).key, self.get_or_create_token(
            address=tkn1_address).key
        order0, order1 = strategy[3][0], strategy[3][1]
        pair = self.get_or_create_pair(tkn0_address, tkn1_address)
        pool_params = {
            # "id": self.next_id,
            "cid": strategy_id,
            "exchange_name": self.c.CARBON_V1_NAME,
            "tkn0_key": tkn0_key,
            "tkn1_key": tkn1_key,
            "pair_name": pair.name,
            "address": self.c.CARBON_CONTROLLER_ADDRESS,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
            "y_0": order0[0],
            "z_0": order0[1],
            "A_0": order0[2],
            "B_0": order0[3],
            "y_1": order1[0],
            "z_1": order1[1],
            "A_1": order1[2],
            "B_1": order1[3],
            "last_updated_block": last_updated_block
        }
        self.create_pool(pool_params)

    def build_pool_params(
            self, exchange_name: str = None, pool_address: str = None, pool_contract: Contract = None
    ) -> Dict[str, Any]:
        """
        Builds the parameters needed to create a pool.

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
            if not pool_contract:
                pool_contract = self.contract_from_address(exchange_name=exchange_name, pool_address=pool_address)
            tkn0_address, tkn1_address = self.get_token_addresses_for_pool(
                exchange_name, pool_address, pool_contract
            )
            tkn0 = self.get_or_create_token(tkn0_address)
            tkn1 = self.get_or_create_token(tkn1_address)
            pair = self.get_or_create_pair(tkn0_address, tkn1_address)
            common_data = dict(
                cid=str(self.next_cid),
                exchange_name=exchange_name,
                pair_name=pair.name,
                address=pool_address,
                tkn0_address=tkn0_address,
                tkn1_address=tkn1_address,
                tkn0_key=tkn0.key,
                tkn1_key=tkn1.key,
                last_updated_block=self.c.w3.eth.blockNumber
            )
            liquidity_params = self.get_liquidity_from_contract(exchange_name=exchange_name,
                                                                contract=pool_contract, address=tkn1_address)
            return {**common_data, **liquidity_params}
        except Exception as e:
            self.c.logger.warning(
                f"[create_pool] Failed to create pool for {exchange_name}, {pool_address}, {e}"
            )

    def create_or_update_pool_with_multicall(
            self, pools: List[Tuple[str, str, Contract]]

    ):
        """
        Create or update pools with multicall to improve efficiency

        Parameters
        ----------
        pools : List[Tuple[str, str]]
            A list of pools to update

        """
        with brownie.multicall(address=self.c.MULTICALL_CONTRACT_ADDRESS):
            for exchange_name, pool_address, contract in pools:
                try:
                    pool = self.get_pool(exchange_name=exchange_name, address=pool_address)
                    if not pool:
                        params = self.build_pool_params(exchange_name=exchange_name, pool_address=pool_address,
                                                        pool_contract=contract)
                        self.create_pool(params)
                    else:
                        liquidity_params = self.get_liquidity_from_contract(exchange_name=exchange_name,
                                                                            contract=contract,
                                                                            address=pool_address)
                        liquidity_params['last_updated_block'] = self.c.w3.eth.blockNumber
                        liquidity_params['cid'] = self.next_cid
                        self.update_pool(liquidity_params)
                except Exception as e:
                    self.c.logger.warning(
                        f"[managers.create_or_update_pool_with_multicall] Error updating pool {pool_address} "
                        f"on {exchange_name}, {e}, continuing..."
                    )
                    continue
