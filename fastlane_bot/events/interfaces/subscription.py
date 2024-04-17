from dataclasses import dataclass
from typing import Any, Dict, Optional

from web3 import AsyncWeb3
from web3.contract.contract import ContractEvent

from ..utils import complex_handler


@dataclass
class Event:
    args: Dict[str, Any]
    event: str
    log_index: int
    transaction_index: int
    transaction_hash: str
    address: str
    block_hash: str
    block_number: int


class Subscription:
    def __init__(self, event: ContractEvent, topic: str):
        self._event = event
        self._topic = topic
        self._subscription_id = None
        self._latest_event_index = (-1, -1) # (block_number, block_index)

    async def subscribe(self, w3: AsyncWeb3):
        self._subscription_id = await w3.eth.subscribe("logs", {"topics": [self._topic]})

    @property
    def subscription_id(self):
        return self._subscription_id

    def process_log(self, log) -> Optional[Event]:
        if self._is_event_latest(log):
            self._latest_event_index = (log["blockNumber"], log["transactionIndex"])
            return self._parse_log(log)
        else:
            return None

    def _parse_log(self, event) -> Event:
        event_data = complex_handler(self._event().process_log(event))
        return Event(
            args=event_data["args"],
            event=event_data["event"],
            log_index=event_data["logIndex"],
            transaction_index=event_data["transactionIndex"],
            transaction_hash=event_data["transactionHash"],
            address=event_data["address"],
            block_hash=event_data["blockHash"],
            block_number=event_data["blockNumber"],
        )

    def _is_event_latest(self, event) -> bool:
        return (event["blockNumber"], event["transactionIndex"]) > self._latest_event_index
