import time

import os

import aiohttp
import asyncio
from eth_typing import HexStr
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes
from typing import Optional, Dict, Any, Union, cast, List, Type, Set
from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3._utils.abi import get_abi_input_types, map_abi_data
from web3._utils.normalizers import BASE_RETURN_NORMALIZERS
from web3.datastructures import AttributeDict
from web3.utils import get_abi_input_names

from fastlane_bot.data.abi import UNISWAP_V3_POOL_ABI, UNISWAP_V2_POOL_ABI, BANCOR_V3_POOL_COLLECTION_ABI, BANCOR_V2_CONVERTER_ABI, PANCAKESWAP_V3_POOL_ABI, CARBON_CONTROLLER_ABI, SOLIDLY_V2_POOL_ABI
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
        return dict(obj)
    elif isinstance(obj, HexBytes):
        return obj.hex()
    elif isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k: complex_handler(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [complex_handler(i) for i in obj]
    elif isinstance(obj, set):
        return list(obj)
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
        data = [t[2:] for t in result['topics']]
        data += [result['data'][2:]]
        data = "0x" + "".join(data)
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


class Subscription:
    """Manages a subscription to blockchain events via a WebSocket connection."""

    def __init__(self):
        """Initializes the Subscription with no active connection."""
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.client.ClientWebSocketResponse] = None

    async def start(self, url, params):
        """Starts a WebSocket subscription.

        Args:
            url (str): The WebSocket URL to connect to.
            params (List[Any]): Parameters for the subscription.
        """
        assert not self._ws
        self._session = aiohttp.ClientSession()
        self._ws = await self._session._ws_connect(url)

        await self._ws.send_json({
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'eth_subscribe',
            'params': params
        })
        self._subscription = (await self._ws.receive_json()).get('result')
        assert self._subscription is not None

    async def get_event(self):
        """Retrieves an event from the subscription.

                Returns:
                    Dict[str, Any]: The received event data.
                """
        assert self._ws is not None
        return await self._ws.receive_json()

    async def unsubscribe(self):
        """Ends the subscription and closes the WebSocket connection."""
        assert self._ws is not None and self._session is not None
        await self._ws.send_json(
            {'jsonrpc': '2.0', 'id': 0, 'method': 'eth_unsubscribe', 'params': [self._subscription]})
        await self._ws.close()
        self._ws = None
        await self._session.close()
        self._session = None


def get_event_name(event):
    for topic in event["topics"]:
        try:
            return TOPIC_TO_EVENT_NAME[topic]
        except KeyError:
            continue


class EventHandler:
    """Handles event retrieval and processing for blockchain data using WebSockets."""

    def __init__(self,
                 w3: AsyncWeb3,
                 topic_or_address: str,
                 is_topic: bool,
                 contract: Type[AsyncContract],
                 websocket_url: str,
                 timeout_seconds: float = 0.005,
                 ):
        """Initializes the EventHandler.

        Args:
            w3 (AsyncWeb3): An instance of AsyncWeb3.
            topic_or_address (str): The topic or address to filter the events.
            is_topic (bool): Flag indicating if the filter is by topic.
            contract (AsyncContract): The contract associated with the events.
            websocket_url (str): The RPC URL for the WebSocket connection.
        """
        self.subscription = Subscription()
        self.w3 = w3
        self.topic_or_address = topic_or_address
        self.is_topic = is_topic
        self.contract = contract
        self.websocket_url = websocket_url
        self.decoder = EventLogDecoder(self.contract)
        self.timeout_seconds = timeout_seconds

    async def connect_websocket(self):
        """Establishes a WebSocket connection to start listening for events."""
        if self.is_topic:
            await self.subscription.start(f'{self.websocket_url}', ['logs', {"topics": [self.topic_or_address]}])
        else:
            await self.subscription.start(f'{self.websocket_url}', ['logs', {"address": self.topic_or_address}])

    async def disconnect_websocket(self):
        """Closes the WebSocket connection."""
        await self.subscription.unsubscribe()

    async def get_newest_events(self):
        """Retrieves the newest events from the WebSocket.

        Continuously fetches events from the WebSocket connection until no more new data is ready.
        It then filters and decodes the events based on the contract's ABI.

        Returns:
            List[Dict]: A list of the newest decoded events.
        """
        events = []
        while True:
            try:
                # Wait for an event with a timeout
                event = await asyncio.wait_for(self.subscription.get_event(), self.timeout_seconds)
                #print(event)
                # print(event['params']['result'])
            except asyncio.TimeoutError:
                # Break the loop if a timeout occurs
                # print("Timeout: No new events within the specified time.")
                break

            events.append(event['params']['result'])
        if not events:
            return []
        filtered_events = self.newest_event_filter(events)

        for event in filtered_events:
            event["args"] = self.decoder.decode_log(event)
            event["event"] = get_event_name(event)

        # decoded_events = [event["args"] =  for event in filtered_events]
        #print(f"*******************decoded_events******************** {filtered_events}")
        return filtered_events

    @staticmethod
    def newest_event_filter(events: List[Dict]) -> List:
        """
            Filters a list of event dictionaries, returning only the newest event for each unique address.

            This function iterates over a list of event dictionaries, each representing an event with various attributes,
            including a unique address, block number, and block index. It identifies and retains only the newest event
            for each unique address based on the block number and, if necessary, the block index. The comparison assumes
            that both the block number and the block index are provided in hexadecimal format.

            Args:
                events (List[Dict]): A list of dictionaries, where each dictionary represents an event with at least
                                     the following keys: 'address', 'blockNumber', and 'transactionIndex'. 'blockNumber' and
                                     'transactionIndex' should be strings representing hexadecimal numbers.

            Returns:
                List[Dict]: A list of dictionaries, where each dictionary is the newest event for a unique address
                            from the input list. The events in the output list are in no specific order relative to
                            each other.

            Raises:
                ValueError: If any event dictionary in the input list does not have the required keys ('address',
                            'blockNumber', 'transactionIndex') or if these keys are not in the expected format.

        event_example = {'address': '0x1529b3ba7462dc38f560a4e38e6a97c07d3293b6',
                         'topics': ['0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67',
                                    '0x0000000000000000000000003328f7f4a1d1c57c35df56bbf0c9dcafca309c49',
                                    '0x0000000000000000000000003328f7f4a1d1c57c35df56bbf0c9dcafca309c49'],
                         'data': '0x000000000000000000000000000000000000000015526dd54c78ba2370697216ffffffffffffffffffffffffffffffffffffffffffffffffffa6e04cb6a0ff6000000000000000000000000000000000000000000000206d0933f6d8db97168500000000000000000000000000000000000000000000623812b388d42d3d3aa4fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffbfc17',
                         'blockNumber': '0x129b1fb',
                         'transactionHash': '0x48a40f76ec729a92c3265a5a3843f43c57e4327a9823c2462347e073442a32a2',
                         'transactionIndex': '0x0',
                         'blockHash': '0x1df62332bedb161507e2e019441fe75282a61e699bbdcb0fd98cd47e8cc9f47e',
                         'logIndex': '0x2', 'removed': False}
        """
        event_dict = {}

        for event in events:
            # Converting block number and block index to integers once and storing them
            block_number = int(event["blockNumber"], 16)  # Assuming block numbers are in hex
            block_index = int(event["transactionIndex"], 16)  # Assuming block indexes are in hex

            # Checking if the event's address is already in the dictionary
            if event["address"] not in event_dict:
                # Add the event if it's not present
                event_dict[event["address"]] = event
                # Storing block number and index in the dictionary for future comparisons
                event_dict[event["address"]]["block_number"] = block_number
                event_dict[event["address"]]["block_index"] = block_index
            else:
                if block_number > event_dict[event["address"]]["block_number"] or (
                        block_number == event_dict[event["address"]]["block_number"] and block_index >
                        event_dict[event["address"]]["block_index"]):
                    event_dict[event["address"]] = event
                    event_dict[event["address"]]["block_number"] = block_number
                    event_dict[event["address"]]["block_index"] = block_index

        return list(event_dict.values())


