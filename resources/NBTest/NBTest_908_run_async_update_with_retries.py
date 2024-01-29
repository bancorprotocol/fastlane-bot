import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from fastlane_bot.events.async_event_update_utils import (
    update_remaining_pools,
    run_async_update_with_retries,
)  # replace with your actual module name
from fastlane_bot.events.exceptions import AyncUpdateRetryException


@pytest.fixture
def mock_mgr(mocker):
    mgr = mocker.Mock()
    mgr.web3.to_checksum_address.side_effect = lambda x: x.upper()
    return mgr


def test_with_mixed_events(mock_mgr):
    mock_mgr.pools_to_add_from_contracts = [
        (None, None, {"address": "addr1"}, None, None),
        (None, None, {"address": "addr2"}, None, None),
    ]
    mock_mgr.exchange_name_from_event.side_effect = ["exchange1", "exchange2"]
    mock_mgr.get_key_and_value.side_effect = [("key1", "value1"), ("key2", "value2")]
    mock_mgr.get_pool_info.side_effect = [None, "pool_info"]

    result = update_remaining_pools(mock_mgr)

    assert len(result) == 1
    assert ("ADDR1", "exchange1", {"address": "addr1"}, "key1", "value1") in result


def test_with_empty_events(mock_mgr):
    mock_mgr.pools_to_add_from_contracts = []

    result = update_remaining_pools(mock_mgr)

    assert result == []


def test_when_exchange_name_not_found(mock_mgr):
    mock_mgr.pools_to_add_from_contracts = [
        (None, None, {"address": "addr1"}, None, None)
    ]
    mock_mgr.exchange_name_from_event.return_value = None

    result = update_remaining_pools(mock_mgr)

    assert result == []




def setup_mock_mgr():
    mgr = MagicMock()
    mgr.blockchain = "ethereum"

    with open("fastlane_bot/data/test_pool_data.json") as f:
        test_pool_data = json.loads(f.read())

    mgr.pool_data = test_pool_data

    with open("fastlane_bot/data/event_test_data.json") as f:
        test_events = json.loads(f.read())
        pools_to_add_from_contracts = [
            (None, None, test_events[event], None, None)
            for event in test_events
            if "address" in test_events[event]
        ]

    for add, en, event, key, value in pools_to_add_from_contracts:
        assert "address" in event, f"address not found in {event.keys()}"
    mgr.pools_to_add_from_contracts = pools_to_add_from_contracts
    return mgr


@patch("fastlane_bot.events.async_event_update_utils.get_new_pool_data")
def test_successful_execution_first_try(mock_get_new_pool_data, mocker):
    mgr = setup_mock_mgr()
    mocker.patch("time.sleep")  # To avoid actual sleep calls
    current_block = max(
        int(pool[2]["blockNumber"])
        for pool in mgr.pools_to_add_from_contracts
        if "blockNumber" in pool[2]
    )
    mock_get_new_pool_data.return_value = mgr.pool_data
    run_async_update_with_retries(mgr, current_block=current_block, logging_path="")

    assert mock_get_new_pool_data.call_count == 1
    mgr.cfg.logger.error.assert_not_called()


@patch("fastlane_bot.events.async_event_update_utils.async_update_pools_from_contracts")
def test_successful_execution_after_retries(
    mock_async_update_pools_from_contracts, mocker
):
    mgr = setup_mock_mgr()
    mgr.get_key_and_value.side_effect = ("key1", "value1"), ("key2", "value2")
    mock_async_update_pools_from_contracts.side_effect = [
        AyncUpdateRetryException,
        None,
    ]
    mocker.patch("time.sleep")  # To avoid actual sleep calls

    with pytest.raises(StopIteration):
        run_async_update_with_retries(mgr, "current_block", "logging_path")


@patch("fastlane_bot.events.async_event_update_utils.get_new_pool_data")
@patch("fastlane_bot.events.async_event_update_utils.async_update_pools_from_contracts")
def test_failure_after_max_retries(
    mock_async_update_pools_from_contracts, mock_get_new_pool_data, mocker
):
    mgr = setup_mock_mgr()
    mock_async_update_pools_from_contracts.side_effect = AyncUpdateRetryException
    mocker.patch("time.sleep")  # To avoid actual sleep calls
    current_block = max(
        int(pool[2]["blockNumber"])
        for pool in mgr.pools_to_add_from_contracts
        if "blockNumber" in pool[2]
    )
    mgr.pool_data.append(
        {
            "address": "addr1",
            "last_updated_block": current_block,
            "exchange_name": "exchange1",
        }
    )
    mock_get_new_pool_data.return_value = mgr.pool_data

    with pytest.raises(ValueError) as exc_info:
        run_async_update_with_retries(
            mgr=mgr,
            current_block=current_block,
            logging_path="",
            retry_interval=1,
            max_retries=3,
        )

    assert "not enough values to unpack" in str(exc_info.value)
