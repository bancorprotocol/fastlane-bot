# coding=utf-8
"""
Contains the manager class for pools. This class is responsible for handling pools and updating their state.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import List, Dict, Any, Callable, Optional

from web3 import Web3
from web3.contract import Contract

from fastlane_bot import Config
from fastlane_bot.events.interface import Pool
from fastlane_bot.events.managers.base import BaseManager
from fastlane_bot.events.pools import pool_factory


class PoolManager(BaseManager):
    def pool_key_from_info(self, pool_info: Dict[str, Any]) -> str:
        """
        Get the pool key from the pool info.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        Returns
        -------
        str
            The pool key.

        """
        if pool_info["exchange_name"] in self.cfg.ALL_FORK_NAMES_WITHOUT_CARBON + [
            "bancor_v2",
        ]:
            return pool_info["address"]
        elif pool_info["exchange_name"] in self.cfg.CARBON_V1_FORKS+["balancer"]:
            return pool_info["cid"]
        elif pool_info["exchange_name"] == "bancor_v3":
            return pool_info["tkn1_address"]
        elif pool_info["exchange_name"] == "bancor_pol":
            return pool_info["tkn0_address"]


    def pool_type_from_exchange_name(self, exchange_name: str) -> Callable:
        """
        Get the pool type from the exchange name.

        Parameters
        ----------
        exchange_name : str
            The exchange name.

        Returns
        -------
        Callable
            The pool type class.

        """
        return pool_factory.get_pool(exchange_name, self.cfg)

    def pool_extras_from_exchange_name(self, exchange_name: str) -> Dict:
        """
        Get the pool extras from the exchange name.

        Parameters
        ----------
        exchange_name : str
            The exchange name.

        Returns
        -------
        Dict
            The Dict containing any extras for the pool type

        """
        return pool_factory.get_fork_extras(exchange_name, self.cfg)

    @staticmethod
    def pool_descr_from_info(pool_info: Dict[str, Any]) -> str:
        """
        Get the pool description from the pool info.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        Returns
        -------
        str
            The pool description.

        """
        return (
            f"{pool_info['exchange_name']} {pool_info['pair_name']} {pool_info['fee']}"
        )

    @staticmethod
    def pool_cid_from_descr(web3: Web3, descr: str) -> str:
        """
        Get the pool CID from the description. Only used for non-Carbon pools.

        Parameters
        ----------
        web3 : Web3
            The Web3 instance.
        descr : str
            The description.

        Returns
        -------
        str
            The pool CID.

        """
        return web3.keccak(text=descr).hex()

    @property
    def pools(self) -> List[Pool]:
        """
        Get the pools from the exchanges.

        Returns
        -------
        List[Pool]
            The pools from the exchanges.
        """
        return [
            pool
            for exchange in self.exchanges.values()
            for pool in exchange.get_pools()
        ]

    def generate_pool_info(
        self,
        address,
        exchange_name,
        tkn0_address,
        tkn1_address,
        t0_symbol,
        t1_symbol,
        t0_decimals,
        t1_decimals,
        cid,
        strategy_id,
        fee,
        fee_float,
        block_number: int = None,
    ) -> Dict[str, Any]:
        """
        Generate the pool info.

        Parameters
        ----------
        address : str
            The address.
        exchange_name : str
            The exchange name.
        tkn0_address : str
            The token 0 address.
        tkn1_address : str
            The token 1 address.
        t0_symbol : str
            The token 0 symbol.
        t1_symbol : str
            The token 1 symbol.
        t0_decimals : int
            The token 0 decimals.
        t1_decimals : int
            The token 1 decimals.
        cid : str
            The cid.
        strategy_id : int
            The strategy id.
        fee : Any
            The fee.
        fee_float : float
            The fee float.
        block_number : int
            The block number

        Returns
        -------
        Dict[str, Any]
            The pool info.

        """
        pool_info = {
            "last_updated_block": block_number,
            "address": address,
            "exchange_name": exchange_name,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
            "tkn0_symbol": t0_symbol,
            "tkn1_symbol": t1_symbol,
            "tkn0_decimals": t0_decimals,
            "tkn1_decimals": t1_decimals,
            "cid": cid,
            "strategy_id": strategy_id,
            "pair_name": f"{tkn0_address}/{tkn1_address}",
            "fee_float": fee_float,
            "fee": fee,
        }
        pool_info["descr"] = self.pool_descr_from_info(pool_info)
        return pool_info

    def add_pool_info(
        self,
        address: str,
        exchange_name: str,
        fee: Any,
        fee_float: float,
        tkn0_address: str,
        tkn1_address: str,
        cid: Optional[str] = None,
        strategy_id: Optional[int] = None,
        other_args: Optional[Dict[str, Any]] = None,
        contract: Optional[Contract] = None,
        block_number: int = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
        """
        This is the main function for adding pool info.
        Parameters
        ----------
        address : str
            The address.
        exchange_name : str
            The exchange name.
        fee : Any
            The fee.
        fee_float : float
            The fee float.
        tkn0_address : str
            The token 0 address.
        tkn1_address : str
            The token 1 address.
        cid : Optional[str], optional
            The cid.
        other_args : Optional[Dict[str, Any]], optional
            The other args.
        contract : Optional[Contract], optional
            The contract.

        Returns
        -------
        Dict[str, Any]
            The pool info.


        """
        # Get or Create ERC20 contracts for each token
        t0_symbol, t0_decimals = self.get_tkn_info(tkn0_address)
        if not t0_symbol:
            return None
        t1_symbol, t1_decimals = self.get_tkn_info(tkn1_address)
        if not t1_symbol:
            return None

        # Generate pool info
        pool_info = self.generate_pool_info(
            address,
            exchange_name,
            tkn0_address,
            tkn1_address,
            t0_symbol,
            t1_symbol,
            t0_decimals,
            t1_decimals,
            cid,
            strategy_id,
            fee,
            fee_float,
            block_number,
        )

        # Add other args if necessary
        if other_args:
            pool_info.update(other_args)

        # Update cid if necessary
        unique_id = pool_info["descr"] if pool_info['exchange_name'] not in self.cfg.CARBON_V1_FORKS else (
            f"{pool_info['exchange_name']} {pool_info['strategy_id']} {pool_info['fee']}"
        )
        pool_info["cid"] = self.pool_cid_from_descr(self.web3, unique_id)

        # Add pool to exchange if necessary
        pool = self.get_or_init_pool(pool_info)
        assert pool, f"Pool not found in {exchange_name} pools"

        if contract:
            pool_info.update(
                pool.update_from_contract(
                    contract,
                    self.tenderly_fork_id,
                    self.w3_tenderly,
                    self.web3,
                    tenderly_exchanges,
                )
            )
        else:
            self.pool_data = [p for p in self.pool_data if p["cid"] != pool_info["cid"]]

        self.pool_data.append(pool_info)
        return pool_info

    def add_pool_to_exchange(self, pool_info: Dict[str, Any]):
        """
        Add a pool to the exchange.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        """
        #try:
        pool_type = self.pool_type_from_exchange_name(pool_info["exchange_name"])
        pool_extras = self.pool_extras_from_exchange_name(exchange_name=pool_info["exchange_name"], )
        pool = pool_type(state=pool_info, **pool_extras)
        self.exchanges[pool_info["exchange_name"]].add_pool(pool)
        # except Exception as e:
        #     print(f"Error adding pool to exchange: {e}, skipping...")

    def get_pool_info(
        self,
        key: str,
        key_value: str,
        ex_name: str,
        event: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the pool info.

        Parameters
        ----------
        key : str
            The key.
        key_value : str
            The key value.
        ex_name : str
            The exchange name.
        event : Optional[Dict[str, Any]], optional
            The event, by default None.

        Returns
        -------
        Optional[Dict[str, Any]]
            The pool info.
        """
        # if ex_name in self.cfg.UNI_V2_FORKS:
        #     ex_name = "uniswap_v2"

        if key == "address":
            key_value = self.web3.to_checksum_address(key_value)

        if ex_name == "bancor_pol":
            key = "tkn0_address"

        if ex_name == "bancor_v2":
            return next(
                (
                    self.validate_pool_info(key_value, event, pool, key)
                    for pool in self.pool_data
                    if pool[key[0]] == key_value[0]
                    and pool[key[1]] == key_value[1]
                    and pool["exchange_name"] == ex_name
                ),
                None,
            )

        return next(
            (
                self.validate_pool_info(key_value, event, pool, key)
                for pool in self.pool_data
                if pool[key] == key_value and pool["exchange_name"] == ex_name
            ),
            None,
        )

    def update_pool_data(self, pool_info: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Update the pool data.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.
        data : Dict[str, Any]
            The data.
        """
        for pool in self.pool_data:
            if pool["cid"] == pool_info["cid"]:
                pool.update(data)
                break

    def get_or_init_pool(self, pool_info: Dict[str, Any]) -> Pool:
        """
        Get or init the pool.

        Parameters
        ----------
        pool_info : Dict[str, Any]
            The pool info.

        Returns
        -------
        Pool
            The pool.
        """
        key = self.pool_key_from_info(pool_info)

        pool = self.exchanges[pool_info["exchange_name"]].get_pool(key)
        if not pool:
            self.add_pool_to_exchange(pool_info)
            key = self.pool_key_from_info(pool_info)
            pool = self.exchanges[pool_info["exchange_name"]].get_pool(key)
        return pool
