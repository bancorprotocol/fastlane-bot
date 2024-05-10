from itertools import chain

import asyncio
import nest_asyncio

from web3 import AsyncWeb3
from web3.contract import Contract

from .interfaces.subscription import Subscription
from .exchanges.base import Exchange


nest_asyncio.apply()


class EventGatherer:
    """
    The EventGatherer manages event gathering using eth.get_logs.
    """

    def __init__(
        self,
        w3: AsyncWeb3,
        exchanges: dict[str, Exchange],
        event_contracts: dict[str, Contract],
    ):
        """ Initializes the EventManager.
        Args:
            manager: The Manager object
            w3: The connected AsyncWeb3 object.
        """
        self._w3 = w3
        self._subscriptions = []
        unique_topics = set()

        for exchange_name, exchange in exchanges.items():
            subscriptions = exchange.get_subscriptions(event_contracts[exchange_name])
            for sub in subscriptions:
                if sub.topic not in unique_topics:
                    unique_topics.add(sub.topic)
                    self._subscriptions.append(sub)

    def get_all_events(self, from_block: int, to_block: int):
        results = asyncio.get_event_loop().run_until_complete(asyncio.gather(*[self._get_events_for_topic(from_block, to_block, sub) for sub in self._subscriptions]))
        return list(chain.from_iterable(results))

    async def _get_events_for_topic(self, from_block: int, to_block: int, subscription: Subscription):
        events = await self._w3.eth.get_logs(filter_params={
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": [subscription.topic]
        })
        return [subscription.parse_log(event) for event in events]


