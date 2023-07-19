# coding=utf-8
"""
Contains the manager class for events. This class is responsible for handling events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import random
import time
from typing import Dict, Any, Optional

from web3.contract import Contract

from fastlane_bot.events.managers.contracts import ContractsManager
from fastlane_bot.events.managers.events import EventManager
from fastlane_bot.events.managers.pools import PoolManager


class Manager(PoolManager, EventManager, ContractsManager):
    def update_from_event(
        self, event: Dict[str, Any], block_number: int = None
    ) -> None:
        """
        Updates the state of the pool data from an event.

        Parameters
        ----------
        event  : Dict[str, Any]
            The event.
        block_number : int, optional
            The block number, by default None

        """
        addr = self.web3.toChecksumAddress(event["address"])
        ex_name = self.exchange_name_from_event(event)

        if not ex_name:
            return

        key, key_value = self.get_key_and_value(event, addr, ex_name)
        pool_info = self.get_pool_info(
            key, key_value, ex_name
        ) or self.add_pool_info_from_contract(
            address=addr, event=event, exchange_name=ex_name
        )
        if not pool_info:
            return

        pool = self.get_or_init_pool(pool_info)
        data = pool.update_from_event(
            event or {}, pool.get_common_data(event, pool_info) or {}
        )

        if event["event"] == "StrategyDeleted":
            self.handle_strategy_deleted(event)
            return
        self.update_pool_data(pool_info, data)

    def update_from_pool_info(
        self, pool_info: Optional[Dict[str, Any]] = None, current_block: int = None
    ) -> Dict[str, Any]:
        """
        Update the pool info.

        Parameters
        ----------
        pool_info : Optional[Dict[str, Any]], optional
            The pool info, by default None.
        current_block : int, optional
            The current block, by default None.
        """
        pool_info["last_updated_block"] = (
            self.web3.eth.blockNumber if current_block is None else current_block
        )
        contract = (
            self.pool_contracts[pool_info["exchange_name"]].get(
                pool_info["address"],
                self.web3.eth.contract(
                    address=pool_info["address"],
                    abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
                ),
            )
            if pool_info["exchange_name"] != "bancor_v3"
            else self.pool_contracts[pool_info["exchange_name"]].get(
                self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS
            )
        )
        pool = self.get_or_init_pool(pool_info)
        params = pool.update_from_contract(contract)
        for key, value in params.items():
            pool_info[key] = value
        return pool_info

    def update_from_contract(
        self,
        address: str = None,
        contract: Optional[Contract] = None,
        pool_info: Optional[Dict[str, Any]] = None,
        block_number: int = None,
    ) -> Dict[str, Any]:
        """
        Update the state from the contract (instead of events).

        Parameters
        ----------
        address : str, optional
            The address, by default None.
        contract : Optional[Contract], optional
            The contract, by default None.
        pool_info : Optional[Dict[str, Any]], optional
            The pool info, by default None.
        block_number : int, optional
            The block number, by default None.

        Returns
        -------
        Dict[str, Any]
            The pool info.
        """
        if pool_info:
            address = pool_info["address"]

        addr = self.web3.toChecksumAddress(address)

        if not pool_info:
            for pool in self.pool_data:
                if pool["address"] == addr:
                    pool_info = pool
                    break

        pool_info = self.validate_pool_info(addr=addr, pool_info=pool_info)
        if not pool_info:
            return

        pool_info["last_updated_block"] = (
            block_number if block_number is not None else self.web3.eth.blockNumber
        )
        if contract is None:
            contract = self.pool_contracts[pool_info["exchange_name"]].get(
                pool_info["address"],
                self.web3.eth.contract(
                    address=pool_info["address"],
                    abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
                ),
            )
        pool = self.get_or_init_pool(pool_info)
        params = pool.update_from_contract(contract)
        for key, value in params.items():
            pool_info[key] = value
        return pool_info

    def update(
        self,
        event: Dict[str, Any] = None,
        address: str = None,
        pool_info: Dict[str, Any] = None,
        contract: Contract = None,
        limiter: bool = True,
        block_number: int = None,
    ) -> None:
        """
        Update the state.

        Parameters
        ----------
        event : Dict[str, Any], optional
            The event, by default None.
        address : str, optional
            The address, by default None.
        pool_info : Dict[str, Any], optional
            The pool info, by default None.
        contract : Contract, optional
            The contract, by default None.
        limiter : bool, optional
            Whether to use the rate limiter, by default True.
        block_number : int, optional
            The block number, by default None.


        Raises
        ------
        Exception
            If the alchemy rate limit is hit.
            If no event or pool info is provided.
            If the pool info is invalid.
        """
        while True:
            if limiter:
                rate_limiter = 0.1 + 0.9 * random.random()
                time.sleep(rate_limiter)
            try:
                if event:
                    self.update_from_event(event=event, block_number=block_number)
                elif address:
                    self.update_from_contract(
                        address, contract, block_number=block_number
                    )
                elif pool_info:
                    self.update_from_pool_info(
                        pool_info=pool_info, current_block=block_number
                    )
                else:
                    self.cfg.logger.debug(
                        f"No event or pool info provided {event} {address} {contract}"
                    )
                    break
                break
            except Exception as e:
                if all(
                    err_msg not in str(e)
                    for err_msg in ["Too Many Requests for url", "format_name"]
                ):
                    self.cfg.logger.error(f"Error updating pool: {e} {address} {event}")
                    break
                else:
                    time.sleep(rate_limiter)
