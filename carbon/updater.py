"""
Database event updater.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio

from web3._utils.filters import LogFilter
from web3.datastructures import AttributeDict

from carbon.manager import *


@dataclass
class EventUpdater:
    """
    Processes events from the Ethereum network and updates the database accordingly
    """

    db: DatabaseManager
    poll_interval: int = 1
    test_sample_size: int = None

    _bancor_v2_contract: Optional[Contract] = None
    _bancor_v3_contract: Optional[Contract] = None
    _uniswap_v2_contract: Optional[Contract] = None
    _uniswap_v3_contract: Optional[Contract] = None
    _sushiswap_contract: Optional[Contract] = None
    _carbon_v1_contract: Optional[Contract] = None

    def __post_init__(self):
        self.pool_list = [
            (
                pool.exchange_name,
                self.db.contract_from_address(pool.exchange_name, pool.address),
                pool.address,
            )
            for pool in session.query(Pool).all()
        ]
        if self.test_sample_size:
            self.pool_list = self.pool_list[: self.test_sample_size]
        self.filters = [
            {
                "exchange": exchange_name,
                "_filter": self._get_event_filter(exchange_name, contract),
            }
            for exchange_name, contract, pool_address in self.pool_list
        ]

    def _handle_event(self, exchange: str, event_log: Any):
        """
        Handles an event log from the Ethereum network
        :param exchange: exchange name
        :param event_log: event log from web3 Contract.events
        """

        processed_event = self.build_processed_event(event_log, exchange)
        pool = self.db.get_or_create_pool(exchange, event_log["address"])
        current_block = event_log["blockNumber"]
        pool.last_updated_block = current_block

        if pool.exchange == BANCOR_V3_NAME:
            if processed_event["token"] == BNT_ADDRESS:
                pool.tkn0_balance = processed_event["newLiquidity"]
            else:
                pool.tkn1_balance = processed_event["newLiquidity"]

        elif pool.exchange == UNISWAP_V3_NAME:
            pool.sqrt_price_q96 = processed_event["price"]
            pool.liquidity = processed_event["liquidity"]
            pool.tick = processed_event["tick"]

        elif pool.exchange in UNIV2_FORKS + [BANCOR_V2_NAME]:
            pool.tkn0_balance = processed_event["tkn0_balance"]
            pool.tkn1_balance = processed_event["tkn1_balance"]

        session.commit()
        print(
            f"Processed event for {exchange} {pool.pair_name} {pool.fee} at block {current_block}..."
        )
        # return exchange, pool.pair_name, pool.fee, current_block

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
        processed_event = {"block_number": event_log["blockNumber"]}
        if exchange == BANCOR_V3_NAME:
            processed_event["pool"] = event_log["args"].get("pool")
            processed_event["token"] = event_log["args"].get("token")
            processed_event["newLiquidity"] = event_log["args"].get("newLiquidity")
        elif exchange in UNIV2_FORKS + [BANCOR_V2_NAME]:
            processed_event["tkn0_balance"] = event_log["args"].get("reserve0")
            processed_event["tkn1_balance"] = event_log["args"].get("reserve1")
        elif exchange == UNISWAP_V3_NAME:
            processed_event["price"] = event_log["args"].get("sqrtPriceX96")
            processed_event["liquidity"] = event_log["args"].get("liquidity")
            processed_event["tick"] = event_log["args"].get("tick")
            processed_event["tick_spacing"] = event_log["args"].get("tickSpacing")

        return processed_event

    def _get_contract_for_exchange(
        self, exchange: str = None, pool_address: str = None
    ) -> Contract:
        """
        Get the relevant ABI for the exchange
        """
        if exchange == BANCOR_V2_NAME:
            return w3.eth.contract(abi=BANCOR_V2_CONVERTER_ABI, address=pool_address)

        elif exchange == BANCOR_V3_NAME:
            return bancor_network_info

        elif exchange in UNIV2_FORKS:
            return w3.eth.contract(abi=UNISWAP_V2_POOL_ABI, address=pool_address)

        elif exchange == UNISWAP_V3_NAME:
            return w3.eth.contract(abi=UNISWAP_V3_POOL_ABI, address=pool_address)

        elif exchange == CARBON_V1_NAME:
            if self._carbon_v1_contract is None:
                self._carbon_v1_contract = w3.eth.contract(CARBON_CONTROLLER_ABI)
            return self._carbon_v1_contract

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

    def _get_event_filter(self, exchange: str, contract: Contract) -> Optional[Any]:
        """
        Creates a _filter for the relevant event for a given exchange

        :param exchange_name: exchange name
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
        elif exchange == CARBON_V1_NAME:
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

    async def _log_loop(self, exchange: str, _filter: LogFilter):
        """
        Polls for new events and processes them
        :param exchange: exchange name
        :param _filter: filter for the relevant event
        """
        while True:
            for event in _filter.get_new_entries():
                self._handle_event(exchange=exchange, event_log=event)
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
