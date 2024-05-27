import asyncio
from itertools import chain
from typing import Dict, List
from traceback import format_exc

import nest_asyncio

from web3 import AsyncWeb3
from web3.contract import Contract

from fastlane_bot.config import Config
from fastlane_bot.config.constants import BLOCK_CHUNK_SIZE_MAP
from .interfaces.subscription import Subscription
from .exchanges.base import Exchange


nest_asyncio.apply()


class EventGatherer:
    """
    The EventGatherer manages event gathering using eth.get_logs.
    """

    def __init__(
        self,
        config: Config,
        w3: AsyncWeb3,
        exchanges: Dict[str, Exchange],
    ):
        """ Initializes the EventManager.
        Args:
            manager: The Manager object
            w3: The connected AsyncWeb3 object.
        """
        self._config = config
        self._w3 = w3
        self._subscriptions = []

        for exchange in exchanges.values():
            subscriptions = exchange.get_subscriptions(w3)
            for sub in subscriptions:
                if sub.topic not in [s.topic for s in self._subscriptions]:
                    self._subscriptions.append(sub)

    def get_all_events(self, from_block: int, to_block: int):
        coroutines = []
        for sub in self._subscriptions:
            if sub.collect_all:
                from_block_ = 0
            else:
                from_block_ = from_block
            coroutines.append(self._get_events_for_subscription(from_block_, to_block, sub))
        results = asyncio.get_event_loop().run_until_complete(asyncio.gather(*coroutines))
        return list(chain.from_iterable(results))

    async def _get_events_for_subscription(self, from_block: int, to_block: int, subscription: Subscription):
        return [subscription.parse_log(log) for log in await self._get_logs_for_topics(from_block, to_block, [subscription.topic])]

    async def _get_logs_for_topics(self, from_block: int, to_block: int, topics: List[str]):
        chunk_size = BLOCK_CHUNK_SIZE_MAP[self._config.network.NETWORK]
        if chunk_size > 0:
            return await self._get_logs_iterative(from_block, to_block, topics, chunk_size)
        else:
            return await self._get_logs_recursive(from_block, to_block, topics)

    async def _get_logs_iterative(self, from_block: int, to_block: int, topics: List[str], chunk_size: int) -> list:
        block_numbers = list(range(from_block, to_block + 1, chunk_size)) + [to_block + 1]
        log_lists = await asyncio.gather(*[
            self._w3.eth.get_logs(filter_params={
                "fromBlock": r[0],
                "toBlock": r[1],
                "topics": topics
            })
            for r in zip(block_numbers, map(lambda n: n - 1, block_numbers[1:]))
        ])
        return [log for log_list in log_lists for log in log_list]

    async def _get_logs_recursive(self, from_block: int, to_block: int, topics: List[str]) -> list:
        if from_block <= to_block:
            try:
                return await self._w3.eth.get_logs(filter_params={
                    "fromBlock": from_block,
                    "toBlock": to_block,
                    "topics": topics
                })
            except Exception as e:
                if "eth_getLogs" not in str(e):
                    self._config.logger.error(f"Unexpected exception in EventGatherer: {format_exc()}")
                if from_block < to_block:
                    mid_block = (from_block + to_block) // 2
                    log_lists = await asyncio.gather(
                        self._get_logs_recursive(from_block, mid_block, topics),
                        self._get_logs_recursive(mid_block + 1, to_block, topics)
                    )
                    return [log for log_list in log_lists for log in log_list]
                else:
                    raise e
        raise Exception(f"Illegal log query range: {from_block} -> {to_block}")
