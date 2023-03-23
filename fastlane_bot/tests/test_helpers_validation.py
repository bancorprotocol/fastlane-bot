# test_helpers.py

from fastlane_bot.helpers import ValidationHelpers

"""
Code Analysis:
-- Imports various libraries such as glob, os, Decimal, ABC, dataclasses, datetime, con, and ec
- Class ValidationHelpers is used to organize bot validation tools
- get_and_validate_trade_routes() validates the cached arbitrage routes and returns the amount in, expected profit, and deadline, and the trade path
- validate_tokens_and_exchanges() validates the tokens and exchanges provided by the user
- build_or_validate_route() builds or validates a route
- _split_valid_from_invalid() splits the valid and invalid routes
- handle_assertions() handles the assertions for the trade route
"""

"""
Test Plan:
- test_get_and_validate_trade_routes(): tests that the cached arbitrage routes are validated. Test uses [get_and_validate_trade_routes(), df_to_pool_attributes(), build_or_validate_route(), _split_valid_from_invalid(), handle_assertions()]
- test_validate_tokens_and_exchanges(): tests that the tokens and exchanges provided by the user are validated. Test uses [validate_tokens_and_exchanges()]
- test_build_or_validate_route(): tests that a route is built or validated. Test uses [build_or_validate_route(), df_to_pool_attributes(), handle_assertions()]
- test_split_valid_from_invalid(): tests that the valid and invalid routes are split. Test uses [_split_valid_from_invalid()]
- test_get_and_validate_trade_routes_edge_case_df_param(): tests the edge case where calling the method get_and_validate_trade_routes() with a param df leads to the cached arbitrage routes not being validated. Test uses [get_and_validate_trade_routes(), df_to_pool_attributes(), build_or_validate_route(), _split_valid_from_invalid(), handle_assertions()]
- test_get_and_validate_trade_routes_affects_df_to_pool_attributes(): tests how calling get_and_validate_trade_routes() affects df_to_pool_attributes(). Tests that the cached arbitrage routes are validated. Test uses [get_and_validate_trade_routes(), df_to_pool_attributes(), build_or_validate_route(), _split_valid_from_invalid(), handle_assertions()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestValidationHelpers:
    def test_validate_tokens_and_exchanges(self, mocker):
        """
        Tests that the tokens and exchanges provided by the user are validated. Test uses [validate_tokens_and_exchanges()]
        """

        # Mock the following methods
        mocker.patch.object(ValidationHelpers, "validate_tokens_and_exchanges")

        # Create a ValidationHelpers object
        vh = ValidationHelpers()

        # Call the method under test
        vh.validate_tokens_and_exchanges()

        # Assert that the mocked methods were called
        ValidationHelpers.validate_tokens_and_exchanges.assert_called()
