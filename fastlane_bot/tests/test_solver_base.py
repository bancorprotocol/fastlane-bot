from _decimal import Decimal

import pytest

from fastlane_bot.solvers import BaseRouteSolver

# test_solvers.py

"""
Code Analysis:
-- BaseRouteSolver is a base class for all route solvers.
- It contains an abstract method `simulate()` which is used to simulate a trade for route solvers.
- It also contains a static method `single_trade_result()` which is used to calculate the trade result for a single trade in a constant product pool.
- It also contains a static method `log_route_summary()` which is used to log the route summary.
"""

"""
Test Plan:
- test_simulate_happy_path(): tests that simulate() works as expected when given valid parameters. Test uses [simulate(), single_trade_result(), log_route_summary()]
- test_simulate_invalid_route(): tests the edge case where calling simulate() with an invalid route leads to an error. Test uses [simulate()]
- test_simulate_invalid_trade_path(): tests the edge case where calling simulate() with an invalid trade path leads to an error. Test uses [simulate()]
- test_single_trade_result_happy_path(): tests that single_trade_result() works as expected when given valid parameters. Test uses [single_trade_result()]
- test_single_trade_result_invalid_param(): tests the edge case where calling single_trade_result() with an invalid parameter leads to an error. Test uses [single_trade_result()]
- test_how_simulate_affects_single_trade_result(): tests how calling simulate() affects single_trade_result(). Tests that the result of simulate() is equal to the result of single_trade_result(). Test uses [simulate(), single_trade_result()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestBaseRouteSolver:
    def test_single_trade_result_invalid_param(self):
        """
        Tests the edge case where calling single_trade_result() with an invalid parameter leads to an error.
        """
        # Arrange
        tkns_in = None
        tkn0_amt = Decimal(2)
        tkn1_amt = Decimal(3)
        fee = Decimal(0.1)

        # Act & Assert
        with pytest.raises(TypeError):
            BaseRouteSolver.single_trade_result(tkns_in, tkn0_amt, tkn1_amt, fee)
