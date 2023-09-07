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
        if event["event"] == "TradingFeePPMUpdated":
            self.handle_trading_fee_updated()
            return

        if event["event"] == "PairTradingFeePPMUpdated":
            self.handle_pair_trading_fee_updated(event)
            return

        if event["event"] == "PairCreated":
            self.handle_pair_created(event)
            return
        if event["event"] == "StrategyDeleted":
            self.handle_strategy_deleted(event)
            return

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

        self.update_pool_data(pool_info, data)

    def handle_pair_created(self, event: Dict[str, Any]):
        """
        Handle the pair created event by updating the fee pairs and pool info for the given pair.

        Parameters
        ----------
        event : Dict[str, Any]
            The event.

        """
        fee_pairs = self.get_fee_pairs(
            [(event["args"]["token0"], event["args"]["token1"], 0, 5000)],
            self.create_or_get_carbon_controller(),
        )
        self.fee_pairs.update(fee_pairs)

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

        pool_info["last_updated_block"] = current_block
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
        params = pool.update_from_contract(contract, cfg=self.cfg)
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

        pool_info["last_updated_block"] = block_number
        if contract is None:
            contract = self.pool_contracts[pool_info["exchange_name"]].get(
                pool_info["address"],
                self.web3.eth.contract(
                    address=pool_info["address"],
                    abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
                ),
            )
        pool = self.get_or_init_pool(pool_info)
        params = pool.update_from_contract(contract, cfg=self.cfg)
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
            else:
                rate_limiter = 0
            try:
                if event:
                    self.cfg.logger.debug("update from event")
                    self.update_from_event(event=event, block_number=block_number)
                elif address:
                    self.cfg.logger.debug("update from address")
                    self.update_from_contract(
                        address, contract, block_number=block_number
                    )
                elif pool_info:
                    self.cfg.logger.debug("update from pool info")
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
                    for err_msg in [
                        "Too Many Requests for url",
                        "format_name",
                    ]
                ):
                    self.cfg.logger.error(f"Error updating pool: {e} {address} {event}")
                    if "ERC721:" not in str(e):
                        raise e
                    break
                else:
                    time.sleep(rate_limiter)

    def handle_pair_trading_fee_updated(
        self,
        event: Dict[str, Any] = None,
    ):
        """
        Handle the pair trading fee updated event by updating the fee pairs and pool info for the given pair.

        Parameters
        ----------
        event : Dict[str, Any], optional
            The event, by default None.
        """
        tkn0_address = event["args"]["token0"]
        tkn1_address = event["args"]["token1"]
        fee = event["args"]["newFeePPM"]

        self.fee_pairs[(tkn0_address, tkn1_address)] = fee

        for idx, pool in enumerate(self.pool_data):
            if (
                pool["tkn0_address"] == tkn0_address
                and pool["tkn1_address"] == tkn1_address
                and pool["exchange_name"] == "carbon_v1"
            ):
                self._handle_pair_trading_fee_updated(fee, pool, idx)
            elif (
                pool["tkn0_address"] == tkn1_address
                and pool["tkn1_address"] == tkn0_address
                and pool["exchange_name"] == "carbon_v1"
            ):
                self._handle_pair_trading_fee_updated(fee, pool, idx)

    def _handle_pair_trading_fee_updated(
        self, fee: int, pool: Dict[str, Any], idx: int
    ):
        """
        Handle the pair trading fee updated event by updating the fee pairs and pool info for the given pair.

        Parameters
        ----------
        fee : int
            The fee.
        pool : Dict[str, Any]
            The pool.
        idx : int
            The index of the pool.

        """
        pool["fee"] = f"{fee}"
        pool["fee_float"] = fee / 1e6
        pool["descr"] = self.pool_descr_from_info(pool)
        self.pool_data[idx] = pool

    def handle_trading_fee_updated(self):
        """
        Handle the trading fee updated event by updating the fee pairs and pool info for all pools.
        """

        # Create or get CarbonController contract object
        carbon_controller = self.create_or_get_carbon_controller()

        # Get pairs by state
        pairs = self.get_carbon_pairs(carbon_controller)

        # Update fee pairs
        self.fee_pairs = self.get_fee_pairs(pairs, carbon_controller)

        # Update pool info
        for pool in self.pool_data:
            if pool["exchange_name"] == "carbon_v1":
                pool["fee"] = self.fee_pairs[
                    (pool["tkn0_address"], pool["tkn1_address"])
                ]
                pool["fee_float"] = pool["fee"] / 1e6
                pool["descr"] = self.pool_descr_from_info(pool)