def process_events(events):
    events = [
        complex_handler(event)
        for event in [
            complex_handler(event)
            for event in events
        ]
    ]
    return events


class EventManager:
    event_handlers: List[EventHandler]

    def __init__(self, base_exchanges: List[str], carbon_controller_addresses: List[str], async_web3: AsyncWeb3,
                 websocket_url: str):
        self.event_handlers = []  # Initialize the event handlers list
        self.async_web3 = async_web3

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
                self.event_handlers.append(EventHandler(
                    w3=self.async_web3,
                    topic_or_address=topic,
                    contract=self.async_web3.eth.contract(abi=abi),
                    is_topic=True,
                    websocket_url=websocket_url
                ))

        # Handle carbon controller addresses separately
        if carbon_controller_addresses:
            for address in carbon_controller_addresses:
                self.event_handlers.append(EventHandler(
                    w3=self.async_web3,
                    topic_or_address=address,
                    contract=self.async_web3.eth.contract(abi=CARBON_CONTROLLER_ABI),
                    is_topic=False,
                    websocket_url=websocket_url
                ))
        #self.connect_websockets()

    def connect_websockets(self):
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(*(handler.connect_websocket() for handler in self.event_handlers)))

    def disconnect_websockets(self):
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(*(handler.disconnect_websocket() for handler in self.event_handlers)))


    def get_latest_events(self):
        all_events = []

        all_events = asyncio.get_event_loop().run_until_complete(
            asyncio.gather(*(handler.get_newest_events() for handler in self.event_handlers)))
        #print(f"events = {all_events}")
        # for handler in self.event_handlers:
        #     events = await handler.get_newest_events()
        #     all_events.extend(events)
        all_events = [x for xs in all_events for x in xs]
        #print(f"events = {all_events}")
        return process_events(all_events)


def main():
    """
    This can be used to troubleshoot the event handler.
    """
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
        f"https://eth-mainnet.g.alchemy.com/v2/{os.environ.get('WEB3_ALCHEMY_PROJECT_ID')}"))

    URL = f"wss://eth-mainnet.g.alchemy.com/v2/{os.environ.get('WEB3_ALCHEMY_PROJECT_ID')}"
    base_exchanges = ["uniswap_v2", "uniswap_v3", "pancakeswap_v3", "bancor_v2", "bancor_v3"]
    carbon_controller_addresses = ["0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"]
    event_manager = EventManager(base_exchanges=base_exchanges, carbon_controller_addresses=carbon_controller_addresses,
                                 async_web3=w3, websocket_url=URL)

    event_manager.connect_websockets()

    # for handler in event_manager.event_handlers:
    #     await handler.connect_websocket()

    for i in range(30):
        _start = time.time()
        events = event_manager.get_latest_events()
        if events:
            print(f"***LOOPING **** took {time.time() - _start} seconds. Found {len(events)} events.")
        time.sleep(2)
        #await asyncio.sleep(2)
    print(f"\n\n***MAIN LOOP RETURNED****")

    event_manager.disconnect_websockets()

    # for handler in event_manager.event_handlers:
    #     await handler.disconnect_websocket()


#main()

#asyncio.run(main())
