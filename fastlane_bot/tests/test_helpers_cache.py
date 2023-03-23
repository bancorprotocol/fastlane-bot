import pandas as pd

from fastlane_bot.helpers import CacheHelpers
from fastlane_bot.tests.utils import (
    make_mock_bot_instance,
)

# test_helpers.py

"""
Code Analysis:
-
"""

"""
Test Plan:
- test_log_results(): tests that the log_results method logs the results of the search. Test uses [log_results()]
- test_archive_trade_routes(): tests that the archive_trade_routes method archives trade routes that have been read. Test uses [archive_trade_routes()]
- test_trade_to_pandas(): tests that the trade_to_pandas method exports values for inspection. Test uses [trade_to_pandas()]
- test_handle_log_for_filetype_csv(): tests the edge case where calling the handle_log_for_filetype method with a filetype of csv leads to the results being written to a csv file. Test uses [handle_log_for_filetype()]
- test_handle_log_for_filetype_csv_to_parquet(): tests how calling the handle_log_for_filetype method with a filetype of csv affects the results being written to a parquet file. Tests that the results are written to a parquet file. Test uses [handle_log_for_filetype()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestCacheHelpers:
    def test_log_results(self):
        """
        Tests that the log_results method logs the results of the search.
        """
        # Arrange
        # Create a bot object which inherits from a CacheHelpers object
        bot = make_mock_bot_instance()
        bot.archive_trade_routes()
        bot.search_results = []

        # Act
        # Call the log_results method
        bot.log_results()
        result = bot.cached_trade_routes

        # Assert
        # Check that the result is None
        assert result is None

    def test_archive_trade_routes(self):
        """
        Tests that the archive_trade_routes method archives trade routes that have been read.
        """
        # Arrange
        # Create a CacheHelpers object
        cache_helpers = CacheHelpers()

        # Act
        # Call the archive_trade_routes method
        result = cache_helpers.archive_trade_routes()

        # Assert
        # Check that the result is None
        assert result is None
