"""
Database updater object for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict

from brownie import Contract
from web3._utils.filters import LogFilter
from web3.datastructures import AttributeDict

from fastlane_bot.abi import BANCOR_V2_CONVERTER_ABI, BANCOR_V3_POOL_COLLECTION_ABI, UNISWAP_V2_POOL_ABI, \
    UNISWAP_V3_POOL_ABI
from fastlane_bot.db.manager import DatabaseManager


@dataclass
class EventUpdater:
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
    poll_interval: int = 12
    test_mode: bool = False

    _carbon_v1_contract: Optional[Contract] = None
    filters: List[Any] = field(default_factory=list)

    def __post_init__(self):
        self.exchange_list = [
            exchange.name for exchange in session.query(Exchange).all()
        ]

        self.exchange_list = [
            CARBON_V1_NAME,
            UNISWAP_V2_NAME,
            UNISWAP_V3_NAME,
            BANCOR_V3_NAME,
            BANCOR_V2_NAME
        ]

        logger.debug(f"post init on EventUpdater, exchanges = {self.exchange_list}")
        if (
            UNISWAP_V2_NAME in self.exchange_list
            and SUSHISWAP_V2_NAME in self.exchange_list
        ):
            self.exchange_list.remove(SUSHISWAP_V2_NAME)

        if self.test_mode:
            self.log_tasks = [
                {
                    "exchange": exchange_name,
                    "_filter": self._get_log_loop_tasks(exchange_name),
                }
                for exchange_name in self.exchange_list
            ]
        else:
            self._get_event_filters(self.exchange_list)
            logger.info(self.filters)

        logger.info(self.exchange_list)

    def _parse_processed_event(
            self, exchange_name: str, pool_identifier: str, processed_event: Dict[str, Any]
    ):
        block_number = processed_event["block_number"]
        if CARBON_V1_NAME in exchange_name:
            exchange_name = CARBON_V1_NAME
            pool_contract = carbon_controller
            tkn0_address, tkn1_address = (
                processed_event["token0"],
                processed_event["token1"],
            )
            pool_address = CARBON_CONTROLLER_ADDRESS
            cid = processed_event["id"]
        elif exchange_name == BANCOR_V3_NAME:
            pool_address = BANCOR_V3_NETWORK_INFO_ADDRESS
            pool_contract = bancor_network_info
            tkn0_address = BNT_ADDRESS
            tkn1_address = processed_event["pool"]
            cid = str(self.next_cid)
        else:
            pool_address = pool_identifier
            pool_contract = DatabaseManager.contract_from_address(
                exchange_name, pool_identifier
            )
            tkn0_address, tkn1_address = DatabaseManager.get_token_addresses_for_pool(
                exchange_name, pool_identifier, pool_contract
            )
            cid = str(self.next_cid)
        return (
            block_number,
            cid,
            pool_address,
            pool_contract,
            tkn0_address,
            tkn1_address,
            exchange_name,
        )

    @property
    def next_cid(self):
        """
        Returns the next cid
        """
        max_idxs = session.query(Pool).all()
        if not max_idxs:
            return 0
        max_idx = max(int(x.cid) for x in max_idxs)
        return max_idx + 1 if max_idx is not None else 0

    def _get_event_filters(self, exchanges: [str]) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        Parameters
        ----------
        exchanges: [str]
            The list of exchanges to get the filters for

        Returns
        -------
        None
        """

        if BANCOR_V2_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(BANCOR_V2_NAME)
            contract = self._get_contract_for_exchange(exchange=BANCOR_V2_NAME)
            self.filters.append(
                {
                    "exchange": BANCOR_V2_NAME,
                    "_filter": contract.events.TokenRateUpdate.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
        if BANCOR_V3_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(BANCOR_V3_NAME)
            contract = self._get_contract_for_exchange(exchange=BANCOR_V3_NAME)
            self.filters.append(
                {
                    "exchange": BANCOR_V3_NAME,
                    "_filter": contract.events.TradingLiquidityUpdated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
        if UNISWAP_V2_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(UNISWAP_V2_NAME)
            contract = self._get_contract_for_exchange(exchange=UNISWAP_V2_NAME)
            self.filters.append(
                {
                    "exchange": UNISWAP_V2_NAME,
                    "_filter": contract.events.Sync.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

        if UNISWAP_V3_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(UNISWAP_V3_NAME)
            contract = self._get_contract_for_exchange(exchange=UNISWAP_V3_NAME)
            self.filters.append(
                {
                    "exchange": UNISWAP_V3_NAME,
                    "_filter": contract.events.Swap.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

        if CARBON_V1_NAME in exchanges:
            from_block = self.db.get_latest_block_for_exchange(CARBON_V1_NAME)
            contract = self._get_contract_for_exchange(exchange=CARBON_V1_NAME)
            self.filters.append(
                {
                    "exchange": CARBON_STRATEGY_CREATED,
                    "_filter": contract.events.StrategyCreated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
            self.filters.append(
                {
                    "exchange": CARBON_STRATEGY_DELETED,
                    "_filter": contract.events.StrategyDeleted.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )
            self.filters.append(
                {
                    "exchange": CARBON_STRATEGY_UPDATED,
                    "_filter": contract.events.StrategyUpdated.createFilter(
                        fromBlock=from_block, toBlock="latest"
                    ),
                }
            )

    def _handle_event(self, exchange: str, event_log: Any, event_type: str = None):
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
        # try:
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

        logger.debug(
            f"Getting or creating pool for processed_event= {processed_event}, pool_identifier = {pool_identifier}"
        )
        pool = self.db.get_or_create_pool(
            exchange_name=exchange,
            pool_identifier=pool_identifier,
            processed_event=processed_event,
        )
        if pool:
            logger.debug(
                f"updating pool for exchange = {exchange}, event = {event_log}, event_type = {event_type}"
            )
            pool.last_updated_block = block_number

            if pool.exchange_name == BANCOR_V3_NAME:
                pool = self._update_bancor3_liquidity(pool, processed_event)

            elif pool.exchange_name == UNISWAP_V3_NAME:
                pool = self._update_uni3_liquidity(pool, processed_event)

            elif pool.exchange_name in UNIV2_FORKS + [BANCOR_V2_NAME]:
                pool = self._update_other_liquidity(pool, processed_event)

            elif CARBON_V1_NAME in pool.exchange_name:
                pool = self._update_carbon_liquidity(
                    cid, event_type, pool, processed_event
                )

            is_created = session.query(Pool).filter(Pool.cid == cid).first()
            if not is_created:
                session.add(pool)
            session.commit()
            logger.info(
                f"Successfully updated event for {exchange} {pool.pair_name} {pool.fee} at block {block_number}..."
            )

    def _update_carbon_liquidity(self, cid, event_type, pool, processed_event):
        if event_type == "delete":
            self.db.delete_carbon_strategy(cid)
        else:
            pool = self._handle_carbon_pool_update(cid, pool, processed_event)
        return pool

    def _update_other_liquidity(self, pool, processed_event) -> Pool:
        pool.tkn0_balance = processed_event["tkn0_balance"]
        pool.tkn1_balance = processed_event["tkn1_balance"]
        return pool

    def _update_uni3_liquidity(self, pool, processed_event) -> Pool:
        pool.sqrt_price_q96 = processed_event["sqrt_price_q96"]
        pool.liquidity = processed_event["liquidity"]
        pool.tick = processed_event["tick"]
        return pool

    def _update_bancor3_liquidity(self, pool, processed_event) -> Pool:
        if processed_event["token"] == BNT_ADDRESS:
            pool.tkn0_balance = processed_event["newLiquidity"]
        else:
            pool.tkn1_balance = processed_event["newLiquidity"]
        return pool

    def _get_pool_identifier(self, event_log, exchange):
        if CARBON_V1_NAME in exchange:
            pool_identifier = event_log["args"].get("id")

        elif exchange == BANCOR_V3_NAME:
            pool_identifier = event_log["args"].get("pool")
        else:
            pool_identifier = event_log["address"]
        return pool_identifier

    def _handle_carbon_pool_update(
        self, cid: int, pool: Pool, processed_event: Dict[str, Any]
    ) -> Pool:
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
    def build_processed_event(
        event_log: AttributeDict, exchange: str
    ) -> Dict[str, Any]:
        """
        Builds a processed event from the event log and exchange name
        :param event_log:  event log from web3 Contract.events
        :param exchange: exchange name
        :return: processed event
        """
        logger.debug(f"event_log = {event_log}")
        block_number = event_log["blockNumber"]
        logger.debug(f"exchange = {exchange}, blocknumber = {block_number}")
        processed_event = {"block_number": block_number}
        if exchange == BANCOR_V3_NAME:
            processed_event["pool"] = event_log["args"].get("pool")
            processed_event["token"] = event_log["args"].get("token")
            processed_event["newLiquidity"] = event_log["args"].get("newLiquidity")
        elif exchange in UNIV2_FORKS + [BANCOR_V2_NAME]:
            processed_event["tkn0_balance"] = event_log["args"].get("reserve0")
            processed_event["tkn1_balance"] = event_log["args"].get("reserve1")
        elif exchange == UNISWAP_V3_NAME:
            processed_event["sqrt_price_q96"] = event_log["args"].get("sqrtPriceX96")
            processed_event["liquidity"] = event_log["args"].get("liquidity")
            processed_event["tick"] = event_log["args"].get("tick")
            processed_event["tick_spacing"] = event_log["args"].get("tickSpacing")
        elif CARBON_V1_NAME in exchange:
            processed_event["token0"] = event_log["args"].get("token0")
            processed_event["token1"] = event_log["args"].get("token1")
            if event_log["args"].get("pairId"):
                return processed_event
            else:
                processed_event["id"] = event_log["args"].get("id")
                processed_event["order0"] = event_log["args"].get("order0")
                processed_event["order1"] = event_log["args"].get("order1")

        return processed_event

    def _get_contract_for_exchange(
        self, exchange: str = None, pool_address: str = None, init_contract=True
    ) -> Contract:
        """
        Get the relevant ABI for the exchange
        """
        if exchange == BANCOR_V2_NAME:
            return w3.eth.contract(abi=BANCOR_V2_CONVERTER_ABI, address=pool_address)

        elif exchange == BANCOR_V3_NAME:
            if init_contract:
                return w3.eth.contract(
                    abi=BANCOR_V3_POOL_COLLECTION_ABI,
                    address=w3.toChecksumAddress(BANCOR_V3_POOL_COLLECTOR_ADDRESS),
                )
            else:
                return bancor_network_info

        elif exchange in UNIV2_FORKS:
            return w3.eth.contract(abi=UNISWAP_V2_POOL_ABI, address=pool_address)

        elif exchange == UNISWAP_V3_NAME:
            return w3.eth.contract(abi=UNISWAP_V3_POOL_ABI, address=pool_address)

        elif CARBON_V1_NAME in exchange:
            return carbon_controller

    def get_pair_name_from_contract(self, exchange: str, contract: Contract) -> str:
        """
        Get the pair name from the contract

        :param exchange: exchange name
        :param contract: contract object

        :return: pair name in the format of tkn0_key/tkn1_key
        """
        tkn0_address = contract.caller.token0()
        tkn0_key = self.db.tkn_from_address(tkn0_address).key
        tkn1_address = contract.caller.token1()
        tkn1_key = self.db.tkn_from_address(tkn1_address).key
        return f"{tkn0_key}/{tkn1_key}"

    def _get_logs(self, exchange: str, contract: Contract) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        :param exchange: exchange name
        :param contract: contract object
        :return: filter for the relevant event
        """

        # pair_name = self.get_pair_name_from_contract(exchange, contract)
        # from_block = self.db.get_latest_block_for_pair(pair_name, exchange)
        from_block = self.db.get_latest_block_for_exchange(exchange)

        # logger.info(f"Starting from block {from_block} for {pair_name} on {exchange}")
        logger.info(f"Starting from block {from_block} on {exchange}")
        if exchange == BANCOR_V2_NAME:
            return contract.events.TokenRateUpdate.get_logs(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == BANCOR_V3_NAME:
            return contract.events.TradingLiquidityUpdated.get_logs(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange in UNIV2_FORKS:
            return contract.events.Sync.get_logs(fromBlock=from_block, toBlock="latest")
        elif exchange == UNISWAP_V3_NAME:
            return contract.events.Swap.get_logs(fromBlock=from_block, toBlock="latest")
        elif CARBON_V1_NAME in exchange:
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

        :param exchange: exchange name
        :param contract: contract object
        :return: filter for the relevant event
        """
        pair_name = self.get_pair_name_from_contract(exchange, contract)
        from_block = self.db.get_latest_block_for_pair(pair_name, exchange)
        logger.info(f"Starting from block {from_block} for {pair_name} on {exchange}")
        if exchange == BANCOR_V2_NAME:
            return contract.events.TokenRateUpdate.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == BANCOR_V3_NAME:
            return contract.events.TradingLiquidityUpdated.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange in UNIV2_FORKS:
            return contract.events.Sync.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif exchange == UNISWAP_V3_NAME:
            return contract.events.Swap.createFilter(
                fromBlock=from_block, toBlock="latest"
            )
        elif CARBON_V1_NAME in exchange:
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
        :param exchange: exchange name
        :param _filter: filter for the relevant event
        """
        # while True:
        for event in _filter.get_new_entries():
            try:
                self._handle_event(exchange=exchange, event_log=event)
            except Exception as e:
                logger.warning(
                    f"_log_loop: {exchange}, {_filter}, Failed to handle event: {e}"
                )

    async def _update_current_block(self):
        while True:
            self.current_block = w3.eth.blockNumber
            await asyncio.sleep(self.poll_interval)

    async def _get_log_loop_tasks(self, _exchange):
        """
        Polls for new events and processes them
        :param _exchange: exchange name
        """
        logger.debug(f"log loop tasks, exchange = {_exchange}")
        contract = self._get_contract_for_exchange(exchange=_exchange)
        while True:
            from_block = self.db.get_latest_block_for_exchange(_exchange)
            if from_block == self.current_block:
                await asyncio.sleep(self.poll_interval)
                continue
            logger.info(f"Starting from block {from_block} on {_exchange}")

            event_type = "None"
            events = []
            delete_events = []
            if _exchange == BANCOR_V3_NAME:
                events = contract.events.TradingLiquidityUpdated.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )

            elif CARBON_V1_NAME in _exchange:

                events += contract.events.StrategyCreated.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )
                delete_events += contract.events.StrategyDeleted.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )
                events += contract.events.StrategyUpdated.getLogs(
                    fromBlock=from_block, toBlock="latest"
                )
                for event in delete_events:
                    logger.debug(
                        f"event = {event}, type = {event_type}, exchange = {_exchange}, from_block = {from_block}"
                    )
                    self._handle_event(
                        exchange=_exchange, event_log=event, event_type="delete"
                    )

            for event in events:
                logger.debug(
                    f"event = {event}, type = {event_type}, exchange = {_exchange}, from_block = {from_block}"
                )
                if event is None or len(event) == 0:
                    continue
                self._handle_event(exchange=_exchange, event_log=event)

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
                    self._handle_event(exchange=exchange, event_log=event)
                except Exception as e:
                    logger.warning(
                        f"_log_loop: {exchange}, {_filter}, Failed to handle event: {e}"
                    )
            await asyncio.sleep(1)

    @staticmethod
    def stop():
        """
        Stops the event updater
        """
        w3.provider.disconnect()
        session.close()

    def __repr__(self):
        return f"EventUpdater({self.filters})"
