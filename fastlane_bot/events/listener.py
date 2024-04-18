import asyncio
import time
from typing import AsyncGenerator, List

from web3 import AsyncWeb3

from .utils import complex_handler
from .managers.base import BaseManager
from .interfaces.event import Event


class EventListener:
    """
    The EventListener is the entry point to create & manage websocket event subscriptions.
    """
    NEW_EVENT_TIMEOUT = 0.01

    def __init__(
        self,
        manager: BaseManager,
        base_exchanges: List[str],
        w3: AsyncWeb3,
    ):
        """ Initializes the EventManager.
        Args:
            base_exchanges: The list of base exchanges for which to gather events.
            carbon_controller_addresses: The list of Carbon Controller addresses for which to gather events.
            w3: The connected AsyncWeb3 object.
        """
        self._manager = manager
        self._w3 = w3
        self._subscriptions = []  # Initialize the subscription list
        self._subscription_by_id = {}
        self._event_buffer = []
        self._last_event_ts = 0

        for exchange_name, exchange in self._manager.exchanges.items():
            if exchange_name in base_exchanges:
                self._subscriptions += exchange.get_subscriptions(self._manager.event_contracts[exchange_name])

    async def pull_block_events(self) -> AsyncGenerator[List[Event], None]:
        """ Collects latest events from Websocket.

        Returns:
            List: A stream of processed event batches retrieved from the Websocket.
        """
        for subscription in self._subscriptions:
            await subscription.subscribe(self._w3)
            self._subscription_by_id[subscription.subscription_id] = subscription

        asyncio.ensure_future(self._listen())
        async for batch in self._get_batched_events():
            yield batch

    async def _get_batched_events(self):
        while True:
            ts = time.time()
            if ts >= self._last_event_ts + self.NEW_EVENT_TIMEOUT:
                if self._event_buffer != []:
                    batch = self._event_buffer.copy()
                    self._event_buffer = []
                    yield batch
            await asyncio.sleep(min(0.01, self._last_event_ts + self.NEW_EVENT_TIMEOUT - ts))

    async def _listen(self):
        async for response in self._w3.ws.process_subscriptions():
            self._last_event_ts = time.time()
            subscription_id = response["subscription"]
            log = response["result"]
            event = self._subscription_by_id[subscription_id].process_log(log)
            if event is not None:
                self._event_buffer.append(complex_handler(event))
