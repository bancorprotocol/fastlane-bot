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
    def __init__(self, event: ContractEvent, topic: Optional[str] = None, collect_all: bool = False):
        self._event = event
        self._topic = _get_event_topic(event) if topic is None else topic
        self._collect_all = collect_all
        self._subscription_id = None
        self._latest_event_index = (-1, -1) # (block_number, block_index)

    async def subscribe(self, w3: AsyncWeb3):
        self._subscription_id = await w3.eth.subscribe("logs", {"topics": [self._topic]})

    @property
    def subscription_id(self):
        return self._subscription_id

    @property
    def topic(self):
        return self._topic
    
    @property
    def collect_all(self):
        return self._collect_all

    def parse_log(self, log) -> Event:
        try:
            event_data = complex_handler(self._event().process_log(log))
        except:
            print(log)
            raise
        return Event.from_dict(event_data)
