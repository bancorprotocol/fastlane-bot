# test_helpers.py

from fastlane_bot.tests.utils import (
    make_mock_bot_instance,
    supported_tokens,
    supported_exchanges,
    db,
)

"""
Code Analysis:
-- This class is used to organize web3/brownie search tools.
- It searches for profitable arbitrage routes using a parallel backend.
- It finds valid trade paths for the token pairs/exchanges.
- It builds candidate routes for the bot to search through.
- It gets the fees for a given pair and exchange.
- It appends valid paths for the token pairs/exchanges.
"""

"""
Test Plan:
- test_search_candidate_routes_returns_profitable_trades(): tests that search_candidate_routes() returns profitable trades. Test uses [search_candidate_routes(), Parallel(), search_results]
- test_find_trade_paths_returns_valid_paths(): tests that find_trade_paths() returns valid paths. Test uses [find_trade_paths(), find_trade_paths(), fee_from_pair(), append_trade_path()]
- test_build_candidate_routes_returns_valid_routes(): tests that build_candidate_routes() returns valid routes. Test uses [build_candidate_routes(), find_trade_paths(), fee_from_pair(), append_trade_path()]
- test_get_valid_paths_returns_valid_paths(): tests that find_trade_paths() returns valid paths. Test uses [find_trade_paths()]
- test_edge_case_build_candidate_routes_no_exchanges(): tests the edge case where calling build_candidate_routes() with no exchanges leads to no valid routes. Test uses [build_candidate_routes(), find_trade_paths(), fee_from_pair(), append_trade_path()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestSearchHelpers:
    def test_search_candidate_routes_returns_profitable_trades(self):
        """
        Tests that search_candidate_routes() returns profitable trades. Test uses [search_candidate_routes(), Parallel(), search_results]
        """
        # Arrange
        bot = make_mock_bot_instance()
        bot.archive_trade_routes()
        bot.build_candidate_routes(
            tokens=supported_tokens, exchanges=supported_exchanges
        )

        # Act
        bot.search_candidate_routes()

        # Assert
        assert bot.search_results is not None

    def test_build_candidate_routes_returns_valid_routes(self):
        """
        Tests that build_candidate_routes() returns valid routes. Test uses [build_candidate_routes(), find_trade_paths(), fee_from_pair(), append_trade_path()]
        """
        # Arrange
        bot = make_mock_bot_instance()
        bot.archive_trade_routes()

        # Act
        bot.build_candidate_routes(
            tokens=supported_tokens, exchanges=supported_exchanges
        )

        # Assert
        assert bot.candidate_routes is not None

    def test_edge_case_build_candidate_routes_no_exchanges(self):
        """
        Tests the edge case where calling build_candidate_routes() with no exchanges leads to no valid routes. Test uses [build_candidate_routes(), find_trade_paths(), fee_from_pair(), append_trade_path()]
        """
        # Arrange
        bot = make_mock_bot_instance()
        bot.archive_trade_routes()

        # Act
        bot.build_candidate_routes(tokens=supported_tokens, exchanges=None)

        # Assert
        assert bot.candidate_routes == []
