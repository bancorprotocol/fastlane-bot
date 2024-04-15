import os

import asyncio
from eth_typing import HexStr
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes
from typing import Optional, Dict, Any, Union, cast, List, Type, Set
from web3 import AsyncWeb3
from web3.providers import WebsocketProviderV2
from web3.contract import AsyncContract
from web3._utils.abi import get_abi_input_types, map_abi_data
from web3._utils.normalizers import BASE_RETURN_NORMALIZERS
from web3.datastructures import AttributeDict
from web3.utils import get_abi_input_names

from fastlane_bot.data.abi import (
    UNISWAP_V3_POOL_ABI,
    UNISWAP_V2_POOL_ABI,
    BANCOR_V3_POOL_COLLECTION_ABI,
    BANCOR_V2_CONVERTER_ABI,
    PANCAKESWAP_V3_POOL_ABI,
    CARBON_CONTROLLER_ABI,
    SOLIDLY_V2_POOL_ABI
)
from dotenv import load_dotenv

load_dotenv()

BANCOR_V2_TOPIC = "0x77f29993cf2c084e726f7e802da0719d6a0ade3e204badc7a3ffd57ecb768c24"
BANCOR_V3_TOPIC = "0x5c02c2bb2d1d082317eb23916ca27b3e7c294398b60061a2ad54f1c3c018c318"
UNI_V2_TOPIC = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
UNI_V3_TOPIC = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
PANCAKE_V3_TOPIC = "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
SOLIDLY_V2_TOPIC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
CARBON_V1_STRATEGY_UPDATED = "0x720da23a5c920b1d8827ec83c4d3c4d90d9419eadb0036b88cb4c2ffa91aef7d"
CARBON_V1_SET_FEE = "0x831434d05f3ad5f63be733ea463b2933c70d2162697fd200a22b5d56f5c454b6"
CARBON_V1_STRATEGY_DELETED = "0x4d5b6e0627ea711d8e9312b6ba56f50e0b51d41816fd6fd38643495ac81d38b6"
CARBON_V1_STRATEGY_CREATED = "0xff24554f8ccfe540435cfc8854831f8dcf1cf2068708cfaf46e8b52a4ccc4c8d"
CARBON_V1_PAIR_CREATED = "0x6365c594f5448f79c1cc1e6f661bdbf1d16f2e8f85747e13f8e80f1fd168b7c3"
BANCOR_POL_TOKEN_TRADED = "0x16ddee9b3f1b2e6f797172fe2cd10a214e749294074e075e451f95aecd0b958c"

# "TradingFeePPMUpdated", "PairTradingFeePPMUpdated"

# AERODROME_V2_TOPIC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"
# SCALE_V2_TOPIC = "0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a"

TOPIC_TO_EVENT_NAME = {
    BANCOR_V2_TOPIC: "TokenRateUpdate",
    BANCOR_V3_TOPIC: "TradingLiquidityUpdated",
    UNI_V2_TOPIC: "Sync",
    UNI_V3_TOPIC: "Swap",
    SOLIDLY_V2_TOPIC: "Sync",
    PANCAKE_V3_TOPIC: "Swap",
    CARBON_V1_STRATEGY_UPDATED: "StrategyUpdated",
    CARBON_V1_STRATEGY_DELETED: "StrategyDeleted",
    CARBON_V1_STRATEGY_CREATED : "StrategyCreated",
    CARBON_V1_PAIR_CREATED: "PairCreated",
    CARBON_V1_SET_FEE: "PairTradingFeePPMUpdated",
}

CARBON_CONTROLLER_ADDRESSES = ["0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"]

UNI_V3_TOPIC_ONLY = [UNI_V3_TOPIC]
TOPICS = [BANCOR_V2_TOPIC, BANCOR_V3_TOPIC]
TOPICS2 = [UNI_V3_TOPIC]

PANCAKESWAP_V3_NAME = "pancakeswap_v3"
CARBON_V1_NAME = "carbon_v1"
SOLIDLY_V2_NAME = "solidly_v2"
BANCOR_V2_NAME = "bancor_v2"
BANCOR_V3_NAME = "bancor_v3"
UNISWAP_V2_NAME = "uniswap_v2"
UNISWAP_V3_NAME = "uniswap_v3"

