"""
Main DB manager of the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import time
from typing import Any, Dict, Type, Optional, Tuple, List

import brownie
import numpy as np
import pandas as pd
from _decimal import Decimal
from brownie import Contract

import fastlane_bot.data.abi as _abi
import fastlane_bot.db.models as models
from fastlane_bot.config import Config
from fastlane_bot.db.model_managers import PoolManager, TokenManager, PairManager


class DatabaseManager(PoolManager, TokenManager, PairManager):
    """
    DatabaseManager class that inherits from PoolManager, TokenManager, and PairManager
    and provides methods to update the database from events.
    """

    __VERSION__ = "3.0.5"
    __DATE__ = "May-03-2023"

    ConfigObj: Config = None

    c = ConfigObj

    update_interval_seconds = 12
    pools_and_token_table = None


    def update_pools_from_contracts(self, only_carbon: bool, bypairs: List[str] = None, pools_and_token_table: pd.DataFrame = None):
        """
        Updates the pools_and_token_table with the latest liquidity data from the contracts.

        Parameters
        ----------
        pools_and_token_table : pd.DataFrame
            The pools_and_token_table to update. If None, the default table will be used.
        bypairs : List[str]
            A list of pair names to update. If None, all pairs will be updated.
        only_carbon : bool
            If True, only Carbon_v1 pairs will be updated.
        """

        if not bypairs:
            bypairs = pools_and_token_table['pair_name'].unique().tolist()

        # Add Carbon_v1 pairs to the table if they do not already exist
        pools_and_token_table = self.add_missing_pairs_to_table(pools_and_token_table, only_carbon)

        # Filter the table by the pairs to update
        filtered_table = pools_and_token_table[pools_and_token_table['pair_name'].isin(bypairs)]
        filtered_table = filtered_table.sort_values(by=['exchange_name'])

        if only_carbon:
            filtered_table = filtered_table[filtered_table['exchange_name'] == 'carbon_v1']

        for index, row in filtered_table.iterrows():
            self.update_pool_from_row(row, index, filtered_table)

    def add_missing_pairs_to_table(self, pools_and_token_table: pd.DataFrame, only_carbon: bool) -> pd.DataFrame:
        """
        Adds missing pairs to the pools_and_token_table.

        Parameters
        ----------
        pools_and_token_table : pd.DataFrame
            The pools_and_token_table to add the missing pairs to.
        only_carbon : bool
            If True, only Carbon_v1 pairs will be added.

        Returns
        -------
        pools_and_token_table : pd.DataFrame
            The pools_and_token_table with the missing pairs added.

        """
        carbon_pairs = missing_pairs = self.get_carbon_pairs()
        if only_carbon:
            pools_and_token_table = pools_and_token_table[pools_and_token_table['exchange_name'] != 'carbon_v1']
        if not only_carbon:
            noncarbon_pairs = self.get_noncarbon_pairs(pools_and_token_table)
            all_pairs = carbon_pairs + noncarbon_pairs
            missing_pairs = [pair for pair in all_pairs if pair not in noncarbon_pairs]
        for pair in missing_pairs:
            pair_name = self.get_pair_name(pair)
            dbrow = self.create_dbrow(pair_name, pools_and_token_table)
            pools_and_token_table = pd.concat([pools_and_token_table, dbrow], ignore_index=True)

        return pools_and_token_table

    def get_noncarbon_pairs(self, pools_and_token_table: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Gets the non-carbon pairs from the pools_and_token_table.

        Parameters
        ----------
        pools_and_token_table : pd.DataFrame
            The pools_and_token_table to get the non-carbon pairs from.

        Returns
        -------
        noncarbon_pairs : List[str]
            The non-carbon pairs.

        """
        noncarbon = pools_and_token_table[pools_and_token_table['exchange_name'] != 'carbon_v1']
        return (
            noncarbon[['tkn0_address', 'tkn1_address']]
            .drop_duplicates()
            .values.tolist()
        )

    def get_pair_name(self, pair: Tuple[str, str]) -> str:
        """
        Gets the pair name from a pair.

        Parameters
        ----------
        pair : Tuple[str, str]
            The pair to get the pair name from.

        Returns
        -------
        pair_name : str
            The pair name.

        """

        tkn0 = self.get_or_create_token(address=pair[0])
        tkn1 = self.get_or_create_token(address=pair[1])
        return f"{tkn0.key}/{tkn1.key}"

    def create_dbrow(self, pair_name: str, pools_and_token_table: pd.DataFrame) -> pd.DataFrame:
        """
        Creates a dbrow for a pair that does not exist in the pools_and_token_table.

        Parameters
        ----------
        pair_name : str
            The pair name to create.
        pools_and_token_table : pd.DataFrame
            The pools_and_token_table to create the dbrow from.

        Returns
        -------
        dbrow : pd.DataFrame
            The dbrow to add to the pools_and_token_table.

        """

        tkn0, tkn1 = pair_name.split('/')
        tkn0 = self.get_token(key=tkn0)
        tkn1 = self.get_token(key=tkn1)
        dbrow = pd.DataFrame({'pair_name': [pair_name], 'tkn0_address': [tkn0.address], 'tkn1_address': [tkn1.address],
                              'exchange_name': ['carbon_v1'], 'address': self.carbon_controller.address})
        missing_cols = [col for col in pools_and_token_table.columns if col not in dbrow.columns]
        for col in missing_cols:
            dbrow[col] = [np.NaN]
        return dbrow

    def update_pool_from_row(self, row: pd.Series, index: int = None, filtered_table: pd.DataFrame = None):
        """
        Updates a single pool from a row in the pools_and_token_table.

        Parameters
        ----------
        row : pd.Series
            The row to update.
        index : int
            The index of the row to update.
        filtered_table : pd.DataFrame
            The filtered table to update from.

        """

        params = row.to_dict()
        params['tkn0_address'], params['tkn1_address'] = self.c.w3.toChecksumAddress(
            params['tkn0_address']), self.c.w3.toChecksumAddress(params['tkn1_address'])

        block_number = self.ConfigObj.w3.eth.block_number
        params['last_updated_block'] = block_number

        contract = self.get_or_init_contract(exchange_name=params['exchange_name'],
                                             pool_address=params['address'])

        strategies = self.get_strategies_for_row(params)

        for strategy in strategies:
            try:
                self.update_pool_from_strategy(params, strategy, contract, filtered_table)
            except Exception as e:
                self.c.logger.error(f"[update_pools_from_contracts] Error updating pool: {e}, skipping...")

    def get_strategies_for_row(self, params: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Gets the strategies for a row in the pools_and_token_table.
        Parameters
        ----------
        params : Dict[str, Any]
            The params dictionary.

        Returns
        -------
        strategies : List[Tuple[str, str]]
            The strategies for the row.

        """
        if params['exchange_name'] == 'carbon_v1':
            return self.get_strategies((params['tkn0_address'], params['tkn1_address']))
        else:
            return [None]

    def update_pool_from_strategy(self, params: Dict[str, Any], strategy: Tuple[str, str], contract: Contract, filtered_table: pd.DataFrame = None):
        """
        Updates a pool from a strategy. The params dictionary contains data from a specific row in the pools_and_token_table, and the strategy provides additional information needed to update the pool.

        Parameters
        ----------
        params : Dict[str, Any]
            The params dictionary.
        strategy : Tuple[str, str]
            The strategy tuple.
        contract : Contract
            The contract to update the pool from.

        """
        if strategy is not None:
            params = self.update_params_from_strategy(params, strategy)

        params['fee_float'] = float(params['fee']) / 1000000.0 if params['exchange_name'] == 'uniswap_v3' else float(
            params['fee'])

        liquidity_params = self.get_liquidity_from_contract(exchange_name=params['exchange_name'],
                                                            contract=contract,
                                                            address=params['address'],
                                                            strategy=strategy)
        random_pool = self.get_pools()[0]
        pool_data = {k: v for k, v in params.items() if k in random_pool.__getattribute__('__table__').columns.keys() and k not in ['last_updated']}
        update_params = {**pool_data, **liquidity_params}

        pool = self.get_pool(cid=str(params['cid']))
        if pool is None:

            update_params['descr'] = f"{update_params['exchange_name']} {update_params['pair_name']} {update_params['fee']}"
            self.get_or_create_token(params['tkn0_address'])
            self.get_or_create_token(params['tkn1_address'])
            self.get_or_create_pair(params['tkn0_address'], params['tkn1_address'])
            self.create_pool(update_params)
        else:
            self.update_pool(update_params, params)

    def update_params_from_strategy(self, params: Dict[str, Any], strategy: Tuple[int, str, Tuple[str, str]]) -> Dict[
        str, Any]:
        """
        Updates the params dictionary from a strategy.

        Parameters
        ----------
        params : Dict[str, Any]
            The params dictionary.
        strategy : Tuple[int, str, Tuple[str, str]]
            The strategy tuple.

        Returns
        -------
        params : Dict[str, Any]
            The updated params dictionary.

        """
        params['cid'] = str(strategy[0])
        params['tkn0_address'], params['tkn1_address'] = self.c.w3.toChecksumAddress(
            strategy[2][0]), self.c.w3.toChecksumAddress(strategy[2][1])
        tkn0 = self.get_or_create_token(address=params['tkn0_address'])
        tkn1 = self.get_or_create_token(address=params['tkn1_address'])
        params['tkn0_symbol'], params['tkn1_symbol'] = tkn0.symbol, tkn1.symbol
        params['tkn0_decimals'], params['tkn1_decimals'] = tkn0.decimals, tkn1.decimals
        params['tkn0_key'], params['tkn1_key'] = tkn0.key, tkn1.key
        params['pair_name'] = f"{tkn0.key}/{tkn1.key}"
        params['desc'] = f"carbon_v1 {tkn0.key}/{tkn1.key} 0.002"
        params['fee'] = 0.002
        return params

    def update_pools_heartbeat(self, only_carbon: bool, bypairs: List[str] = None, update_interval_seconds: int = 12,
                               pools_and_token_table: pd.DataFrame = None):
        """
        Updates pools in a loop. This is the main function that should be called to update pools.

        Parameters
        ----------
        bypairs : List[str]
            The list of pairs to update.
        update_interval_seconds : int
            The update interval in seconds.
        pools_and_token_table : pd.DataFrame
            The pools and token table to update from.
        only_carbon : bool
            Whether to only update carbon pools.
        """
        while True:
            self.update_pools_from_contracts(bypairs=bypairs, pools_and_token_table=pools_and_token_table, only_carbon=only_carbon)
            time.sleep(update_interval_seconds)

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
                "fee_float": 0.000,
                "tkn0_balance": pool_balances[0],
                "tkn1_balance": pool_balances[1],
            }
        elif exchange_name == self.ConfigObj.BANCOR_V2_NAME:
            reserve0, reserve1 = contract.caller.reserveBalances()
            params = {
                "fee": "0.003",
                "fee_float": 0.003,
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
                "fee_float": str(contract.caller.fee() / 1000000),
                "tick_spacing": contract.caller.tickSpacing(),
            }

        elif exchange_name in self.ConfigObj.UNIV2_FORKS:
            reserve_balance = contract.caller.getReserves()
            params = {
                "fee": "0.003",
                "fee_float": 0.003,
                "tkn0_balance": reserve_balance[0],
                "tkn1_balance": reserve_balance[1],
            }
        elif self.ConfigObj.CARBON_V1_NAME in exchange_name:
            order0, order1 = strategy[3][0], strategy[3][1]
            params = {
                "fee": "0.002",
                "fee_float": 0.002,
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
                tkn_obj = self.get_or_create_token(tkn)
                token_symbols.append(tkn_obj.symbol)

            if top_n is None:
                # Filter the df to only include carbon tokens on the given exchange
                return self.data[(self.data['exchange'] == exchange) & (
                        self.data['tkn0_symbol'].isin(token_symbols) | self.data['tkn1_symbol'].isin(token_symbols))][
                    'address'].unique().tolist()
            else:
                try:
                    return self.data[(self.data['exchange'] == exchange) & (
                            self.data['tkn0_symbol'].isin(token_symbols) | self.data['tkn1_symbol'].isin(
                        token_symbols))][
                               'address'].unique().tolist()[:top_n]
                except IndexError:
                    self.c.logger.error(f"Could not get {top_n} genesis pools for {exchange}")
                    return []

        if top_n is None:
            return self.data[self.data['exchange'] == exchange]['address'].unique().tolist()
        else:
            try:
                return self.data[self.data['exchange'] == exchange]['address'].unique().tolist()[:top_n]
            except IndexError:
                self.c.logger.error(f"Could not get {top_n} genesis pools for {exchange}")
                return []

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
            try:
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

            except Exception as e:
                self.c.logger.error(
                    f"[manager.create_pools_from_contracts] Error creating pool {exchange} {address} [{e}]")
                continue

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
                self.update_carbon_pool(strategy, last_updated_block)
            else:
                self.create_carbon_pool(strategy, last_updated_block)

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
