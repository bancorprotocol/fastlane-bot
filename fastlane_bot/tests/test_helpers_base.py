from datetime import datetime

import pytest
from mock.mock import patch

from fastlane_bot.constants import ec
from fastlane_bot.helpers import BaseHelper
from fastlane_bot.tests.utils import (
    make_mock_bot_instance,
)

# test_helpers.py

"""
Code Analysis:
-- This class is the main user interface for the FastLaneArbBot. 
- It is responsible for collecting data from the Ethereum blockchain, and then finding arbitrage opportunities between the supported exchanges.
- It has public attributes such as base_path, raiseonerror, filetype, verbose, n_jobs, number_of_retries, feeless_report_mode, execute_mode, exchanges, tokens, minimum_profit, search_delay, network_rpc, network_name, fastlane_contract_address, candidate_routes, external_pools, search_results, web3, arb_contract, local_account, public_address, nonce, and max_slippage.
- It has private attributes such as _best_route_report and _network.
- It has a property block_number which returns the current block number.
- It has a property best_route_report which returns the best route report.
- It has a property cached_trade_routes which gets the trade routes from the collection path.
- It has a property ts which returns a tuple of datetime and a string.
- It has a post-init method which configures the web3 instance, sets the local account, public address, nonce, and arb contract.
"""

"""
Test Plan:
- test_block_number_property(): tests that the block_number property returns the current block number. Test uses [block_number]
- test_best_route_report_property(): tests that the best_route_report property returns the best route report. Test uses [best_route_report]
- test_cached_trade_routes_property(): tests that the cached_trade_routes property gets the trade routes from the collection path. Test uses [cached_trade_routes]
- test_ts_property(): tests that the ts property returns a tuple of datetime and a string. Test uses [ts]
- test_exchanges_field_default_value(): tests the edge case where the exchanges field has the default value. Test uses [exchanges]
- test_post_init_method(): tests that the post-init method configures the web3 instance, sets the local account, public address, nonce, and arb contract. Test uses [__post_init__]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestBaseHelper:
    def test_block_number_property(self, mocker):
        """
        Tests that the block_number property returns the current block number.
        """
        # Arrange
        bot = make_mock_bot_instance()

        # Act
        block_number = bot.block_number

        assert block_number > 0
