import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict, Optional
import pandas as pd

from _decimal import Decimal

from fastlane_bot.config import Config
# from fastlane_bot.db.manager import DatabaseManager
from fastlane_bot.helpers.poolandtokens import PoolAndTokens


@dataclass
class Token:
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
    pass


@dataclass
class QueryInterface:
    """
    Interface for querying data from the data fetcher module. These methods mirror the existing methods
    expected/used in the bot module. The implementation of these methods should allow for the bot module
    to be used with the new data fetcher module without any changes to the bot module.
    """

    state: List[Dict[str, Any]] = field(default_factory=list)
    ConfigObj: Config = None
    crosscheck: Optional[pd.DataFrame] = None
    uniswap_v2_event_mappings: Dict[str, str] = field(default_factory=dict)

    def remove_zero_liquidity_pools(self):

        print(f"Total number of pools. {len(self.state)} before removing zero liquidity pools")
        initial_state = self.state.copy()

        uniswap_v3 = [pool for pool in self.state if pool["exchange_name"] == 'uniswap_v3' if 'liquidity' in pool and pool["liquidity"] > 0]
        sushiswap_v2 = [pool for pool in self.state if pool["exchange_name"] == 'sushiswap_v2' if 'tkn0_balance' in pool and pool["tkn0_balance"] > 0]
        uniswap_v2 = [pool for pool in self.state if pool["exchange_name"] == 'uniswap_v2' if 'tkn0_balance' in pool and pool["tkn0_balance"] > 0]
        bancor_v2 = [pool for pool in self.state if pool["exchange_name"] == 'bancor_v2' if 'tkn0_balance' in pool and pool["tkn0_balance"] > 0]
        bancor_v3 = [pool for pool in self.state if pool["exchange_name"] == 'bancor_v3' if 'tkn0_balance' in pool and pool["tkn0_balance"] > 0]
        carbon_v1 = [pool for pool in self.state if pool["exchange_name"] == 'carbon_v1']
        assert 'BNT-FF1C/ETH-EEeE' in [pair['pair_name'] for pair in bancor_v3], "BNT-FF1C/ETH-EEeE not found in bancor_v3"
        self.state = uniswap_v3 + sushiswap_v2 + uniswap_v2 + bancor_v2 + bancor_v3 + carbon_v1
        print(f"Removed zero liquidity pools. {len(self.state)} pools remaining")
        print(f"uniswap_v3: {len(uniswap_v3)}")
        print(f"sushiswap_v2: {len(sushiswap_v2)}")
        print(f"uniswap_v2: {len(uniswap_v2)}")
        print(f"bancor_v2: {len(bancor_v2)}")
        print(f"bancor_v3: {len(bancor_v3)}")
        print(f"carbon_v1: {len(carbon_v1)}")

        zero_liquidity_pools = [pool for pool in initial_state if pool not in self.state]
        print(f"zero_liquidity_pools: {len(zero_liquidity_pools)}")

        uniswap_v3_zero_liquidity_pools = [pool for pool in zero_liquidity_pools if pool["exchange_name"] == 'uniswap_v3']
        sushiswap_v2_zero_liquidity_pools = [pool for pool in zero_liquidity_pools if pool["exchange_name"] == 'sushiswap_v2']
        uniswap_v2_zero_liquidity_pools = [pool for pool in zero_liquidity_pools if pool["exchange_name"] == 'uniswap_v2']
        bancor_v2_zero_liquidity_pools = [pool for pool in zero_liquidity_pools if pool["exchange_name"] == 'bancor_v2']
        bancor_v3_zero_liquidity_pools = [pool for pool in zero_liquidity_pools if pool["exchange_name"] == 'bancor_v3']
        carbon_v1_zero_liquidity_pools = [pool for pool in zero_liquidity_pools if pool["exchange_name"] == 'carbon_v1']

        print(f"uniswap_v3_zero_liquidity_pools: {len(uniswap_v3_zero_liquidity_pools)}")
        print(f"sushiswap_v2_zero_liquidity_pools: {len(sushiswap_v2_zero_liquidity_pools)}")
        print(f"uniswap_v2_zero_liquidity_pools: {len(uniswap_v2_zero_liquidity_pools)}")
        print(f"bancor_v2_zero_liquidity_pools: {len(bancor_v2_zero_liquidity_pools)}")
        print(f"bancor_v3_zero_liquidity_pools: {len(bancor_v3_zero_liquidity_pools)}")
        print(f"carbon_v1_zero_liquidity_pools: {len(carbon_v1_zero_liquidity_pools)}")

    def select_random_pools(self, n_percent: float = 0.25):
        print(f"Total number of pools. {len(self.state)} before selecting random pools")
        initial_state = self.state.copy()

        uniswap_v3_random_pools = [pool for pool in self.state if pool["exchange_name"] == 'uniswap_v3']
        sushiswap_v2_random_pools = [pool for pool in self.state if pool["exchange_name"] == 'sushiswap_v2']
        uniswap_v2_random_pools = [pool for pool in self.state if pool["exchange_name"] == 'uniswap_v2']
        bancor_v2_random_pools = [pool for pool in self.state if pool["exchange_name"] == 'bancor_v2']
        bancor_v3_random_pools = [pool for pool in self.state if pool["exchange_name"] == 'bancor_v3']
        carbon_v1_random_pools = [pool for pool in self.state if pool["exchange_name"] == 'carbon_v1']

        external_pools = uniswap_v3_random_pools + sushiswap_v2_random_pools + uniswap_v2_random_pools + bancor_v2_random_pools

        # select random pools
        random.shuffle(external_pools)
        external_pools = external_pools[:int(len(external_pools) * n_percent)]
        self.state = external_pools + bancor_v3_random_pools + carbon_v1_random_pools
        print(f"Selected {len(self.state)} random pools from {len(initial_state)} pools")

    def remove_unmapped_uniswap_v2_pools(self):
        print(f"Total number of pools. {len(self.state)} before removing unmapped uniswap v2 pools")
        initial_state = self.state.copy()

        # remove uniswap v2 pools not found in uniswap_v2_event_mappings
        self.state = [pool for pool in self.state if pool["exchange_name"] != 'uniswap_v2' or (pool["exchange_name"] == 'uniswap_v2' and pool["address"] in self.uniswap_v2_event_mappings)]
        unmapped_uniswap_v2_pools = [pool for pool in initial_state if pool not in self.state]
        print(f"Removed {len(unmapped_uniswap_v2_pools)} unmapped uniswap_v2/sushi pools. {len(self.state)} uniswap_v2/sushi pools remaining")

    def remove_faulty_token_pools(self):
        print(f"Total number of pools. {len(self.state)} before removing faulty token pools")

        # for tkn0_key and tkn1_key in each pool, check if the token is faulty by calling get_token(key), if so, remove the pool from state
        for idx, pool in enumerate(self.state):
            try:
                self.get_token(pool["tkn0_key"])
            except Exception as e:
                print(f"Exception: {e}")
                print(f"Removing pool for exchange={pool['pair_name']}, pair_name={pool['pair_name']} token={pool['tkn0_key']} from state for faulty token")
                self.state.pop(idx)
            try:
                self.get_token(pool["tkn1_key"])
            except Exception as e:
                print(f"Exception: {e}")
                print(f"Removing pool for exchange={pool['pair_name']}, pair_name={pool['pair_name']} token={pool['tkn1_key']} from state for faulty token")
                self.state.pop(idx)

    @staticmethod
    def cleanup_token_key(token_key: str) -> str:
        return f"{token_key.split('-', 1)[0]}_{token_key.split('-', 1)[1]}" if len(
            token_key.split('-')) > 2 else token_key

    def handle_token_key_cleanup(self):
        for idx, pool in enumerate(self.state):
            self.state[idx]["tkn0_key"] = self.cleanup_token_key(pool["tkn0_key"])
            self.state[idx]["tkn1_key"] = self.cleanup_token_key(pool["tkn1_key"])
            key0 = self.state[idx]["tkn0_key"]
            key1 = self.state[idx]["tkn1_key"]
            self.state[idx]["pair_name"] = key0 + "/" + key1

    def update_state(self, state: List[Dict[str, Any]]):
        old_state = self.state
        self.state = state.copy()
        try:
            assert old_state != self.state
        except AssertionError:
            print("WARNING: State not updated")

    def drop_all_tables(self):
        # method implementation...
        return DeprecationWarning("Method not implemented")

    def get_pool_data_with_tokens(self) -> List:
        # method implementation...
        return [
            PoolAndTokens(
                ConfigObj=self.ConfigObj,
                id=idx,
                cid=record["cid"] if "cid" in record else None,
                last_updated=record["last_updated"]
                if "last_updated" in record
                else None,
                last_updated_block=record["last_updated_block"]
                if "last_updated_block" in record
                else None,
                descr=record["descr"] if "descr" in record else None,
                pair_name=record["pair_name"] if "pair_name" in record else None,
                exchange_name=record["exchange_name"]
                if "exchange_name" in record
                else None,
                fee=record["fee"] if "fee" in record else None,
                fee_float=record["fee_float"] if "fee_float" in record else None,
                tkn0_balance=record["tkn0_balance"]
                if "tkn0_balance" in record
                else None,
                tkn1_balance=record["tkn1_balance"]
                if "tkn1_balance" in record
                else None,
                z_0=record["z_0"] if "z_0" in record else None,
                y_0=record["y_0"] if "y_0" in record else None,
                A_0=record["A_0"] if "A_0" in record else None,
                B_0=record["B_0"] if "B_0" in record else None,
                z_1=record["z_1"] if "z_1" in record else None,
                y_1=record["y_1"] if "y_1" in record else None,
                A_1=record["A_1"] if "A_1" in record else None,
                B_1=record["B_1"] if "B_1" in record else None,
                sqrt_price_q96=record["sqrt_price_q96"]
                if "sqrt_price_q96" in record
                else None,
                tick=record["tick"] if "tick" in record else None,
                tick_spacing=record["tick_spacing"]
                if "tick_spacing" in record
                else None,
                liquidity=record["liquidity"] if "liquidity" in record else None,
                address=record["address"] if "address" in record else None,
                anchor=record["anchor"] if "anchor" in record else None,
                tkn0=record["tkn0_key"] if "tkn0_key" in record else None,
                tkn1=record["tkn1_key"] if "tkn1_key" in record else None,
                tkn0_key=record["tkn0_key"] if "tkn0_key" in record else None,
                tkn1_key=record["tkn1_key"] if "tkn1_key" in record else None,
                tkn0_address=record["tkn0_address"]
                if "tkn0_address" in record
                else None,
                tkn0_decimals=record["tkn0_decimals"]
                if "tkn0_decimals" in record
                else None,
                tkn1_address=record["tkn1_address"]
                if "tkn1_address" in record
                else None,
                tkn1_decimals=record["tkn1_decimals"]
                if "tkn1_decimals" in record
                else None,
            )
            for idx, record in enumerate(self.state)
        ]

    def get_tokens(self) -> List[Token]:
        # method implementation...
        return list(
            set(
                [
                    Token(
                        symbol=record["tkn0_symbol"]
                        if "tkn0_symbol" in record
                        else None,
                        decimals=record["tkn0_decimals"]
                        if "tkn0_decimals" in record
                        else None,
                        key=record["tkn0_key"] if "tkn0_key" in record else None,
                        address=record["tkn0_address"]
                        if "tkn0_address" in record
                        else None,
                    )
                    for record in self.state
                ]
                + [
                    Token(
                        symbol=record["tkn1_symbol"]
                        if "tkn1_symbol" in record
                        else None,
                        decimals=record["tkn1_decimals"]
                        if "tkn1_decimals" in record
                        else None,
                        key=record["tkn1_key"] if "tkn1_key" in record else None,
                        address=record["tkn1_address"]
                        if "tkn1_address" in record
                        else None,
                    )
                    for record in self.state
                ]
            )
        )

    def get_bnt_price_from_tokens(self, price, tkn) -> Decimal:
        # method implementation...
        return DeprecationWarning("Method not implemented")

    def get_token(self, key: str) -> Any:
        # method implementation...
        # print(f"[get_token] key: {key}")
        if "-" in key:
            return [tkn for tkn in self.get_tokens() if tkn.key == key][0]
        elif key.startswith("0x"):
            return [tkn for tkn in self.get_tokens() if tkn.address == key][0]
        else:
            raise ValueError(f"[get_token] Invalid token: {key}")

    def get_pool(self, **kwargs) -> Pool:
        return [
            pool
            for pool in self.get_pool_data_with_tokens()
            if all(getattr(pool, key) == kwargs[key] for key in kwargs)
        ][0]

    def get_pools(self) -> List[Pool]:
        # method implementation...
        return self.get_pool_data_with_tokens()

    def update_recently_traded_pools(self, cids: List[str]):
        # method implementation...
        return DeprecationWarning("Method not implemented")
