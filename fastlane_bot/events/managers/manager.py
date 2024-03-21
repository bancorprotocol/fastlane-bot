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

from fastlane_bot.data.abi import BANCOR_V3_NETWORK_INFO_ABI
from fastlane_bot.events.managers.contracts import ContractsManager
from fastlane_bot.events.managers.events import EventManager
from fastlane_bot.events.managers.pools import PoolManager
from fastlane_bot.events.pools.utils import get_pool_cid


class Manager(PoolManager, EventManager, ContractsManager):
    def update_from_event(self, event: Dict[str, Any]):
        """
        Updates the state of the pool data from an event. StrategyCreated and StrategyUpdated events are handled as
        the "default" event types to process.

        Args:
            event (Dict[str, Any]): The event to process.

        """
        ex_name = self.exchange_name_from_event(event)
        if event["event"] in ["TradingFeePPMUpdated", "PairTradingFeePPMUpdated"]:
            self.handle_trading_fee_updated()
            return

        if event["event"] == "PairCreated":
            self.set_carbon_v1_fee_pairs()
            return

        if event["event"] == "StrategyDeleted":
            self.handle_strategy_deleted(event)
            return

        addr = self.web3.to_checksum_address(event["address"])
        if not ex_name:
            return

        key, key_value = self.get_key_and_value(event, addr, ex_name)
        pool_info = self.get_pool_info(key, key_value, ex_name)
        if not pool_info:
            # StrategyCreated events get appended to this list to be processed in the async workflow (see main.py),
            # to gather any currently unknown fee and token info. Then the event will be reprocessed in this method
            # and the pool data liquidity will be updated at that time (second pass).
            self.pools_to_add_from_contracts.append(
                (addr, ex_name, event, key, key_value)
            )
            return

        if "descr" not in pool_info:
            pool_info["descr"] = self.pool_descr_from_info(pool_info)

        pool = self.get_or_init_pool(pool_info)
        data = pool.update_from_event(
            event or {}, pool.get_common_data(event, pool_info)
        )
        self.update_pool_data(pool_info, data)

    # def handle_pair_created(self, event: Dict[str, Any]):
    #     """
    #     Handle the pair created event by updating the fee pairs and pool info for the given pair.
    #
    #     Parameters
    #     ----------
    #     event : Dict[str, Any]
    #         The event.
    #
    #     """
    #     for exchange_name in self.cfg.CARBON_V1_FORKS:
    #         if exchange_name in self.exchanges:
    #             fee_pairs = self.set_carbon_v1_fee_pairs()
    #             self.fee_pairs[exchange_name].update(fee_pairs)

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
        if "last_updated_block" in pool_info:
            if (
                    type(pool_info["last_updated_block"]) == int
                    and pool_info["last_updated_block"] == current_block
            ):
                return pool_info
        else:
            pool_info["last_updated_block"] = current_block

        if pool_info["exchange_name"] == self.cfg.BANCOR_V3_NAME:
            contract = self.pool_contracts[pool_info["exchange_name"]].get(
                self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS,
                self.web3.eth.contract(
                    address=self.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS,
                    abi=BANCOR_V3_NETWORK_INFO_ABI,
                ),
            )
        elif pool_info["exchange_name"] == self.cfg.BALANCER_NAME:
            contract = self.pool_contracts[pool_info["exchange_name"]].get(
                self.cfg.BALANCER_VAULT_ADDRESS,
                self.web3.eth.contract(
                    address=self.cfg.BALANCER_VAULT_ADDRESS,
                    abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
                ),
            )
        else:
            contract = self.pool_contracts[pool_info["exchange_name"]].get(
                pool_info["address"],
                self.web3.eth.contract(
                    address=pool_info["address"],
                    abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
                ),
            )
        pool = self.get_or_init_pool(pool_info)
        params = pool.update_from_contract(
            contract, self.tenderly_fork_id, self.w3_tenderly, self.web3
        )
        for key, value in params.items():
            pool_info[key] = value

        if "descr" not in pool_info or not pool_info["descr"]:
            pool_info["descr"] = self.pool_descr_from_info(pool_info)

        # update the pool_data where the cids match
        for idx, pool in enumerate(self.pool_data):
            if pool["cid"] == pool_info["cid"]:
                self.pool_data[idx] = pool_info
                break
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
        # if pool_info:
        #     address = pool_info["address"]
        #
        # addr = self.web3.to_checksum_address(address)
        #
        # if not pool_info:
        #     for pool in self.pool_data:
        #         if pool["address"] == addr:
        #             pool_info = pool
        #             break
        #
        # pool_info = self.validate_pool_info(addr=addr, pool_info=pool_info)
        # if not pool_info:
        #     return
        #
        # pool_info["descr"] = self.pool_descr_from_info(pool_info)
        # pool_info["last_updated_block"] = block_number
        # if contract is None:
        #     contract = self.pool_contracts[pool_info["exchange_name"]].get(
        #         pool_info["address"],
        #         self.web3.eth.contract(
        #             address=pool_info["address"],
        #             abi=self.exchanges[pool_info["exchange_name"]].get_abi(),
        #         ),
        #     )
        # pool = self.get_or_init_pool(pool_info)
        # params = pool.update_from_contract(
        #     contract,
        #     tenderly_fork_id=self.tenderly_fork_id,
        #     w3_tenderly=self.w3_tenderly,
        #     w3=self.web3,
        # )
        # for key, value in params.items():
        #     pool_info[key] = value
        return pool_info

    def update(
            self,
            event: Dict[str, Any] = None,
            address: str = None,
            token_address: bool = False,
            pool_info: Dict[str, Any] = None,
            contract: Contract = None,
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
        token_address: str, optional
            If the balance should be updated using an ERC20 contract.
        pool_info : Dict[str, Any], optional
            The pool info, by default None.
        contract : Contract, optional
            The contract, by default None.
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
            try:
                if event:
                    self.update_from_event(event=event)
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
                if "Too Many Requests for url" in str(e):
                    time.sleep(random.random())
                    return self.update(
                        event,
                        address,
                        token_address,
                        pool_info,
                        contract,
                        block_number,
                    )
                elif "format_name" not in str(e):
                    self.cfg.logger.error(f"Error updating pool: {e} {address} {event}")
                    if "ERC721:" not in str(e):
                        raise e
                    break
                else:
                    rate_limiter = 0.1 + 0.9 * random.random()
                    time.sleep(random.random())

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

        for exchange_name in self.cfg.CARBON_V1_FORKS:
            if exchange_name in self.exchanges:

                fee = self.fee_pairs[exchange_name][(tkn0_address, tkn1_address)]

                for idx, pool in enumerate(self.pool_data):
                    if (
                            pool["tkn0_address"] == tkn0_address
                            and pool["tkn1_address"] == tkn1_address
                            and pool["exchange_name"] == exchange_name
                    ):
                        self._handle_pair_trading_fee_updated(fee, pool, idx)
                    elif (
                            pool["tkn0_address"] == tkn1_address
                            and pool["tkn1_address"] == tkn0_address
                            and pool["exchange_name"] == exchange_name
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
        for exchange_name in self.cfg.CARBON_V1_FORKS:
            if exchange_name in self.exchanges:

                # Create or get CarbonController contract object
                carbon_controller = self.create_or_get_carbon_controller(exchange_name)

                # Get pairs by state
                pairs = self.get_carbon_pairs(carbon_controller, exchange_name)

                # Update fee pairs
                self.fee_pairs[exchange_name] = self.get_fee_pairs(pairs, carbon_controller)

                # Update pool info
                for idx, pool in enumerate(self.pool_data):
                    if pool["exchange_name"] == exchange_name:
                        pool["fee"] = self.fee_pairs[exchange_name][
                            (pool["tkn0_address"], pool["tkn1_address"])
                        ]
                        pool["fee_float"] = pool["fee"] / 1e6
                        pool["descr"] = self.pool_descr_from_info(pool)
                        self.pool_data[idx] = pool


    def update_remaining_pools(self):
        remaining_pools = []
        all_events = [pool[2] for pool in self.pools_to_add_from_contracts]
        for event in all_events:
            addr = self.web3.to_checksum_address(event["address"])
            ex_name = self.exchange_name_from_event(event)
            if not ex_name:
                self.cfg.logger.warning("[run_async_update_with_retries] ex_name not found from event")
                continue

            key, key_value = self.get_key_and_value(event, addr, ex_name)
            pool_info = self.get_pool_info(key, key_value, ex_name)

            if not pool_info:
                remaining_pools.append((addr, ex_name, event, key, key_value))

        random.shuffle(remaining_pools)
        self.pools_to_add_from_contracts = remaining_pools
