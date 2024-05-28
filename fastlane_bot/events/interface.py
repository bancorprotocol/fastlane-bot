"""
Contains the interface for querying data from the data fetcher module.

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
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

    def __eq__(self, other):
        return self.address == other.address if isinstance(other, Token) else False

    def __hash__(self):
        return hash(self.address)


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
    uniswap_v3_event_mappings: Dict[str, str] = field(default_factory=dict)
    solidly_v2_event_mappings: Dict[str, str] = field(default_factory=dict)
    exchanges: List[str] = field(default_factory=list)
    token_list: Dict[str, Any] = None
    pool_data = None
    pool_data_list = None

    @property
    def cfg(self) -> Config:
        return self.ConfigObj

    def filter_target_tokens(self, target_tokens: List[str]):
        """
        Filter the pools to only include pools that are in the target pools list

        Parameters
        ----------
        target_tokens: List[str]
            The list of tokens to filter pools by. Pools must contain both tokens in the list to be included.
        """
        initial_state = self.state.copy()
        self.state = [
            pool
            for pool in self.state
            if pool["tkn0_address"] in target_tokens and pool["tkn1_address"] in target_tokens
        ]

        self.cfg.logger.info(
            f"[events.interface] Limiting pools by target_tokens. Removed {len(initial_state) - len(self.state)} non target-pools. {len(self.state)} pools remaining"
        )

        # Log the total number of pools remaining for each exchange
        self.ConfigObj.logger.debug("Pools remaining per exchange:")
        for exchange_name in self.exchanges:
            pools = self.filter_pools(exchange_name)
            self.log_pool_numbers(pools, exchange_name)

    def remove_unsupported_exchanges(self) -> None:
        initial_state = self.state.copy()
        self.state = [
            pool for pool in self.state if pool["exchange_name"] in self.exchanges
        ]
        self.cfg.logger.debug(
            f"Removed {len(initial_state) - len(self.state)} unsupported exchanges. {len(self.state)} pools remaining"
        )

        # Log the total number of pools remaining for each exchange
        self.ConfigObj.logger.debug("Pools remaining per exchange:")
        for exchange_name in self.exchanges:
            pools = self.filter_pools(exchange_name)
            self.log_pool_numbers(pools, exchange_name)

    def has_balance(self, pool: Dict[str, Any], keys: List[str]) -> bool:
        """
        Check if a pool has a balance for a given key

        Parameters
        ----------
        pool: Dict[str, Any]
            The pool to check
        keys: List[str]
            The keys to check for a balance

        Returns
        -------
        bool
            True if the pool has a balance for the given key, False otherwise

        """

        for key in keys:
            if key in pool and pool[key] > 0:
                return True
        return False

    def get_tokens_from_exchange(self, exchange_name: str) -> List[str]:
        """
        This token gets all tokens that exist in pools on the specified exchange.
        Parameters
        ----------
        exchange_name: str
            The exchange from which to get tokens.

        Returns
        -------
        list[str]
            Returns a list of token keys.
        """
        pools = self.filter_pools(exchange_name=exchange_name)
        tokens = []
        for pool in pools:
            for idx in range(8):
                try:
                    tkn = pool[f"tkn{idx}_address"]
                    if type(tkn) == str:
                        tokens.append(tkn)
                except KeyError:
                    # Out of bounds
                    break
        tokens = list(set(tokens))
        return tokens

    def filter_pools(
        self, exchange_name: str, keys: List[str] = ""
    ) -> List[Dict[str, Any]]:
        """
        Filter pools by exchange name and key

        Parameters
        ----------
        exchange_name: str
            The exchange name to filter by
        keys: str
            The key to filter by

        Returns
        -------
        List[Dict[str, Any]]
            The filtered pools
        """
        if keys:
            return [
                pool
                for pool in self.state
                if pool["exchange_name"] == exchange_name
                and self.has_balance(pool, keys)
                and pool["tkn0_decimals"] is not None
                and pool["tkn1_decimals"] is not None
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
        self.cfg.logger.debug(f"[events.interface] {exchange_name}: {len(pools)}")

    def remove_zero_liquidity_pools(self) -> None:
        """
        Remove pools with zero liquidity.
        """
        initial_state = self.state.copy()

        exchanges = []
        keys = []

        for ex in self.cfg.ALL_KNOWN_EXCHANGES:
            if ex in self.cfg.UNI_V2_FORKS + self.cfg.SOLIDLY_V2_FORKS + ["bancor_v2", "bancor_v3"]:
                exchanges.append(ex)
                keys.append(["tkn0_balance"])
            elif ex in self.cfg.UNI_V3_FORKS:
                exchanges.append(ex)
                keys.append(["liquidity"])
            elif ex in self.cfg.CARBON_V1_FORKS:
                exchanges.append(ex)
                keys.append(["y_0", "y_1"])
            elif ex in "bancor_pol":
                exchanges.append(ex)
                keys.append(["y_0"])
            elif ex in "balancer":
                exchanges.append(ex)
                keys.append(["tkn0_balance"])

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
            pool for pool in self.state
            if pool["exchange_name"] not in self.cfg.UNI_V2_FORKS or pool["address"] in self.uniswap_v2_event_mappings
        ]
        self.cfg.logger.debug(
            f"Removed {len(initial_state) - len(self.state)} unmapped uniswap_v2/sushi pools. {len(self.state)} uniswap_v2/sushi pools remaining"
        )

        # Log the total number of pools filtered out for each exchange
        self.ConfigObj.logger.debug("Unmapped uniswap_v2/sushi pools:")
        unmapped_pools = [pool for pool in initial_state if pool not in self.state]
        assert len(unmapped_pools) == len(initial_state) - len(self.state)
        # uniswap_v3_unmapped = [
        #     pool for pool in unmapped_pools if pool["exchange_name"] == "uniswap_v3"
        # ]
        # self.log_pool_numbers(uniswap_v3_unmapped, "uniswap_v3")
        uniswap_v2_unmapped = [
            pool for pool in unmapped_pools if pool["exchange_name"] == "uniswap_v2"
        ]
        self.log_pool_numbers(uniswap_v2_unmapped, "uniswap_v2")
        sushiswap_v2_unmapped = [
            pool for pool in unmapped_pools if pool["exchange_name"] == "sushiswap_v2"
        ]
        self.log_pool_numbers(sushiswap_v2_unmapped, "sushiswap_v2")

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

    def get_pool_data_with_tokens(self) -> List[PoolAndTokens]:
        """
        Get pool data with tokens as a List
        """
        if self.pool_data_list is None:
            self.refresh_pool_data()
        return self.pool_data_list

    def get_pool_data_lookup(self) -> Dict[str, PoolAndTokens]:
        """
        Get pool data with tokens as a Dict to find specific pools
        """
        if self.pool_data is None:
            self.refresh_pool_data()
        return self.pool_data

    def refresh_pool_data(self):
        """
        Refreshes pool data to ensure it is up-to-date
        """
        self.pool_data_list = [
            self.create_pool_and_tokens(idx, record)
            for idx, record in enumerate(self.state)
        ]
        self.pool_data = {str(pool.cid): pool for pool in self.pool_data_list}

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
                    "strategy_id",
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
                    "tkn0_address",
                    "tkn0_decimals",
                    "tkn1_address",
                    "tkn1_decimals",
                    "tkn0_weight",
                    "tkn1_weight",
                    "tkn2",
                    "tkn2_balance",
                    "tkn2_address",
                    "tkn2_decimals",
                    "tkn2_weight",
                    "tkn3",
                    "tkn3_balance",
                    "tkn3_address",
                    "tkn3_decimals",
                    "tkn3_weight",
                    "tkn4",
                    "tkn4_balance",
                    "tkn4_address",
                    "tkn4_decimals",
                    "tkn4_weight",
                    "tkn5",
                    "tkn5_balance",
                    "tkn5_address",
                    "tkn5_decimals",
                    "tkn5_weight",
                    "tkn6",
                    "tkn6_balance",
                    "tkn6_address",
                    "tkn6_decimals",
                    "tkn6_weight",
                    "tkn7",
                    "tkn7_balance",
                    "tkn7_address",
                    "tkn7_decimals",
                    "tkn7_weight",
                    "pool_type",
                ]
            },
        )
        result.tkn0 = result.pair_name.split("/")[0].split("-")[0]
        result.tkn1 = result.pair_name.split("/")[1].split("-")[0]
        result.tkn0_address = result.pair_name.split("/")[0]
        result.tkn1_address = result.pair_name.split("/")[1]
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
            for idx in range(len(record["descr"].split("/"))):
                try:
                    token_set.add(self.create_token(record, f"tkn{str(idx)}_"))
                except AttributeError:
                    pass
        token_set.add(Token(symbol=self.ConfigObj.NATIVE_GAS_TOKEN_SYMBOL, address=self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, decimals=18))
        token_set.add(Token(symbol=self.ConfigObj.WRAPPED_GAS_TOKEN_SYMBOL, address=self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, decimals=18))
        return list(token_set)

    def populate_tokens(self):
        """
        Populate the token Dict with tokens using the available pool data.
        """
        self.token_list = {}
        for record in self.state:
            for idx in range(len(record["descr"].split("/"))):
                try:
                    token = self.create_token(record, f"tkn{str(idx)}_")
                    self.token_list[token.address] = token
                except AttributeError:
                    pass
        # native and wrapped gas token info populated everytime
        native_gas_tkn = Token(symbol=self.ConfigObj.NATIVE_GAS_TOKEN_SYMBOL, address=self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, decimals=18)
        wrapped_gas_tkn = Token(symbol=self.ConfigObj.WRAPPED_GAS_TOKEN_SYMBOL, address=self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, decimals=18)
        self.token_list[native_gas_tkn.address] = native_gas_tkn
        self.token_list[wrapped_gas_tkn.address] = wrapped_gas_tkn

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

    def get_token(self, tkn_address: str) -> Optional[Token]:
        """
        Get a token from the state

        Parameters
        ----------
        tkn_address: str
            The token address

        Returns
        -------
        Optional[Token]
            The token

        """
        if self.token_list is None:
            self.populate_tokens()
        try:
            return self.token_list.get(tkn_address)
        except KeyError:
            try:
                self.populate_tokens()
                return self.token_list.get(tkn_address)
            except KeyError as e:
                self.ConfigObj.logger.info(f"[interface.py get_token] Could not find token: {tkn_address} in token_list")
                tokens = self.get_tokens()
                if tkn_address.startswith("0x"):
                    return next((tkn for tkn in tokens if tkn.address == tkn_address), None)
                else:
                    raise ValueError(f"[get_token] Invalid token: {tkn_address}")

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
        pool_data_with_tokens = self.get_pool_data_lookup()
        if "cid" in kwargs:
            cid = str(kwargs['cid'])
            try:
                return pool_data_with_tokens[cid]
            except KeyError:
                # pool not in data
                self.cfg.logger.error(f"[interface.py get_pool] pool with cid: {cid} not in data")
                return None
        else:
            try:
                return next(
                    (
                        pool
                        for pool in pool_data_with_tokens
                        if all(getattr(pool, key) == kwargs[key] for key in kwargs)
                    ),
                    None,
                )
            except AttributeError:
                return None

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
