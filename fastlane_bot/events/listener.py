
from typing import List
from web3 import AsyncWeb3

from .utils import complex_handler
from .managers.base import BaseManager


class EventListener:
    """
    The EventListener is the entry point to create & manage websocket event subscriptions.
    """

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

        for exchange_name, exchange in self._manager.exchanges.items():
            if exchange_name in base_exchanges:
                self._subscriptions += exchange.get_subscriptions(self._manager.event_contracts[exchange_name])

    async def get_latest_events(self):
        """ Collects latest events from Websocket.

        Returns:
            List: A stream of processed events retrieved from the Websocket.
        """
        subscription_by_id = {}
        for subscription in self._subscriptions:
            await subscription.subscribe(self._w3)
            subscription_by_id[subscription.subscription_id] = subscription

        async for response in self._w3.ws.process_subscriptions():
            subscription_id = response["subscription"]
            log = response["result"]
            event = subscription_by_id[subscription_id].process_log(log)
            if event is not None:
                yield complex_handler(event)
