"""
Main DB manager of the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import field
from typing import Any, Dict, Type, Optional, Tuple, List

import pandas as pd
from _decimal import Decimal
from brownie import Contract

from fastlane_bot.db.model_managers import PoolManager, TokenManager, PairManager
import fastlane_bot.db.models as models

from fastlane_bot import config as c
import fastlane_bot.data.abi as _abi


class DatabaseManager(PoolManager, TokenManager, PairManager):
    """
    DatabaseManager class that inherits from PoolManager, TokenManager, and PairManager
    and provides methods to update the database from events.
    """

    __VERSION__ = "3.0.1"
    __DATE__ = "04-26-2023"

    data: pd.DataFrame = field(default_factory=pd.DataFrame)

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
        blockchain = models.Blockchain(name=c.ETHEREUM_BLOCKCHAIN_NAME)
        blockchain.block_number = c.w3.eth.blockNumber
        self.session.add(blockchain)
        self.session.commit()

    def create_supported_exchanges(self):
        """
        Creates the supported exchanges in the database
        """
        for exchange in c.SUPPORTED_EXCHANGES:
            self.session.add(models.Exchange(name=exchange, blockchain_name=c.ETHEREUM_BLOCKCHAIN_NAME))
        self.session.commit()

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
        if pool.exchange_name == c.BANCOR_V3_NAME:
            self.update_pool(**{
                "id": pool.id,
                "last_updated_block": processed_event["block_number"],
                "tkn0_balance": processed_event["newLiquidity"]
            } if processed_event["token"] == c.BNT_ADDRESS else {
                "id": pool.id,
                "tkn1_balance": processed_event["newLiquidity"],
            })

        elif pool.exchange_name == c.UNISWAP_V3_NAME:
            self.update_pool(**{
                "id": pool.id,
                "last_updated_block": processed_event["block_number"],
                "sqrt_price_q96": processed_event["sqrt_price_q96"],
                "liquidity": processed_event["liquidity"],
                "tick": processed_event["tick"],
            })

        elif pool.exchange_name in c.UNIV2_FORKS + [c.BANCOR_V2_NAME]:
            self.update_pool(**{
                "id": pool.id,
                "last_updated_block": processed_event["block_number"],
                "tkn0_balance": processed_event["tkn0_balance"],
                "tkn1_balance": processed_event["tkn1_balance"],
            })

        elif c.CARBON_V1_NAME in pool.exchange_name:
            self.update_pool(**{
                "id": pool.id,
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
                                  pool: models.Pool,
                                  contract: Contract,
                                  strategy: Optional[Any] = None,
                                  address: Optional[str] = None):
        """
        Updates a pool with the provided strategy.

        Parameters
        ----------
        pool : models.Pool
            The pool object
        strategy : Any
            The strategy object
        last_updated_block : int
            The last block from which we collected 0.0-data-archive

        """
        common_params = {
            "id": pool.id,
            "last_updated_block": c.w3.eth.block_number,
        }
        liquidity_params = self.get_liquidity_from_contract(exchange_name=pool.exchange_name,
                                                            contract=contract,
                                                            address=address,
                                                            strategy=strategy)
        update_params = {**common_params, **liquidity_params}
        self.update_pool(**update_params)

    def get_liquidity_from_contract(self,
                                      exchange_name: str,
                                      contract: Contract,
                                      strategy: Optional[Any] = None,
                                      address: Optional[str] = None):
        """
        Updates a pool with the provided strategy.

        Parameters
        ----------
        pool : models.Pool
            The pool object
        strategy : Any
            The strategy object
        last_updated_block : int
            The last block from which we collected 0.0-data-archive

        """
        params = {}
        if exchange_name == c.BANCOR_V3_NAME:
            pool_balances = contract.tradingLiquidity(address)
            params = {
                "fee": "0.000",
                "tkn0_balance": pool_balances[0],
                "tkn1_balance": pool_balances[1],
            }
        elif exchange_name == c.BANCOR_V2_NAME:
            reserve0, reserve1 = contract.caller.reserveBalances()
            params = {
                "fee": "0.003",
                "tkn0_balance": reserve0,
                "tkn1_balance": reserve1,
            }
        elif exchange_name == c.UNISWAP_V3_NAME:
            slot0 = contract.caller.slot0()
            params = {
                "tick": slot0[1],
                "sqrt_price_q96": slot0[0],
                "liquidity": contract.caller.liquidity(),
                "fee": contract.caller.fee(),
                "tick_spacing": contract.caller.tickSpacing(),
            }

        elif exchange_name in c.UNIV2_FORKS:
            reserve_balance = contract.caller.getReserves()
            params = {
                "fee": "0.003",
                "tkn0_balance": reserve_balance[0],
                "tkn1_balance": reserve_balance[1],
            }
        elif c.CARBON_V1_NAME in exchange_name:
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
            contract = c.w3.eth.contract(address=address, abi=_abi.ERC20_ABI)
            symbol = contract.caller.symbol()
            tkn_key = f"{symbol}-{address[:-4]}"
            token = models.Token(address=address, name=contract.caller.name(), symbol=symbol, decimals=contract.caller.decimals(), key=tkn_key)
            self.create_token(token)
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
            tkn0_key = self.get_token(address=tkn0_address).key
            tkn1_key = self.get_token(address=tkn1_address).key
            pair = models.Pair(tkn0_address=tkn0_address, tkn1_address=tkn1_address, name=f"{tkn0_key}/{tkn1_key}")
            self.create_pair(pair)
        return pair

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
        elif exchange_name == c.BANCOR_V2_NAME:
            reserve_tokens = pool_contract.caller.reserveTokens()
            tkn0_address = c.w3.toChecksumAddress(reserve_tokens[0])
            tkn1_address = c.w3.toChecksumAddress(reserve_tokens[1])
        else:
            tkn0_address = c.w3.toChecksumAddress(pool_contract.caller.token0())
            tkn1_address = c.w3.toChecksumAddress(pool_contract.caller.token1())
        return tkn0_address, tkn1_address

    def create_pool_from_contract(self, exchange_name: str, pool_address: str, strategy: Tuple[str, str, str, Any]):
        """
        Creates a pool with the provided strategy.

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_address : str
            The address of the pool
        contract : Contract
            The contract object

        """
        cid = self.next_cid if strategy is None else str(strategy[0])
        contract = self.contract_from_address(exchange_name, pool_address)
        common_params = {
            "id": self.next_id,
            "cid": cid,
            "last_updated_block": c.w3.eth.block_number,
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
        pool_params = params | other_params
        self.create_pool(**pool_params)

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
            pool_contract = self.contract_from_address(exchange_name, pool_address)
            self.update_pool(exchange_name, pool_address, pool_contract)

    def _get_bnt_price_from_tokens(self, price, tkn) -> Decimal:
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