def complex_handler(obj: Any) -> Union[Dict, str, List, Set, Any]:
    """
    This function aims to handle complex data types, such as web3.py's AttributeDict, HexBytes, and native Python collections
    like dict, list, tuple, and set. It recursively traverses these collections and converts their elements into more "primitive"
    types, making it easier to work with these elements or serialize the data into JSON.

    Args:
        obj (Any): The object to be processed. This can be of any data type, but the function specifically handles AttributeDict,
        HexBytes, dict, list, tuple, and set.

    Returns:
        Union[Dict, str, List, Set, Any]: Returns a "simplified" version of the input object, where AttributeDict is converted
        into dict, HexBytes into str, and set into list. For dict, list, and tuple, it recursively processes their elements.
        If the input object does not match any of the specified types, it is returned as is.
    """
    if isinstance(obj, AttributeDict):
        return complex_handler(dict(obj))
    elif isinstance(obj, HexBytes):
        return obj.hex()
    elif isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k: complex_handler(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [complex_handler(i) for i in obj]
    elif isinstance(obj, set):
        return complex_handler(list(obj))
    else:
        return obj


class EventLogDecoder:
    """Decodes log data using the ABI of a smart contract.

    This class provides methods to decode log data from blockchain events
    using the ABI (Application Binary Interface) provided by a smart contract.

    Attributes:
        contract (AsyncContract): An asynchronous smart contract instance containing the ABI.
        event_abis (List[Dict]): Extracted event ABIs from the contract's ABI.
        _sign_abis (Dict): A mapping from event signatures to their ABIs.
        _name_abis (Dict): A mapping from event names to their ABIs.
    """

    def __init__(self, contract: Type[AsyncContract]):
        """Initializes the EventLogDecoder with a smart contract.

        Args:
            contract (AsyncContract): An asynchronous smart contract instance.
        """
        self.contract = contract
        self.event_abis = [abi for abi in self.contract.abi if abi['type'] == 'event']
        self._sign_abis = {event_abi_to_log_topic(abi): abi for abi in self.event_abis}
        self._name_abis = {abi['name']: abi for abi in self.event_abis}

    def decode_log(self, result: Dict[str, Any]):
        """Decodes a log entry.

        Args:
            result (Dict[str, Any]): The log entry to decode.

        Returns:
            Dict[str, Any]: The decoded log data.
        """
        data = HexBytes("")
        for t in result['topics']:
            data += t
        data += result['data']
        return self.decode_event_input(data)

    def decode_event_input(self, data: Union[HexStr, str], name: str = None) -> Dict[str, Any]:
        """Decodes the data input of an event.

        Args:
            data (Union[HexStr, str]): The data to decode.
            name (str, optional): The name of the event to use for decoding. Defaults to None.

        Returns:
            Dict[str, Any]: The decoded event data.
        """
        # type ignored b/c expects data arg to be HexBytes
        data = HexBytes(data)  # type: ignore
        selector, params = data[:32], data[32:]

        if name:
            func_abi = self._get_event_abi_by_name(event_name=name)
        else:
            func_abi = self._get_event_abi_by_selector(selector)

        names = get_abi_input_names(func_abi)
        types = get_abi_input_types(func_abi)

        decoded = self.contract.w3.codec.decode(types, cast(HexBytes, params))
        normalized = map_abi_data(BASE_RETURN_NORMALIZERS, types, decoded)

        return dict(zip(names, normalized))

    def _get_event_abi_by_selector(self, selector: HexBytes) -> Dict[str, Any]:
        """Retrieves an event ABI by its selector.

        Args:
            selector (HexBytes): The selector of the event.

        Returns:
            Dict[str, Any]: The event's ABI.

        Raises:
            ValueError: If the selector does not match any event in the ABI.
        """
        try:
            return self._sign_abis[selector]
        except KeyError:
            raise ValueError("Event is not presented in contract ABI.")

    def _get_event_abi_by_name(self, event_name: str) -> Dict[str, Any]:
        """Retrieves an event ABI by its name.

        Args:
            event_name (str): The name of the event.

        Returns:
            Dict[str, Any]: The event's ABI.

        Raises:
            KeyError: If the event name is not found in the ABI.
        """
        try:
            return self._name_abis[event_name]
        except KeyError:
            raise KeyError(f"Event named '{event_name}' was not found in contract ABI.")


def get_event_name(event):
    for topic in event["topics"]:
        try:
            return TOPIC_TO_EVENT_NAME[topic.hex()]
        except KeyError:
            continue


class EventHandler:
    """Handles event retrieval and processing for blockchain data using WebSockets."""

    def __init__(self,
                 w3: AsyncWeb3,
                 topic_or_address: str,
                 is_topic: bool,
                 contract: Type[AsyncContract],
                 ):
        """Initializes the EventHandler.

        Args:
            w3 (AsyncWeb3): An instance of AsyncWeb3.
            topic_or_address (str): The topic or address to filter the events.
            is_topic (bool): Flag indicating if the filter is by topic.
            contract (AsyncContract): The contract associated with the events.
        """
        self._w3 = w3
        self._topic_or_address = topic_or_address
        self._is_topic = is_topic
        self._contract = contract
        self._decoder = EventLogDecoder(contract)
        self._latest_event_index = (-1, -1) # (block_number, block_index)

    async def subscribe(self):
        """Establishes a WebSocket connection to start listening for events."""
        if self._is_topic:
            return await self._w3.eth.subscribe("logs", {"topics": [self._topic_or_address]})
        else:
            return await self._w3.eth.subscribe("logs", {"address": self._topic_or_address})

    def process_new_event(self, event):
        block_number = event["blockNumber"]
        block_index = event["transactionIndex"]
        if (block_number, block_index) > self._latest_event_index:
            self._latest_event_index = (block_number, block_index)
            event = dict(event)
            event["args"] = self._decoder.decode_log(event)
            event["event"] = get_event_name(event)
            return event
        else:
            return None


def normalize_events(events):
    return [complex_handler(event) for event in events]


class EventManager:
    event_handlers: List[EventHandler]

    def __init__(
        self,
        base_exchanges: List[str],
        carbon_controller_addresses: List[str],
        w3: AsyncWeb3,
    ):
        self._w3 = w3
        self._event_handlers = []  # Initialize the event handlers list

        # Mapping of exchanges to their topics and ABIs
        exchange_mappings = {
            BANCOR_V2_NAME: (BANCOR_V2_TOPIC, BANCOR_V2_CONVERTER_ABI),
            BANCOR_V3_NAME: (BANCOR_V3_TOPIC, BANCOR_V3_POOL_COLLECTION_ABI),
            UNISWAP_V2_NAME: (UNI_V2_TOPIC, UNISWAP_V2_POOL_ABI),
            UNISWAP_V3_NAME: (UNI_V3_TOPIC, UNISWAP_V3_POOL_ABI),
            PANCAKESWAP_V3_NAME: (PANCAKE_V3_TOPIC, PANCAKESWAP_V3_POOL_ABI),
            SOLIDLY_V2_NAME: (SOLIDLY_V2_TOPIC, SOLIDLY_V2_POOL_ABI),
        }

        # Dynamically create EventHandler instances based on provided base exchanges
        for exchange in base_exchanges:
            if exchange in exchange_mappings:
                topic, abi = exchange_mappings[exchange]
                self._event_handlers.append(EventHandler(
                    w3=w3,
                    topic_or_address=topic,
                    contract=w3.eth.contract(abi=abi),
                    is_topic=True,
                ))

        # Handle carbon controller addresses separately
        if carbon_controller_addresses:
            for address in carbon_controller_addresses:
                self._event_handlers.append(EventHandler(
                    w3=w3,
                    topic_or_address=address,
                    contract=w3.eth.contract(abi=CARBON_CONTROLLER_ABI),
                    is_topic=False,
                ))


    async def get_latest_events(self):
        event_handlers_by_sid = {}
        for handler in self._event_handlers:
            subscription_id = await handler.subscribe()
            event_handlers_by_sid[subscription_id] = handler

        async for response in self._w3.ws.process_subscriptions():
            subscription_id = response["subscription"]
            event = response["result"]
            event = event_handlers_by_sid[subscription_id].process_new_event(event)
            if event is not None:
                yield normalize_events([event])


async def main():
    """
    This can be used to troubleshoot the event handler.
    """
    base_exchanges = ["uniswap_v2", "uniswap_v3", "pancakeswap_v3", "bancor_v2", "bancor_v3"]
    carbon_controller_addresses = ["0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"]
    async with AsyncWeb3.persistent_websocket(WebsocketProviderV2(
        f"wss://eth-mainnet.g.alchemy.com/v2/{os.environ.get('WEB3_ALCHEMY_PROJECT_ID')}"
    )) as w3:
        event_manager = EventManager(
            base_exchanges=base_exchanges,
            carbon_controller_addresses=carbon_controller_addresses,
            w3=w3
        )
        async for event in event_manager.get_latest_events():
            print(event)


if __name__ == "__main__":
    asyncio.run(main())
