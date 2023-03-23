# test_routes.py

from fastlane_bot.routes import ConstantFunctionRoute, ConstantProductRoute
from fastlane_bot.tests.utils import (
    make_mock_constant_function_route,
    make_mock_constant_product_route,
)

"""
Code Analysis:
-- This class is used to auto-determine the route type and instantiate the correct route class.
- It takes a list of liquidity pools in the trade path as a parameter.
- It checks the type of the second liquidity pool in the trade path and instantiates the corresponding route class.
- If the second liquidity pool is a UniswapV3LiquidityPool, it instantiates a ConstantFunctionRoute with a UniswapV3RouteSolver.
- If the second liquidity pool is an OrderBookDexLiquidityPool, it instantiates an OrderBookDexRoute with a CarbonV1RouteSolver.
- If the second liquidity pool is neither of the above, it instantiates a ConstantProductRoute with a ConstantProductRouteSolver.
- It then sets the class to the instantiated route class and copies the attributes of the instantiated route class to the current class.
"""

"""
Test Plan:
- test_instantiate_route_with_uniswap_v3_liquidity_pool(): tests that a ConstantFunctionRoute is instantiated when the second liquidity pool in the trade path is a UniswapV3LiquidityPool. Test uses [__post_init__(), isinstance(), ConstantFunctionRoute()]
- test_instantiate_route_with_order_book_dex_liquidity_pool(): tests that an OrderBookDexRoute is instantiated when the second liquidity pool in the trade path is an OrderBookDexLiquidityPool. Test uses [__post_init__(), isinstance(), OrderBookDexRoute()]
- test_instantiate_route_with_other_liquidity_pool(): tests that a ConstantProductRoute is instantiated when the second liquidity pool in the trade path is neither a UniswapV3LiquidityPool nor an OrderBookDexLiquidityPool. Test uses [__post_init__(), isinstance(), ConstantProductRoute()]
- test_copy_attributes_to_route(): tests that the attributes of the instantiated route class are copied to the current class. Test uses [__post_init__(), __dict__]
- test_edge_case_instantiate_route_with_empty_trade_path(): tests the edge case where calling the __post_init__() method with an empty trade_path leads to an error. Test uses [__post_init__(), trade_path]
- test_how_instantiate_route_affects_copy_attributes(): tests how calling __post_init__() affects the copying of attributes to the current class. Tests that the attributes of the instantiated route class are correctly copied to the current class. Test uses [__post_init__(), __dict__]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestRoute:
    def test_instantiate_constant_function_route(self):
        """
        Tests that a ConstantFunctionRoute is instantiated when the second liquidity pool in the trade path is a UniswapV3LiquidityPool.
        """

        # Instantiate the Route class with the mocked trade_path
        route = make_mock_constant_function_route()

        # Verify that ConstantFunctionRoute was instantiated with the correct parameters
        assert isinstance(route, ConstantFunctionRoute)

    def test_instantiate_constant_product_route(self):
        """
        Tests that a ConstantFunctionRoute is instantiated when the second liquidity pool in the trade path is a UniswapV3LiquidityPool.
        """

        # Instantiate the Route class with the mocked trade_path
        route = make_mock_constant_product_route()

        # Verify that ConstantFunctionRoute was instantiated with the correct parameters
        assert isinstance(route, ConstantProductRoute)

    def test_reverse_constant_function_route(self):
        """
        Tests that a ConstantFunctionRoute can be reversed.
        """

        # Instantiate the Route class with the mocked trade_path
        route = make_mock_constant_function_route()
        p1, p2, p3 = route.trade_path
        p1t0 = p1.tkn0.symbol
        p1t1 = p1.tkn1.symbol
        p2t0 = p2.tkn0.symbol
        p2t1 = p2.tkn1.symbol
        p3t0 = p3.tkn0.symbol
        p3t1 = p3.tkn1.symbol
        route.reverse_route(skip_idx=1)
        route.assert_bnt_order()
        p1_r, p2_r, p3_r = route.trade_path
        p1t0_r = p1_r.tkn0.symbol
        p1t1_r = p1_r.tkn1.symbol
        p2t0_r = p2_r.tkn0.symbol
        p2t1_r = p2_r.tkn1.symbol
        p3t0_r = p3_r.tkn0.symbol
        p3t1_r = p3_r.tkn1.symbol

        # Verify that ConstantFunctionRoute was instantiated with the correct parameters
        assert p1t0 == p3t1_r
        assert p1t1 == p3t0_r
        assert p2t0 == p2t0_r
        assert p2t1 == p2t1_r
        assert p3t0 == p1t1_r
        assert p3t1 == p1t0_r

    def test_reverse_constant_product_route(self):
        """
        Tests that a ConstantProductRoute can be reversed.
        """

        # Instantiate the Route class with the mocked trade_path
        route = make_mock_constant_product_route()
        p1, p2, p3 = route.trade_path
        p1t0 = p1.tkn0.symbol
        p1t1 = p1.tkn1.symbol
        p2t0 = p2.tkn0.symbol
        p2t1 = p2.tkn1.symbol
        p3t0 = p3.tkn0.symbol
        p3t1 = p3.tkn1.symbol
        route.reverse_route()
        p1_r, p2_r, p3_r = route.trade_path
        p1t0_r = p1_r.tkn0.symbol
        p1t1_r = p1_r.tkn1.symbol
        p2t0_r = p2_r.tkn0.symbol
        p2t1_r = p2_r.tkn1.symbol
        p3t0_r = p3_r.tkn0.symbol
        p3t1_r = p3_r.tkn1.symbol

        # Verify that ConstantProductRoute was instantiated with the correct parameters
        assert p1t0 == p3t1_r
        assert p1t1 == p3t0_r
        assert p2t0 == p2t1_r
        assert p2t1 == p2t0_r
        assert p3t0 == p1t1_r
        assert p3t1 == p1t0_r
