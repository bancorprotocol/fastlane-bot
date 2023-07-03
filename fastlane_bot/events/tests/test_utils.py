# Imports for test setup
from typing import List, Union, Any, Dict, Hashable
from web3.datastructures import AttributeDict
from web3.types import HexBytes
import pytest

from ..utils import filter_latest_events, complex_handler


def test_filter_latest_events(mocked_mgr, mock_events):
    result = filter_latest_events(mocked_mgr, mock_events)

    # Check that we only have one event per pool
    assert len(result) == len({event['address'] for event in result})

    # Select first pool's address
    pool_address = result[0]['address']

    # Get all events for this pool
    pool_events = [event for event in mock_events[0] if event['address'] == pool_address]

    # Check that the event is indeed the latest one for this pool
    assert result[0] == max(pool_events, key=lambda e: e['blockNumber'])


def test_complex_handler():
    # AttributeDict case
    attribute_dict = AttributeDict({'a': 1, 'b': 2})
    assert complex_handler(attribute_dict) == {'a': 1, 'b': 2}

    # HexBytes case
    hex_bytes = HexBytes(b'hello')
    assert complex_handler(hex_bytes) == '0x68656c6c6f'

    # dict case
    dictionary = {'a': 1, 'b': HexBytes(b'hello'), 'c': AttributeDict({'d': 4})}
    assert complex_handler(dictionary) == {'a': 1, 'b': '0x68656c6c6f', 'c': {'d': 4}}

    # list case
    list_ = [1, HexBytes(b'hello'), AttributeDict({'d': 4})]
    assert complex_handler(list_) == [1, '0x68656c6c6f', {'d': 4}]

    # set case
    set_ = {1, 2, 3}
    assert complex_handler(set_) == [1, 2, 3]

    # other case
    assert complex_handler(123) == 123
    assert complex_handler('abc') == 'abc'


# Mocks for filter_latest_events

@pytest.fixture
def mocked_mgr():
    class MockManager:
        def pool_type_from_exchange_name(self, exchange_name):
            class MockPoolType:
                def unique_key(self):
                    return 'address'

            return MockPoolType()

        def exchange_name_from_event(self, event):
            return 'uniswap_v2'

    return MockManager()

@pytest.fixture
def mock_events() -> List[List[AttributeDict]]:
    event1 = AttributeDict({
        'args': {'reserve0': 100, 'reserve1': 100},
        'event': 'Sync',
        'address': '0xabc',
        'blockNumber': 5,
        'transactionIndex': 0,
        'logIndex': 0
    })
    event2 = AttributeDict({
        'args': {'reserve0': 200, 'reserve1': 200},
        'event': 'Sync',
        'address': '0xabc',
        'blockNumber': 10,
        'transactionIndex': 1,
        'logIndex': 1
    })
    event3 = AttributeDict({
        'args': {'reserve0': 300, 'reserve1': 300},
        'event': 'Sync',
        'address': '0xdef',
        'blockNumber': 7,
        'transactionIndex': 1,
        'logIndex': 1
    })
    return [[event1, event2, event3]]
