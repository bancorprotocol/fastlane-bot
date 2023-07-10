# coding=utf-8
"""
This module contains the tests for the exchanges classes
"""

from fastlane_bot import Bot
from fastlane_bot.events.pools import (
    SushiswapV2Pool,
    UniswapV2Pool,
    UniswapV3Pool,
    BancorV3Pool,
    CarbonV1Pool,
)
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from typing import List
from web3.datastructures import AttributeDict
from web3.types import HexBytes
import pytest

from fastlane_bot.events.utils import filter_latest_events, complex_handler

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3Pool))
from fastlane_bot.testing import *

plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]
from fastlane_bot import __VERSION__

require("3.0", __VERSION__)


@pytest.fixture
def mocked_mgr():
    class MockManager:
        def pool_type_from_exchange_name(self, exchange_name):
            class MockPoolType:
                def unique_key(self):
                    return "address"

            return MockPoolType()

        def exchange_name_from_event(self, event):
            return "uniswap_v2"

    mocked_mgr = MockManager()
    return mocked_mgr


@pytest.fixture
def mock_events() -> List[List[AttributeDict]]:
    event1 = AttributeDict(
        {
            "args": {"reserve0": 100, "reserve1": 100},
            "event": "Sync",
            "address": "0xabc",
            "blockNumber": 5,
            "transactionIndex": 0,
            "logIndex": 0,
        }
    )
    event2 = AttributeDict(
        {
            "args": {"reserve0": 200, "reserve1": 200},
            "event": "Sync",
            "address": "0xabc",
            "blockNumber": 10,
            "transactionIndex": 1,
            "logIndex": 1,
        }
    )
    event3 = AttributeDict(
        {
            "args": {"reserve0": 300, "reserve1": 300},
            "event": "Sync",
            "address": "0xdef",
            "blockNumber": 7,
            "transactionIndex": 1,
            "logIndex": 1,
        }
    )
    mock_events = [[event1, event2, event3]]
    return mock_events


def test_filter_latest_events(mocked_mgr, mock_events):
    result = filter_latest_events(mocked_mgr, mock_events)

    # Check that we only have one event per pool
    assert len(result) == len({event["address"] for event in result})

    # Select first pool's address
    pool_address = result[0]["address"]

    # Get all events for this pool
    pool_events = [
        event for event in mock_events[0] if event["address"] == pool_address
    ]

    # Check that the event is indeed the latest one for this pool
    assert result[0] == max(pool_events, key=lambda e: e["blockNumber"])


def test_complex_handler():
    # AttributeDict case
    attribute_dict = AttributeDict({"a": 1, "b": 2})
    assert complex_handler(attribute_dict) == {"a": 1, "b": 2}

    # HexBytes case
    hex_bytes = HexBytes(b"hello")
    assert complex_handler(hex_bytes) == "0x68656c6c6f"

    # dict case
    dictionary = {"a": 1, "b": HexBytes(b"hello"), "c": AttributeDict({"d": 4})}
    assert complex_handler(dictionary) == {"a": 1, "b": "0x68656c6c6f", "c": {"d": 4}}

    # list case
    list_ = [1, HexBytes(b"hello"), AttributeDict({"d": 4})]
    assert complex_handler(list_) == [1, "0x68656c6c6f", {"d": 4}]

    # set case
    set_ = {1, 2, 3}
    assert complex_handler(set_) == [1, 2, 3]

    # other case
    assert complex_handler(123) == 123
    assert complex_handler("abc") == "abc"
