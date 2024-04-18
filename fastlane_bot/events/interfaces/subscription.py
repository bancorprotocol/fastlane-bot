from typing import Optional

from web3 import AsyncWeb3, Web3
from web3.contract.contract import ContractEvent

from ..utils import complex_handler
from .event import Event


def _get_event_topic(event):
    abi = event().abi
    topic = Web3.keccak(text=f'{abi["name"]}({",".join([arg["type"] for arg in abi["inputs"]])})')
    return topic.hex()


class Subscription:
    def __init__(self, event: ContractEvent, topic: Optional[str] = None):
        self._event = event
        self._topic = _get_event_topic(event) if topic is None else topic
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

    def _parse_log(self, log) -> Event:
        try:
            event_data = complex_handler(self._event().process_log(log))
        except:
            print(log)
            raise
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
