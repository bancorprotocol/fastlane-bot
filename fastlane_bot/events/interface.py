# coding=utf-8
"""
Contains the interface for querying data from the data fetcher module.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional

from fastlane_bot.config import Config
from fastlane_bot.helpers.poolandtokens import PoolAndTokens


@dataclass
class Token:

    __VERSION__ = "0.0.1"
    __DATE__ = "2023-07-03"

    symbol: str
    address: str
    decimals: int
    key: str

    def __eq__(self, other):
        return self.key == other.key if isinstance(other, Token) else False

    def __hash__(self):
        return hash(self.key)


@dataclass
class Pool(PoolAndTokens):

    __VERSION__ = "0.0.1"
    __DATE__ = "2023-07-03"

    pass


@dataclass
class QueryInterface:
    """
    Interface for querying data from the data fetcher module. These methods mirror the existing methods
    expected/used in the bot module. The implementation of these methods should allow for the bot module
    to be used with the new data fetcher module without any changes to the bot module.
    """

    __VERSION__ = "0.0.1"
    __DATE__ = "2023-07-03"

    mgr: Any = None
    state: List[Dict[str, Any]] = field(default_factory=list)
    ConfigObj: Config = None
    uniswap_v2_event_mappings: Dict[str, str] = field(default_factory=dict)
    exchanges: List[str] = field(default_factory=list)

    @property
    def cfg(self) -> Config:
        return self.ConfigObj

    def remove_unsupported_exchanges(self) -> None:
        initial_state = self.state.copy()
        self.state = [
            pool for pool in self.state if pool["exchange_name"] in self.exchanges
        ]
        self.cfg.logger.info(
            f"Removed {len(initial_state) - len(self.state)} unsupported exchanges. {len(self.state)} pools remaining"
        )

        # Log the total number of pools remaining for each exchange
        self.ConfigObj.logger.info("Pools remaining per exchange:")
        for exchange_name in self.exchanges:
            pools = self.filter_pools(exchange_name)
            self.log_pool_numbers(pools, exchange_name)

    def has_balance(self, pool: Dict[str, Any], key: str) -> bool:
        """
        Check if a pool has a balance for a given key

        Parameters
        ----------
        pool: Dict[str, Any]
            The pool to check
        key: str
            The key to check for a balance

        Returns
        -------
        bool
            True if the pool has a balance for the given key, False otherwise

        """
        return key in pool and pool[key] > 0

    def filter_pools(self, exchange_name: str, key: str = "") -> List[Dict[str, Any]]:
        """
        Filter pools by exchange name and key

        Parameters
        ----------
        exchange_name: str
            The exchange name to filter by
        key: str
            The key to filter by

        Returns
        -------
        List[Dict[str, Any]]
            The filtered pools
        """
        if key:
            return [
                pool
                for pool in self.state
                if pool["exchange_name"] == exchange_name
                and self.has_balance(pool, key)
            ]
        else:
            return [
                pool for pool in self.state if pool["exchange_name"] == exchange_name
            ]

    def log_pool_numbers(self, pools: List[Dict[str, Any]], exchange_name: str) -> None:
        """
        Log the number of pools for a given exchange name

        Parameters
        ----------
        pools: List[Dict[str, Any]]
            The pools to log
        exchange_name: str
            The exchange name to log

        """
        self.cfg.logger.info(f"{exchange_name}: {len(pools)}")

    def remove_zero_liquidity_pools(self) -> None:
        """
        Remove pools with zero liquidity.
        """
        initial_state = self.state.copy()

        exchanges = [
            "uniswap_v3",
            "sushiswap_v2",
            "uniswap_v2",
            "bancor_v2",
            "bancor_v3",
            "carbon_v1",
        ]
        keys = [
            "liquidity",
            "tkn0_balance",
            "tkn0_balance",
            "tkn0_balance",
            "tkn0_balance",
            "",
        ]

        self.state = [
            pool
            for exchange, key in zip(exchanges, keys)
            for pool in self.filter_pools(exchange, key)
        ]

        for exchange in exchanges:
            self.log_pool_numbers(
                [pool for pool in self.state if pool["exchange_name"] == exchange],
                exchange,
            )

        zero_liquidity_pools = [
            pool for pool in initial_state if pool not in self.state
        ]

        for exchange in exchanges:
            self.log_pool_numbers(
                [
                    pool
                    for pool in zero_liquidity_pools
                    if pool["exchange_name"] == exchange
                ],
                f"{exchange}_zero_liquidity_pools",
            )

    def remove_unmapped_uniswap_v2_pools(self) -> None:
        """
        Remove unmapped uniswap_v2 pools
        """
        initial_state = self.state.copy()
        self.state = [
            pool
            for pool in self.state
            if pool["exchange_name"] != "uniswap_v2"
            or (
                pool["exchange_name"] in ["uniswap_v2", "sushiswap_v2"]
                and pool["address"] in self.uniswap_v2_event_mappings
            )
        ]
        self.cfg.logger.info(
            f"Removed {len(initial_state) - len(self.state)} unmapped uniswap_v2/sushi pools. {len(self.state)} uniswap_v2/sushi pools remaining"
        )
        self.log_umapped_pools_by_exchange(initial_state)

    def log_umapped_pools_by_exchange(self, initial_state):
        # Log the total number of pools filtered out for each exchange
        self.ConfigObj.logger.info("Unmapped uniswap_v2/sushi pools:")
        unmapped_pools = [pool for pool in initial_state if pool not in self.state]
        assert len(unmapped_pools) == len(initial_state) - len(self.state)
        uniswap_v3_unmapped = [
            pool for pool in unmapped_pools if pool["exchange_name"] == "uniswap_v3"
        ]
        self.log_pool_numbers(uniswap_v3_unmapped, "uniswap_v3")
        uniswap_v2_unmapped = [
            pool for pool in unmapped_pools if pool["exchange_name"] == "uniswap_v2"
        ]
        self.log_pool_numbers(uniswap_v2_unmapped, "uniswap_v2")
        sushiswap_v2_unmapped = [
            pool for pool in unmapped_pools if pool["exchange_name"] == "sushiswap_v2"
        ]
        self.log_pool_numbers(sushiswap_v2_unmapped, "sushiswap_v2")

    def remove_faulty_token_pools(self) -> None:
        """
        Remove pools with faulty tokens
        """
        self.cfg.logger.info(
            f"Total number of pools. {len(self.state)} before removing faulty token pools"
        )

        safe_pools = []
        for pool in self.state:
            try:
                self.get_token(pool["tkn0_key"])
                self.get_token(pool["tkn1_key"])
                safe_pools.append(pool)
            except Exception as e:
                self.cfg.logger.info(f"Exception: {e}")
                self.cfg.logger.info(
                    f"Removing pool for exchange={pool['pair_name']}, pair_name={pool['pair_name']} token={pool['tkn0_key']} from state for faulty token"
                )

        self.state = safe_pools

    @staticmethod
    def cleanup_token_key(token_key: str) -> str:
        """
        Cleanup token key. This renames keys that have more than 1 '-' in them.

        Parameters
        ----------
        token_key: str
            The token key to cleanup

        Returns
        -------
        str
            The cleaned up token key

        """
        split_key = token_key.split("-", 2)
        return (
            f"{split_key[0]}_{split_key[1]}-{split_key[2]}"
            if len(split_key) > 2
            else token_key
        )

    def handle_token_key_cleanup(self) -> None:
        """
        Cleanup token keys in state
        """
        for idx, pool in enumerate(self.state):
            key0 = self.cleanup_token_key(pool["tkn0_key"])
            key1 = self.cleanup_token_key(pool["tkn1_key"])
            self.state[idx]["tkn0_key"] = key0
            self.state[idx]["tkn1_key"] = key1
            self.state[idx]["pair_name"] = key0 + "/" + key1

    def update_state(self, state: List[Dict[str, Any]]) -> None:
        """
        Update the state.

        Parameters
        ----------
        state: List[Dict[str, Any]]
            The new state

        """
        self.state = state.copy()
        if self.state == state:
            self.cfg.logger.warning("WARNING: State not updated")

    def drop_all_tables(self) -> None:
        """
        Drop all tables. Deprecated.
        """
        raise DeprecationWarning("Method not implemented")

    def get_pool_data_with_tokens(self) -> List[PoolAndTokens]:
        """
        Get pool data with tokens
        """
        return [
            self.create_pool_and_tokens(idx, record)
            for idx, record in enumerate(self.state)
        ]

    def create_pool_and_tokens(self, idx: int, record: Dict[str, Any]) -> PoolAndTokens:
        """
        Create a pool and tokens object from a record

        Parameters
        ----------
        idx: int
            The index of the record
        record: Dict[str, Any]
            The record

        Returns
        -------
        PoolAndTokens
            The pool and tokens object

        """
        result = PoolAndTokens(
            ConfigObj=self.ConfigObj,
            id=idx,
            **{
                key: record.get(key)
                for key in [
                    "cid",
                    "last_updated",
                    "last_updated_block",
                    "descr",
                    "pair_name",
                    "exchange_name",
                    "fee",
                    "fee_float",
                    "tkn0_balance",
                    "tkn1_balance",
                    "z_0",
                    "y_0",
                    "A_0",
                    "B_0",
                    "z_1",
                    "y_1",
                    "A_1",
                    "B_1",
                    "sqrt_price_q96",
                    "tick",
                    "tick_spacing",
                    "liquidity",
                    "address",
                    "anchor",
                    "tkn0",
                    "tkn1",
                    "tkn0_key",
                    "tkn1_key",
                    "tkn0_address",
                    "tkn0_decimals",
                    "tkn1_address",
                    "tkn1_decimals",
                ]
            },
        )
        result.tkn0 = result.pair_name.split("/")[0].split("-")[0]
        result.tkn1 = result.pair_name.split("/")[1].split("-")[0]
        result.tkn0_key = result.pair_name.split("/")[0]
        result.tkn1_key = result.pair_name.split("/")[1]
        return result

    def get_tokens(self) -> List[Token]:
        """
        Get tokens. This method returns a list of tokens that are in the state.

        Returns
        -------
        List[Token]
            The list of tokens
        """
        token_set = set()
        for record in self.state:
            token_set.add(self.create_token(record, "tkn0_"))
            token_set.add(self.create_token(record, "tkn1_"))
        return list(token_set)

    def create_token(self, record: Dict[str, Any], prefix: str) -> Token:
        """
        Create a token from a record

        Parameters
        ----------
        record: Dict[str, Any]
            The record
        prefix: str
            The prefix of the token

        Returns
        -------
        Token
            The token

        """
        return Token(
            symbol=record.get(f"{prefix}symbol"),
            decimals=record.get(f"{prefix}decimals"),
            key=record.get(f"{prefix}key"),
            address=record.get(f"{prefix}address"),
        )

    def get_bnt_price_from_tokens(self, price: float, tkn: Token) -> float:
        """
        Get the BNT price from tokens

        Parameters
        ----------
        price: float
            The price
        tkn: Token
            The token

        Returns
        -------
        float
            The BNT price

        """
        raise DeprecationWarning("Method not implemented")

    def get_token(self, key: str) -> Optional[Token]:
        """
        Get a token from the state

        Parameters
        ----------
        key: str
            The token key

        Returns
        -------
        Optional[Token]
            The token

        """
        tokens = self.get_tokens()
        if "-" in key:
            return next((tkn for tkn in tokens if tkn.key == key), None)
        elif key.startswith("0x"):
            return next((tkn for tkn in tokens if tkn.address == key), None)
        else:
            raise ValueError(f"[get_token] Invalid token: {key}")

    def get_pool(self, **kwargs) -> Optional[PoolAndTokens]:
        """
        Get a pool from the state

        Parameters
        ----------
        kwargs: Dict[str, Any]
            The pool parameters

        Returns
        -------
        Pool
            The pool

        """
        pool_data_with_tokens = self.get_pool_data_with_tokens()
        try:
            pool = next(
                (
                    pool
                    for pool in pool_data_with_tokens
                    if all(getattr(pool, key) == kwargs[key] for key in kwargs)
                ),
                None,
            )
            pool.exchange_name
        except AttributeError:
            if 'cid' in kwargs:
                kwargs['cid'] = int(kwargs['cid'])
                pool = next(
                    (
                        pool
                        for pool in pool_data_with_tokens
                        if all(getattr(pool, key) == kwargs[key] for key in kwargs)
                    ),
                    None,
                )
        return pool

    def get_pools(self) -> List[PoolAndTokens]:
        """
        Get all pools from the state

        Returns
        -------
        List[Pool]
            The list of pools

        """
        return self.get_pool_data_with_tokens()

    def update_recently_traded_pools(self, cids: List[str]):
        """
        Update recently traded pools. Deprecated.

        Parameters
        ----------
        cids: List[str]
            The list of cids

        """
        raise DeprecationWarning("Method not implemented")
