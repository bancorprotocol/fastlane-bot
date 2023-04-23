"""
Database updater object for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from brownie import Contract
from web3._utils.filters import LogFilter
from web3.datastructures import AttributeDict

from fastlane_bot.data.abi import BANCOR_V2_CONVERTER_ABI, BANCOR_V3_POOL_COLLECTION_ABI, UNISWAP_V2_POOL_ABI, \
    UNISWAP_V3_POOL_ABI
from fastlane_bot.db.manager import DatabaseManager
import fastlane_bot.config as c
import fastlane_bot.db.models as models


@dataclass
class EventHandler:
    """
    Processes events from the Ethereum network and updates the database accordingly

    Parameters
    ----------
    db: fastlane_bot.db.manager.DatabaseManager
        The database manager to use
    poll_interval: int
        The number of seconds to wait between polling the Ethereum network for new events
    test_sample_size: int
        The number of pools to use for testing. If None, all pools will be used.

    """

    db: DatabaseManager
    poll_interval: int = c.DEFAULT_POLL_INTERVAL
    filters: List[Any] = field(default_factory=list)

    def __post_init__(self):


        self.exchange_list = self.db.exchange_list

        if (
            c.UNISWAP_V2_NAME in self.exchange_list
            and c.SUSHISWAP_V2_NAME in self.exchange_list
        ):
            self.exchange_list.remove(c.SUSHISWAP_V2_NAME)

        self.filters = self._get_event_filters(self.exchange_list)
        c.logger.info("Starting event handler with the following exchanges:")
        c.logger.info(f"{self.exchange_list}")

    def _get_event_filters(self, exchanges: [str]) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        Parameters
        ----------
        exchanges: [str]
            The list of exchanges to get the filters for

        Returns
        -------
        filters: [AttributeDict]
            The list of filters for the relevant events
        """
        filters = []
        if c.BANCOR_V2_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(c.BANCOR_V2_NAME)
            contract = self._get_contract_for_exchange(exchange=c.BANCOR_V2_NAME)
            filters.append(
                {
                    "exchange": c.BANCOR_V2_NAME,
                    "_filter": contract.events.TokenRateUpdate.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
        if c.BANCOR_V3_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(c.BANCOR_V3_NAME)
            contract = self._get_contract_for_exchange(exchange=c.BANCOR_V3_NAME)
            filters.append(
                {
                    "exchange": c.BANCOR_V3_NAME,
                    "_filter": contract.events.TradingLiquidityUpdated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
        if c.UNISWAP_V2_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(c.UNISWAP_V2_NAME)
            contract = self._get_contract_for_exchange(exchange=c.UNISWAP_V2_NAME)
            filters.append(
                {
                    "exchange": c.UNISWAP_V2_NAME,
                    "_filter": contract.events.Sync.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

        if c.UNISWAP_V3_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(c.UNISWAP_V3_NAME)
            contract = self._get_contract_for_exchange(exchange=c.UNISWAP_V3_NAME)
            filters.append(
                {
                    "exchange": c.UNISWAP_V3_NAME,
                    "_filter": contract.events.Swap.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

        if c.CARBON_V1_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(c.CARBON_V1_NAME)
            contract = self._get_contract_for_exchange(exchange=c.CARBON_V1_NAME)
            filters.extend(
                (
                    {
                        "exchange": c.CARBON_STRATEGY_CREATED,
                        "_filter": contract.events.StrategyCreated.createFilter(
                            fromBlock=from_block, toBlock="latest"
                        ),
                    },
                    {
                        "exchange": c.CARBON_STRATEGY_DELETED,
                        "_filter": contract.events.StrategyDeleted.createFilter(
                            fromBlock=from_block, toBlock="latest"
                        ),
                    },
                    {
                        "exchange": c.CARBON_STRATEGY_UPDATED,
                        "_filter": contract.events.StrategyUpdated.createFilter(
                            fromBlock=from_block, toBlock="latest"
                        ),
                    },
                )
            )
        return filters

    @staticmethod
    def _carbon_v1_data(processed_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets the pool data for Carbon v1 events

        Parameters
        ----------
        processed_event : Dict[str, Any]
            The processed event

        Returns
        -------
        Dict[str, Any]
            The pool data
        """
        return {
            "exchange_name": c.CARBON_V1_NAME,
            "pool_contract": c.CARBON_CONTROLLER_CONTRACT,
            "tkn0_address": processed_event["token0"],
            "tkn1_address": processed_event["token1"],
            "pool_address": c.CARBON_CONTROLLER_ADDRESS,
            "cid": processed_event["id"]
        }

    def _bancor_v3_data(self, next_cid: int, processed_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets the pool data for Bancor v3 events

        Parameters
        ----------
        next_cid : int
            The next cid
        processed_event : Dict[str, Any]
            The processed event

        Returns
        -------
        Dict[str, Any]
            The pool data
        """
        return {
            "exchange_name": c.BANCOR_V3_NAME,
            "pool_contract": c.BANCOR_NETWORK_INFO_CONTRACT,
            "tkn0_address": c.BNT_ADDRESS,
            "tkn1_address": processed_event["pool"],
            "pool_address": c.BANCOR_V3_NETWORK_INFO_ADDRESS,
            "cid": self.db.next_cid
        }

    def _default_data(self, exchange_name: str, pool_identifier: str) -> Dict[str, Any]:
        """
        Gets the pool data for a default exchange

        Parameters
        ----------
        next_cid : int
            The next cid
        exchange_name : str
            The name of the exchange
        pool_identifier : str
            The identifier of the pool

        Returns
        -------
        Dict[str, Any]
            The pool data
        """
        pool_contract = self.db.contract_from_address(exchange_name, pool_identifier)
        tkn0_address, tkn1_address = self.db.get_token_addresses_for_pool(exchange_name, pool_identifier,
                                                                                  pool_contract)
        return {
            "exchange_name": exchange_name,
            "pool_contract": pool_contract,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
            "pool_address": pool_identifier,
            "cid": self.db.next_cid
        }

    def _create_pool_from_event(self, exchange_name: str, pool_identifier: str,
                                processed_event: Dict[str, Any]) -> models.Pool:
        """
        Creates a pool in the database from an event

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_identifier : str
            The identifier of the pool
        processed_event : Dict[str, Any]
            The processed event

        Returns
        -------
        models.Pool
            The Pool object

        """
        block_number, cid, pool_address, pool_contract, tkn0_address, tkn1_address, exchange_name = self._parse_processed_event(
            exchange_name, pool_identifier, processed_event
        )
        tkn0 = self.db.get_or_create_token(tkn0_address)
        tkn1 = self.db.get_or_create_token(tkn1_address)
        pair = self.db.get_or_create_pair(tkn0_address, tkn1_address)
        common_data = dict(
            cid=str(cid),
            exchange_name=exchange_name,
            pair_name=pair.name,
            tkn0_address=tkn0_address,
            tkn1_address=tkn1_address,
            tkn0_key=tkn0.key,
            tkn1_key=tkn1.key,
            pool_address=pool_address,
            last_updated_block=block_number,
        )
        other_params = {"fee": self.db.get_pool_fee(exchange_name, pool_contract)}
        carbon_params = (
            {
                "y_0": processed_event["order0"][0],
                "z_0": processed_event["order0"][1],
                "A_0": processed_event["order0"][2],
                "B_0": processed_event["order0"][3],
                "y_1": processed_event["order1"][0],
                "z_1": processed_event["order1"][1],
                "A_1": processed_event["order1"][2],
                "B_1": processed_event["order1"][3],
            }
            if exchange_name == c.CARBON_V1_NAME
            else {}
        )
        all_params = common_data | other_params | carbon_params
        c.logger.debug(f"all_params={all_params}")
        try:
            pool = models.Pool(**all_params)
            self.db.session.add(pool)
            self.db.session.commit()
            c.logger.info(f"Successfully created pool!!!: {all_params}")
        except Exception as e:
            self.db._rollback_and_log(e)
            pool = None
        return pool

    def _parse_processed_event(self, exchange_name: str, pool_identifier: str, processed_event: Dict[str, Any]):
        """
        Parses the processed event to get the pool's data

        Parameters
        ----------
        exchange_name : str
            The name of the exchange
        pool_identifier : str
            The identifier of the pool
        processed_event : Dict[str, Any]
            The processed event

        Returns
        -------
        Tuple[int, str, str, Any, str, str, str]
            The block number, the cid, the pool address, the pool contract, the tkn0 address, the tkn1 address, the exchange name

        """
        block_number = processed_event["block_number"]
        pool_data = (
            self._carbon_v1_data(processed_event) if c.CARBON_V1_NAME in exchange_name
            else self._bancor_v3_data(processed_event) if exchange_name == c.BANCOR_V3_NAME
            else self._default_data(exchange_name, pool_identifier)
        )

        return (
            block_number,
            pool_data["cid"],
            pool_data["pool_address"],
            pool_data["pool_contract"],
            pool_data["tkn0_address"],
            pool_data["tkn1_address"],
            pool_data["exchange_name"],
        )

    def _handle_pool_update_from_event(self, exchange: str, event_log: Any, event_type: str = None):
        """
        Handles an event log from the Ethereum network

        Parameters
        ----------
        exchange: str
            The name of the exchange the event came from
        event_log: Any
            The event log to process
        event_type: str
            The type of event to process
        """
        processed_event = self.build_processed_event(event_log, exchange)
        pool_identifier = self._get_pool_identifier(event_log, exchange)
        (
            block_number,
            cid,
            pool_address,
            pool_contract,
            tkn0_address,
            tkn1_address,
            exchange,
        ) = self._parse_processed_event(
            exchange, pool_identifier, processed_event
        )

        c.logger.debug(
            f"Getting or creating pool for processed_event= {processed_event}, pool_identifier = {pool_identifier}"
        )
        pool = self.db.get_or_create_pool(
            exchange_name=exchange,
            pool_identifier=pool_identifier,
            processed_event=processed_event,
        )
        if pool:
            c.logger.debug(f"Pool found: {pool}")

            pool.last_updated_block = block_number

            if pool.exchange_name == c.BANCOR_V3_NAME:
                pool = self._update_bancor3_liquidity(pool, processed_event)

            elif pool.exchange_name == c.UNISWAP_V3_NAME:
                pool = self._update_uni3_liquidity(pool, processed_event)

            elif pool.exchange_name in c.UNIV2_FORKS + [c.BANCOR_V2_NAME]:
                pool = self._update_other_liquidity(pool, processed_event)

            elif c.CARBON_V1_NAME in pool.exchange_name:
                pool = self._update_carbon_liquidity(
                    cid, event_type, pool, processed_event
                )
            self.db._add_or_update(block_number, cid, pool)

    def _update_carbon_liquidity(self, cid: int, event_type: str, pool: models.Pool, processed_event: Dict[str, Any]) -> models.Pool:
        """
        Updates the liquidity of a Carbon pool

        Parameters
        ----------
        cid: int
            The cid of the pool
        event_type: str
            The type of event to process
        pool: models.Pool
            The pool to update
        processed_event: Dict[str, Any]
            The processed event to update the pool with

        Returns
        -------
        models.Pool
            The updated pool
        """
        if event_type == "delete":
            self.db.delete_carbon_strategy(cid)
        else:
            pool = self._handle_carbon_pool_update(cid, pool, processed_event)
        return pool

    def _update_other_liquidity(self, pool: models.Pool, processed_event: Dict[str, Any]) -> models.Pool:
        """
        Updates the liquidity of a Uniswap V2 or Sushiswap pool

        Parameters
        ----------
        pool: models.Pool
            The pool to update
        processed_event: Dict[str, Any]
            The processed event to update the pool with

        Returns
        -------
        models.Pool
            The updated pool
        """
        pool.tkn0_balance = processed_event["tkn0_balance"]
        pool.tkn1_balance = processed_event["tkn1_balance"]
        return pool

    def _update_uni3_liquidity(self, pool: models.Pool, processed_event: Dict[str, Any]) -> models.Pool:
        """
        Updates the liquidity of a Uniswap V3 pool

        Parameters
        ----------
        pool: models.Pool
            The pool to update
        processed_event: Dict[str, Any]
            The processed event to update the pool with

        Returns
        -------
        models.Pool
            The updated pool
        """
        pool.sqrt_price_q96 = processed_event["sqrt_price_q96"]
        pool.liquidity = processed_event["liquidity"]
        pool.tick = processed_event["tick"]
        return pool

    def _update_bancor3_liquidity(self, pool: models.Pool, processed_event: Dict[str, Any]) -> models.Pool:
        """
        Updates the liquidity of a Bancor V3 pool

        Parameters
        ----------
        pool: models.Pool
            The pool to update
        processed_event: Dict[str, Any]
            The processed event to update the pool with

        Returns
        -------
        models.Pool
            The updated pool
        """
        if processed_event["token"] == c.BNT_ADDRESS:
            pool.tkn0_balance = processed_event["newLiquidity"]
        else:
            pool.tkn1_balance = processed_event["newLiquidity"]
        return pool

    def _get_pool_identifier(self, event_log: Any, exchange: str) -> str:
        """
        Gets the pool identifier from the event log

        Parameters
        ----------
        event_log: Any
            The event log to get the pool identifier from
        exchange: str
            The name of the exchange the event came from

        Returns
        -------
        str
            The pool identifier
        """
        if c.CARBON_V1_NAME in exchange:
            return event_log["args"].get("id")
        elif exchange == c.BANCOR_V3_NAME:
            return event_log["args"].get("pool")
        else:
            return event_log["address"]

    def _handle_carbon_pool_update(
        self, cid: int, pool: models.Pool, processed_event: Dict[str, Any]
    ) -> models.Pool:
        """
        Handles a carbon pool update

        Parameters
        ----------
        cid: int
            The carbon pool id
        pool: models.Pool
            The pool to update
        processed_event: Dict[str, Any]
            The processed event to update the pool with

        Returns
        -------
        models.Pool
            The updated pool
        """
        pool.cid = str(cid)
        pool.y_0 = processed_event["order0"][0]
        pool.z_0 = processed_event["order0"][1]
        pool.A_0 = processed_event["order0"][2]
        pool.B_0 = processed_event["order0"][3]
        pool.y_1 = processed_event["order1"][0]
        pool.z_1 = processed_event["order1"][1]
        pool.A_1 = processed_event["order1"][2]
        pool.B_1 = processed_event["order1"][3]
        return pool

    @staticmethod
    def build_processed_event(event_log: AttributeDict, exchange: str) -> Dict[str, Any]:
        """
        Builds a processed event from the event log and exchange name

        Parameters
        ----------
        event_log: AttributeDict
            The event log to process
        exchange: str
            The name of the exchange the event came from

        Returns
        -------
        Dict[str, Any]
            The processed event
        """
        block_number = event_log["blockNumber"]
        args = event_log["args"]
        processed_event = {"block_number": block_number}

        if exchange == c.BANCOR_V3_NAME:
            processed_event.update(
                {"pool": args.get("pool"), "token": args.get("token"), "newLiquidity": args.get("newLiquidity")}
            )
        elif exchange in c.UNIV2_FORKS + [c.BANCOR_V2_NAME]:
            processed_event.update({"tkn0_balance": args.get("reserve0"), "tkn1_balance": args.get("reserve1")})
        elif exchange == c.UNISWAP_V3_NAME:
            processed_event.update(
                {
                    "sqrt_price_q96": args.get("sqrtPriceX96"),
                    "liquidity": args.get("liquidity"),
                    "tick": args.get("tick"),
                    "tick_spacing": args.get("tickSpacing"),
                }
            )
        elif c.CARBON_V1_NAME in exchange:
            processed_event.update({"token0": args.get("token0"), "token1": args.get("token1")})
            if args.get("pairId"):
                return processed_event
            else:
                processed_event.update(
                    {"id": args.get("id"), "order0": args.get("order0"), "order1": args.get("order1")}
                )
        return processed_event

    def _get_contract_for_exchange(
        self, exchange: str = None, pool_address: str = None, init_contract=True
    ) -> Contract:
        """
        Get the relevant ABI for the exchange

        Parameters
        ----------
        exchange : str
            exchange name
        pool_address : str
            pool address
        init_contract : bool
            whether to initialize the contract or not

        Returns
        -------
        Contract
            contract object

        """
        if exchange == c.BANCOR_V2_NAME:
            return c.w3.eth.contract(abi=BANCOR_V2_CONVERTER_ABI, address=pool_address)
        elif exchange == c.BANCOR_V3_NAME:
            if init_contract:
                return c.w3.eth.contract(
                    abi=BANCOR_V3_POOL_COLLECTION_ABI,
                    address=c.w3.toChecksumAddress(c.BANCOR_V3_POOL_COLLECTOR_ADDRESS),
                )
            else:
                return c.BANCOR_NETWORK_INFO_CONTRACT

        elif exchange in c.UNIV2_FORKS:
            return c.w3.eth.contract(abi=UNISWAP_V2_POOL_ABI, address=pool_address)

        elif exchange == c.UNISWAP_V3_NAME:
            return c.w3.eth.contract(abi=UNISWAP_V3_POOL_ABI, address=pool_address)

        elif c.CARBON_V1_NAME in exchange:
            return c.CARBON_CONTROLLER_CONTRACT

    def get_pair_name_from_contract(self, contract: Contract) -> str:
        """
        Get the pair name from the contract

        Parameters
        ----------
        contract : Contract
            contract object

        Returns
        -------
        str
            pair name
        """
        tkn0_address = contract.caller.token0()
        tkn0_key = self.db.tkn_from_address(tkn0_address).key
        tkn1_address = contract.caller.token1()
        tkn1_key = self.db.tkn_from_address(tkn1_address).key
        return f"{tkn0_key}/{tkn1_key}"

    def _get_logs(self, exchange: str, contract: Contract) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        Parameters
        ----------
        exchange : str
            exchange name
        contract : Contract
            contract object

        Returns
        -------
        Optional[Any]
            The event logs
        """

        from_block = self.db.get_latest_block_for_exchange(exchange)

        c.logger.debug(f"Starting from block {from_block} on {exchange}")
        if exchange == c.BANCOR_V2_NAME:
            return contract.events.TokenRateUpdate.get_logs(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == c.BANCOR_V3_NAME:
            return contract.events.TradingLiquidityUpdated.get_logs(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange in c.UNIV2_FORKS:
            return contract.events.Sync.get_logs(fromBlock=from_block, toBlock="latest")
        elif exchange == c.UNISWAP_V3_NAME:
            return contract.events.Swap.get_logs(fromBlock=from_block, toBlock="latest")
        elif c.CARBON_V1_NAME in exchange:
            return [
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.PairCreated.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyCreated.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyDeleted.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyUpdated.get_logs(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
            ]

    def _get_event_filter(self, exchange: str, contract: Contract) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        Parameters
        ----------
        exchange : str
            exchange name
        contract : Contract
            contract object

        Returns
        -------
        Optional[Any]
            The event filter

        """
        pair_name = self.get_pair_name_from_contract(exchange, contract)
        from_block = self.db.get_latest_block_for_pair(pair_name, exchange)
        c.logger.info(f"Starting from block {from_block} for {pair_name} on {exchange}")
        if exchange == c.BANCOR_V2_NAME:
            return contract.events.TokenRateUpdate.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == c.BANCOR_V3_NAME:
            return contract.events.TradingLiquidityUpdated.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange in c.UNIV2_FORKS:
            return contract.events.Sync.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == c.UNISWAP_V3_NAME:
            return contract.events.Swap.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif c.CARBON_V1_NAME in exchange:
            return [
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.PoolCreated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyCreated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyDeleted.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "_filter": contract.events.StrategyUpdated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
                {
                    "exchange": "Carbon",
                    "filter": contract.events.TokensTraded.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                },
            ]

    def _log_loop_noasync(self, exchange: str, _filter: LogFilter):
        """
        Polls for new events and processes them

        Parameters
        ----------
        exchange : str
            exchange name
        _filter : LogFilter
            event filter

        """
        for event in _filter.get_new_entries():
            try:
                self._handle_pool_update_from_event(exchange=exchange, event_log=event)
            except Exception as e:
                c.logger.error(
                    f"_log_loop: {exchange}, {_filter}, Failed to handle event: {e}"
                )

    async def _update_current_block(self):
        while True:
            self.current_block = c.w3.eth.blockNumber
            await asyncio.sleep(self.poll_interval)

    async def _process_events(self, events: List[Dict], event_type: str, _exchange: str):
        """
        Processes a list of events

        Parameters
        ----------
        events : List[Dict]
            List of events
        event_type : str
            Type of event
        _exchange : str
            exchange name
        """
        for event in events:
            if event is None or len(event) == 0:
                continue
            if event_type == "delete":
                self._handle_pool_update_from_event(exchange=_exchange, event_log=event, event_type="delete")
            else:
                self._handle_pool_update_from_event(exchange=_exchange, event_log=event, event_type="update")

    async def _get_log_loop_tasks(self, _exchange: str) -> List[asyncio.Task]:
        """
        Polls for new events and processes them

        Parameters
        ----------
        _exchange : str
            exchange name

        Returns
        -------
        List[asyncio.Task]
            List of tasks to be run in the event loop
        """
        contract = self._get_contract_for_exchange(exchange=_exchange)

        while True:
            from_block = self.db.get_latest_block_for_exchange(_exchange)
            if from_block == self.current_block:
                await asyncio.sleep(self.poll_interval)
                continue

            events, delete_events = [], []
            if _exchange == c.BANCOR_V3_NAME:
                events = contract.events.TradingLiquidityUpdated.getLogs(fromBlock=from_block, toBlock="latest")
            elif c.CARBON_V1_NAME in _exchange:
                events += contract.events.StrategyCreated.getLogs(fromBlock=from_block, toBlock="latest")
                delete_events += contract.events.StrategyDeleted.getLogs(fromBlock=from_block, toBlock="latest")
                events += contract.events.StrategyUpdated.getLogs(fromBlock=from_block, toBlock="latest")

            await self._process_events(events=events, _exchange=_exchange, event_type="update")
            await self._process_events(events=delete_events, _exchange=_exchange, event_type="delete")

            await asyncio.sleep(self.poll_interval)


    async def _log_loop(self, exchange: str, _filter: LogFilter):
        """
        Polls for new events and processes them
        :param exchange: exchange name
        :param _filter: filter for the relevant event
        """
        while True:
            for event in _filter.get_new_entries():
                try:
                    self._handle_pool_update_from_event(exchange=exchange, event_log=event)
                except Exception as e:
                    c.logger.error(
                        f"_log_loop: {exchange}, {_filter}, Failed to handle event: {e}"
                    )
            await asyncio.sleep(1)

    def stop(self):
        """
        Stops the event updater
        """
        c.w3.provider.disconnect()
        self.db.session.close()

    def __repr__(self):
        return f"EventUpdater({self.filters})"
