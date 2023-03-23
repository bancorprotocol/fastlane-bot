"""
Class objects for route solvers

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from abc import abstractmethod, ABC
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List, Tuple

from fastlane_bot.constants import ec
from fastlane_bot.pools import LiquidityPool
from fastlane_bot.utils import swap_bancor_eth_to_weth, convert_to_correct_decimal

# *******************************************************************************************
# RouteSolver Base - Base Class for Route Solvers
# *******************************************************************************************
logger = ec.DEFAULT_LOGGER


@dataclass
class BaseRouteSolver:
    """
    Base class for all route solvers.
    """

    _next_id: int = 0
    route: Any = None  # Any is used to avoid circular imports. (`ConstantFunctionRoute` or `ConstantFunctionRoute`)

    def next_id(self) -> int:
        """
        Get the next id
        """
        self._next_id += 1
        return self._next_id

    @abstractmethod
    def simulate(self, trade_path: List[LiquidityPool]) -> Dict[str, Any]:
        """
        Simulate the trade for route solvers
        """
        pass

    @staticmethod
    def single_trade_result(
        tkns_in: Decimal, tkn0_amt: Decimal, tkn1_amt: Decimal, fee: Decimal
    ) -> Decimal:
        """
        Calculate the trade result for a single trade in a constant product pool
        :param tkns_in:  Amount of tokens to trade
        :param tkn0_amt:  Amount of token 0 in the pool
        :param tkn1_amt:  Amount of token 1 in the pool
        :param fee:  Fee for the pool
        :return:  Amount of tokens received
        """

        return (tkns_in * tkn1_amt * (Decimal(1) - Decimal(fee))) / (tkns_in + tkn0_amt)

    @staticmethod
    def log_route_summary(route: Any):
        """
        Log the route summary
        """
        key: str = (
            f"************* {route.p2.exchange} ************* \n"
            f"{route.p1.tkn0.symbol}_{route.p1.tkn1.symbol}->"
            f"{route.p2.tkn0.symbol}_{route.p2.tkn1.symbol}->"
            f"{route.p3.tkn0.symbol}_{route.p3.tkn1.symbol}"
        )
        logger.debug(
            f"\n" f"End: {type} \n" f"key: {key} \n" f"BNT profit: {route.profit} \n"
        )
        key_amts: str = (
            f"{route.p1.tkn0.amt}_{route.p1.tkn1.amt}->\n"
            f"{route.p2.tkn0.amt}_{route.p2.tkn1.amt}->\n"
            f"{route.p3.tkn0.amt}_{route.p3.tkn1.amt} \n"
        )
        logger.debug(
            f"token balances/liquidity: {key_amts}, \n"
            f"trade amts: {route.trade_path_amts} \n"
        )


# *******************************************************************************************
# RouteSolver - Constant Product Solver
# *******************************************************************************************


@dataclass
class ConstantProductRouteSolver(BaseRouteSolver, ABC):
    """
    Constant Product Trade Solver

    ******************************* NOTE ****************************************
    See all method param definitions in the Route passed in via the :param route.
    *****************************************************************************
    """

    def simulate(self, trade_path: List[LiquidityPool] = None) -> Any or None:
        """
        Main trade function for constant product trade routes
        """
        route: Any = (
            self.route.copy_route()
        )  # Any is used to avoid circular imports. (`ConstantFunctionRoute` or `ConstantFunctionRoute`)
        p1: LiquidityPool = route.p1
        p2: LiquidityPool = route.p2
        p3: LiquidityPool = route.p3

        key: str = (
            f"{p1.tkn0.symbol}_{p1.tkn1.symbol}->"
            f"{p2.tkn0.symbol}_{p2.tkn1.symbol}->"
            f"{p3.tkn0.symbol}_{p3.tkn1.symbol}"
        )
        logger.debug(f"key before reverse \n: {key}")
        trade_result: Dict[str, Any]

        if (
            p1 is None
            or p3 is None
            or p1.tkn0.amt == 0
            or p1.tkn1.amt == 0
            or p3.tkn0.amt == 0
            or p3.tkn1.amt == 0
        ):
            logger.debug("One of the pools was 'None'")
            return None
        path = self.calc_max_arb(route)
        if path[0] <= 0:
            path = self._extracted_from_simulate(route)
        route.trade_path_amts = path
        self.log_route_summary(route)
        return route if route.profit > ec.DEFAULT_MIN_PROFIT else None

    def _extracted_from_simulate(self, route):
        route.reverse_route()

        p1: LiquidityPool = route.p1
        p2: LiquidityPool = route.p2
        p3: LiquidityPool = route.p3
        key: str = (
            f"{p1.tkn0.symbol}_{p1.tkn1.symbol}->"
            f"{p2.tkn0.symbol}_{p2.tkn1.symbol}->"
            f"{p3.tkn0.symbol}_{p3.tkn1.symbol}"
        )
        logger.debug(f"key after reverse \n: {key}")
        return self.calc_max_arb(route)

    def calc_max_arb(self, route):
        """
        Calculate the max arbitrage amount for a given route
        :param route:  Route
        :return:  List of trade amounts
        """
        max_trade_amt = self.calc_arb_trade_constant_product(
            route,
        )
        first_hop = self.single_trade_result(
            max_trade_amt, route.p1.tkn0.amt, route.p1.tkn1.amt, Decimal(route.p1.fee)
        )
        second_hop = self.single_trade_result(
            first_hop, route.p2.tkn0.amt, route.p2.tkn1.amt, Decimal(route.p2.fee)
        )
        third_hop_result = self.single_trade_result(
            second_hop, route.p3.tkn0.amt, route.p3.tkn1.amt, Decimal(route.p3.fee)
        )
        logger.info(
            f"calc_max_arb {route.p1.tkn0.symbol}_{route.p1.tkn1.symbol}->{route.p2.tkn0.symbol}_{route.p2.tkn1.symbol}->{route.p3.tkn0.symbol}_{route.p3.tkn1.symbol} \n{route.p1.tkn0.amt}, {route.p1.tkn1.amt}, {route.p1.fee} \n{route.p2.tkn0.amt}, {route.p2.tkn1.amt}, {route.p2.fee}, \n{route.p3.tkn0.amt}, {route.p3.tkn1.amt}, {route.p3.fee}\ntrades {max_trade_amt}, {first_hop}, {second_hop}, {third_hop_result}\nprofit = {third_hop_result - max_trade_amt}\n\n"
        )

        return [max_trade_amt] + [first_hop, second_hop, third_hop_result]

    @staticmethod
    def calc_arb_trade_constant_product(
        route: Any,  # Any is used to avoid circular imports. (`ConstantFunctionRoute` or `ConstantFunctionRoute`)
    ) -> Decimal:
        """
        Calculate the max arbitrage amount for a given route
        :param route:  Route
        :return:  Max arbitrage amount for a given constant product route
        """
        r = route
        val = Decimal(
            (
                -r.p2.tkn0.amt * r.p3.tkn0.amt * r.p1.tkn0.amt
                + (
                    Decimal("-1")
                    * r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                    * Decimal(r.p2.fee)
                    * Decimal(r.p3.fee)
                    * Decimal(r.p1.fee)
                    + r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                    * Decimal(r.p2.fee)
                    * Decimal(r.p3.fee)
                    + r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                    * Decimal(r.p2.fee)
                    * Decimal(r.p1.fee)
                    - r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                    * Decimal(r.p2.fee)
                    + r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                    * Decimal(r.p3.fee)
                    * Decimal(r.p1.fee)
                    - r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                    * Decimal(r.p3.fee)
                    - r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                    * Decimal(r.p1.fee)
                    + r.p2.tkn0.amt
                    * r.p3.tkn0.amt
                    * r.p1.tkn0.amt
                    * r.p2.tkn1.amt
                    * r.p3.tkn1.amt
                    * r.p1.tkn1.amt
                )
                ** Decimal("0.5")
            )
            / (
                r.p2.tkn0.amt * r.p3.tkn0.amt
                - r.p3.tkn0.amt * r.p1.tkn1.amt * Decimal(r.p1.fee)
                + r.p3.tkn0.amt * r.p1.tkn1.amt
                + r.p2.tkn1.amt * r.p1.tkn1.amt * Decimal(r.p2.fee) * Decimal(r.p1.fee)
                - r.p2.tkn1.amt * r.p1.tkn1.amt * Decimal(r.p2.fee)
                - r.p2.tkn1.amt * r.p1.tkn1.amt * Decimal(r.p1.fee)
                + r.p2.tkn1.amt * r.p1.tkn1.amt
            )
        )
        return max(val, Decimal("0"))


# *******************************************************************************************
# RouteSolver - Uniswap V3 Solver TODO: This is still ugly and needs to be refactored.
# *******************************************************************************************


@dataclass
class UniswapV3RouteSolver(BaseRouteSolver):
    """
    This class is used to solve the arbitrage for UniV3 routes

    ******************************* NOTE ****************************************
    See all method param definitions in the Route passed in via the :param route.
    *****************************************************************************
    """

    route: Any = None  # Any is used to avoid circular imports. (should be `ConstantFunctionRoute`)

    def __post_init__(self):
        from fastlane_bot.routes import ConstantFunctionRoute

        # Set the route type to the correct type for type hinting
        self.route: ConstantFunctionRoute = self.route

    def simulate(self, trade_path: List[LiquidityPool]) -> Any or None:
        """
        Takes 3 liquidity pools with token balances already populated as args, the first and last being Bancor V3 pools,
        and calculates potential arbitrage
        """
        from fastlane_bot.routes import ConstantFunctionRoute

        route: ConstantFunctionRoute = (
            self.route.copy_route()
        )  # Any is used to avoid circular imports. (`ConstantFunctionRoute` or `ConstantFunctionRoute`)
        p1: LiquidityPool = route.p1
        p2: LiquidityPool = route.p2
        p3: LiquidityPool = route.p3

        key: str = (
            f"{p1.tkn0.symbol}_{p1.tkn1.symbol}->"
            f"{p2.tkn0.symbol}_{p2.tkn1.symbol}->"
            f"{p3.tkn0.symbol}_{p3.tkn1.symbol}"
        )
        logger.debug(f"Begin: Constant Function Solver \n: {key}")
        self.log_route_summary(route)
        if (
            p1 is None
            or p3 is None
            or p1.tkn0.amt == 0
            or p1.tkn1.amt == 0
            or p2.liquidity == 0
            or p2.sqrt_price_q96 == 0
            or p3.tkn0.amt == 0
            or p3.tkn1.amt == 0
        ):
            logger.debug("One of the pools was 'None'")
            return None
        logger.debug(
            f"{route.p1.tkn0.symbol}_{route.p1.tkn1.symbol}->{route.p2.tkn0.symbol}_{route.p2.tkn1.symbol}->{route.p3.tkn0.symbol}_{route.p3.tkn1.symbol}, {route.p1.tkn0.decimals} {route.p1.tkn1.decimals} {route.p2.tkn0.decimals} {route.p2.tkn1.decimals} {route.p3.tkn0.decimals} {route.p3.tkn1.decimals} {route.p1.tkn0.amt}, {route.p1.tkn1.amt}, {route.p1.fee}, {route.p2.sqrt_price_q96}, {route.p2.liquidity}, {route.p2.fee}, {route.p3.tkn0.amt}, {route.p3.tkn1.amt}, {route.p3.fee}"
        )
        result = self.best_route_univ3(route)
        if not result:
            logger.debug(f"No profitable route found for {key}")
            return None
        result = (
            result
            if Decimal(str(result.profit)) > Decimal(str(ec.DEFAULT_MIN_PROFIT))
            else None
        )
        if not result:
            logger.debug(f"No profitable route found for UNI-V3 {key}")
            return None
        result = (
            result
            if all(Decimal(str(amt)) > Decimal("0") for amt in result.trade_path_amts)
            else None
        )
        if not result:
            logger.debug(f"No profitable route found for {key}")
            return None
        logger.debug(f"UNI V3 profit = {result.profit} vs {ec.DEFAULT_MIN_PROFIT}")
        return result

    @staticmethod
    def multiply_by_decimals(number):
        """the adjusted amount - 10 to the power of the number of decimal places"""
        return Decimal(10**number)

    @staticmethod
    def convert_decimals(amt: Decimal, n: int) -> Decimal:
        """
        Utility function to convert to Decimaling point value of a specific precision.
        """
        if amt is None:
            return Decimal("0")
        return Decimal(str(amt / (Decimal("10") ** Decimal(str(n)))))

    @staticmethod
    def convert_to_correct_decimal(address: str, amt: Decimal) -> Decimal:
        """
        Uses decimal_ct_map to convert a Decimaling point value to the correct precision.
        """
        return convert_to_correct_decimal(address, amt)

    def calc_amount1(self, liquidity, sqrt_p, price_next) -> Decimal:
        """
        Returns the amount of token 1 given the liquidity, sqrt price, and price next
        """
        return self.route.p2.calc_amount1(liquidity, sqrt_p, price_next)

    def calc_amount0(self, liquidity, sqrt_p, price_next) -> Decimal:
        """
        Returns the amount of token 0 given the liquidity, sqrt price, and price next
        """
        return self.route.p2.calc_amount0(liquidity, sqrt_p, price_next)

    def swap_token0_in(
        self,
        amount_in: Decimal,
        liquidity: Decimal,
        sqrt_p: Decimal,
        decimal_tkn0_modifier: Decimal,
        decimal_tkn1_modifier: Decimal,
    ) -> Decimal:
        """Returns amount out when swapping from Token 0 to Token 1, when you do not cross a tick"""
        amount_decimal_adjusted = amount_in * decimal_tkn0_modifier

        liquidity_x96 = Decimal(liquidity * ec.Q96)
        price_next = Decimal(
            (liquidity_x96 * sqrt_p)
            / (liquidity_x96 + amount_decimal_adjusted * sqrt_p)
        )
        amount_out = self.calc_amount1(liquidity, sqrt_p, price_next)
        return Decimal(amount_out / decimal_tkn1_modifier)

    def swap_token1_in(
        self,
        amount_in: Decimal,
        liquidity: Decimal,
        sqrt_price: Decimal,
        decimal_tkn0_modifier: Decimal,
        decimal_tkn1_modifier: Decimal,
    ) -> Decimal:
        """Returns amount out when swapping from Token 1 to Token 0, when you do not cross a tick"""
        amount = amount_in * decimal_tkn1_modifier
        price_diff = Decimal((amount * ec.Q96) / liquidity)
        price_next = Decimal(sqrt_price + price_diff)
        amount_out = self.calc_amount0(liquidity, price_next, sqrt_price)
        return Decimal(amount_out / decimal_tkn0_modifier)

    @staticmethod
    def get_net_liquidity_for_next_tick(
        uni_v3_position: LiquidityPool, next_tick: Decimal
    ) -> Decimal:
        """This function gets the Liquidity Net value from the specified tick in a Uni V3 pool. This allows you to determine the Liquidity in the next range when crossing a tick boundary."""
        next_tick = int(next_tick)
        tick_stats = uni_v3_position.contract.ticks(next_tick)
        liquidity_net = tick_stats[1]
        return Decimal(liquidity_net)

    def get_next_liquidity_range(
        self,
        uni_v3_position: LiquidityPool,
        current_max_tick: Decimal,
        current_liquidity: Decimal,
        is_token0: bool,
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, bool]:
        """This calculates the details of the next tick range when crossing ticks"""
        tick_changes = 0
        liquidity_change = 0
        liquidity_change = self.get_net_liquidity_for_next_tick(
            uni_v3_position, current_max_tick
        )
        while liquidity_change == 0 and tick_changes < ec.MAX_LIQUIDITY_CHECK_LOOPS:
            _tick_mod = (
                -(uni_v3_position.tick_spacing * tick_changes)
                if is_token0
                else (uni_v3_position.tick_spacing * tick_changes)
            )
            liquidity_change = self.get_net_liquidity_for_next_tick(
                uni_v3_position, current_max_tick + _tick_mod
            )

            tick_changes += 1

        next_range_exists = bool(
            (liquidity_change > 0 or liquidity_change < 0)
            and current_liquidity - liquidity_change != 0
            if is_token0
            else current_liquidity + liquidity_change
        )
        next_liquidity = (
            current_liquidity - liquidity_change
            if is_token0
            else current_liquidity + liquidity_change
        )
        next_starting_tick = (
            (current_max_tick - (uni_v3_position.tick_spacing * tick_changes))
            if is_token0
            else (current_max_tick + (uni_v3_position.tick_spacing * tick_changes))
        )
        next_max_tick = (
            next_starting_tick - uni_v3_position.tick_spacing
            if is_token0
            else next_starting_tick + uni_v3_position.tick_spacing
        )

        next_sqrt_p = self.tick_to_sqrt_price_times_q96(next_starting_tick)
        next_max_in, next_max_out = (
            self.calculate_max_swap_token0(
                next_sqrt_p,
                self.tick_to_sqrt_price_times_q96(next_max_tick),
                next_liquidity,
                uni_v3_position.t0decimal_mod,
                uni_v3_position.t1decimal_mod,
            )
            if is_token0
            else self.calculate_max_swap_token1(
                next_sqrt_p,
                self.tick_to_sqrt_price_times_q96(next_max_tick),
                next_liquidity,
                uni_v3_position.t0decimal_mod,
                uni_v3_position.t1decimal_mod,
            )
        )

        return (
            next_liquidity,
            next_starting_tick,
            next_max_tick,
            next_sqrt_p,
            next_max_in,
            next_max_out,
            next_range_exists,
        )

    def calculate_swap_output_uni_v3(
        self,
        uni_v3_position: LiquidityPool,
        amount_in: Decimal,
        token_in: str,
        liquidity: Decimal,
        sqrt_price: Decimal,
        max_in: Decimal,
        max_out: Decimal,
        current_max_tick,
        is_first_entry: bool,
        cross_tick_count: int,
    ) -> Decimal:
        """This calculates and returns the swap output from a Uniswap V3 pool. When crossing a tick range, it recursively calls itself while adding the max output for the given range until it reaches a range it cannot exhaust"""
        cross_tick_count += 1
        if cross_tick_count > ec.MAX_LIQUIDITY_CHECK_LOOPS:
            return Decimal("0")

        # Stores the total output of the trade for cross-tick trades
        ttl_max_trade_1 = Decimal("0")
        token_in = swap_bancor_eth_to_weth(token_in)
        fee = Decimal(str(int(uni_v3_position.fee) / 1000000))

        # takes the fee from the swap in a single time
        total_in_after_fee = (
            (amount_in * (1 - Decimal(fee))) if is_first_entry else amount_in
        )
        if total_in_after_fee <= max_in:
            return (
                self.swap_token0_in(
                    total_in_after_fee,
                    liquidity,
                    sqrt_price,
                    uni_v3_position.t0decimal_mod,
                    uni_v3_position.t1decimal_mod,
                )
                if token_in == uni_v3_position.tkn0.address
                else self.swap_token1_in(
                    total_in_after_fee,
                    liquidity,
                    sqrt_price,
                    uni_v3_position.t0decimal_mod,
                    uni_v3_position.t1decimal_mod,
                )
            )
        trade_result = 0

        ttl_max_trade_1 += max_out
        leftover_token_in = total_in_after_fee - max_in

        (
            next_liquidity,
            next_starting_tick,
            next_max_tick,
            next_sqrt_p,
            next_max_in,
            next_max_out,
            next_range_exists,
        ) = self.get_next_liquidity_range(
            uni_v3_position,
            current_max_tick,
            liquidity,
            token_in == uni_v3_position.tkn0.address,
        )
        if next_range_exists:
            trade_result = self.calculate_swap_output_uni_v3(
                uni_v3_position,
                leftover_token_in,
                token_in,
                next_liquidity,
                next_sqrt_p,
                next_max_in,
                next_max_out,
                next_max_tick,
                False,
                cross_tick_count,
            )

        ttl_max_trade_1 += trade_result

        return ttl_max_trade_1

    def recalculate_pools_for_cross_tick_trades(
        self,
        tokens_in: Decimal,
        p1: LiquidityPool,
        p2: LiquidityPool,
        uni_liquidity: Decimal,
        uni_max_tick: Decimal,
        p3: LiquidityPool,
        max_input_p2: Decimal,
        max_output_p2: Decimal,
        total_loops: int,
    ) -> Decimal:
        """This Function recursively finds the maximum arbitrage trade by checking if a trade will cross a Uniswap pool's tick boundary and recalculates each pool given the new state."""
        total_max_trade_in = Decimal("0")
        if total_loops >= ec.MAX_CROSS_TICK_CHECKS:
            return total_max_trade_in
        total_loops += 1
        is_swapping_token0 = swap_bancor_eth_to_weth(p1.tkn1.address) == p2.tkn0.address

        firsttrade_result = self.single_trade_result_constant_product(
            tokens_in, p1.tkn0.amt, p1.tkn1.amt, p1.fee
        )
        # If there isn't a tick-range cross, return the amount in
        if (firsttrade_result * (1 - Decimal(p2.fee))) <= max_input_p2:
            return tokens_in

        # Calculate the max input to the Uni pool after taking the trading fee
        max_input_uni_fee_adjusted = max_input_p2 / (1 - Decimal(p2.fee))

        # Calculate new tkn0 tkn1 values of Pool 1 given the output of the max swap to the Uni V3 pool before crossing a tick
        (
            pool1_new_tkn0,
            pool1_new_tkn1,
        ) = self.get_new_tkn_values_given_out_constant_product(
            tkns_out=max_input_uni_fee_adjusted,
            tkn0_amt=p1.tkn0.amt,
            tkn1_amt=p1.tkn1.amt,
        )

        # Calculate the input to the first pool that results in an output that crosses the Uniswap pool's tick threshold
        max_first_trade = self.get_in_given_out_constant_product(
            max_input_uni_fee_adjusted, pool1_new_tkn0, pool1_new_tkn1, p1.fee
        )

        # Add the trade into the first pool to the total trade being returned
        total_max_trade_in += max_first_trade
        # Calculate the state of the Uniswap pool after crossing the tick range
        (
            next_liquidity,
            next_starting_tick,
            next_max_tick,
            next_sqrt_p,
            next_max_in,
            next_max_out,
            next_range_exists,
        ) = self.get_next_liquidity_range(
            p2, uni_max_tick, uni_liquidity, is_swapping_token0
        )

        if next_range_exists:
            # Update the constant product pools to reflect the trades
            new_pool1 = self.get_liquidity_pool_after_trade_constant_product(
                max_first_trade, p1, True
            )
            new_pool3 = self.get_liquidity_pool_after_trade_constant_product(
                max_output_p2, p3, False
            )
            new_arb_result = self.calculate_max_arb_cp_uni3_cp(
                new_pool1.tkn0.amt,
                new_pool1.tkn1.amt,
                new_pool1.fee,
                next_liquidity,
                next_sqrt_p,
                p2.t0decimal_mod,
                p2.t1decimal_mod,
                p2.fee,
                new_pool3.tkn0.amt,
                new_pool3.tkn1.amt,
                new_pool3.fee,
                is_swapping_token0,
            )

            # Add the results from tick-ranges recursively. If the calculated arb from the next range is less than 0, return 0
            total_max_trade_in += (
                self.recalculate_pools_for_cross_tick_trades(
                    new_arb_result,
                    new_pool1,
                    p2,
                    next_liquidity,
                    next_max_tick,
                    new_pool3,
                    next_max_in,
                    next_max_out,
                    total_loops,
                )
                if new_arb_result > 0
                else 0
            )

        return total_max_trade_in

    def calc_trade_result(
        self,
        tokens_in: Decimal,
        p1: LiquidityPool,
        p2: LiquidityPool,
        p3: LiquidityPool,
    ) -> List[Decimal]:
        """This function returns TradeAmounts object containing trade results of each trade in a series of 3 trades"""

        token_address_in = swap_bancor_eth_to_weth(p1.tkn1.address)
        is_tkn0 = token_address_in == p2.tkn0.address

        # Max that can go into Uniswap pool before next tick range
        max_in = p2.max_in_swap_token_0 if is_tkn0 else p2.max_in_swap_token_1
        max_out = p2.max_out_swap_token_0 if is_tkn0 else p2.max_out_swap_token_1

        # Output of first trade
        first_trade_result = self.single_trade_result_constant_product(
            tokens_in, p1.tkn0.amt, p1.tkn1.amt, p1.fee
        )
        max_tick = p2.lower_tick if is_tkn0 else p2.upper_tick

        # Output of second trade
        second_trade_result = self.calculate_swap_output_uni_v3(
            p2,
            first_trade_result,
            token_address_in,
            p2.liquidity,
            p2.sqrt_price_q96,
            max_in,
            max_out,
            max_tick,
            True,
            0,
        )

        # Output of third trade
        third_trade_result = self.single_trade_result_constant_product(
            second_trade_result, p3.tkn0.amt, p3.tkn1.amt, p3.fee
        )

        trades = [
            tokens_in,
            first_trade_result,
            second_trade_result,
            third_trade_result,
        ]
        return trades

    def calculate_max_arb_cp_uni3_cp(
        self,
        p1t0a: Decimal,
        p1t1a: Decimal,
        p1fee: Decimal,
        p2l: Decimal,
        p2sqrt_price_xq96: Decimal,
        p2t0decimal: Decimal,
        p2t1decimal: Decimal,
        p2fee: Decimal,
        p3t0a: Decimal,
        p3t1a: Decimal,
        p3fee: Decimal,
        is_swapping_token0: bool,
    ):
        return (
            self.calculate_max_arb_constant_product_uni_v3_token0_in(
                p1t0a,
                p1t1a,
                p1fee,
                p2l,
                p2sqrt_price_xq96,
                p2t0decimal,
                p2t1decimal,
                p2fee,
                p3t0a,
                p3t1a,
                p3fee,
            )
            if is_swapping_token0
            else self.calculate_max_arb_constant_product_uni_v3_token1_in(
                p1t0a,
                p1t1a,
                p1fee,
                p2l,
                p2sqrt_price_xq96,
                p2t0decimal,
                p2t1decimal,
                p2fee,
                p3t0a,
                p3t1a,
                p3fee,
            )
        )

    @staticmethod
    def calculate_max_arb_constant_product_uni_v3_token1_in(
        p1t0a: Decimal,
        p1t1a: Decimal,
        p1fee: Decimal,
        p2l: Decimal,
        p2sqrt_price_xq96: Decimal,
        p2t0decimal: Decimal,
        p2t1decimal: Decimal,
        p2fee: Decimal,
        p3t0a: Decimal,
        p3t1a: Decimal,
        p3fee: Decimal,
    ):
        """This returns the optimal amount to trade into the set of pools when the input going into the Uniswap pool is its Token0"""
        p1fee, p3fee = Decimal(str(p1fee)), Decimal(str(p3fee))
        p2fee = Decimal(str(int(p2fee) / 1000000))
        return Decimal(
            p2sqrt_price_xq96
            * p2l
            * (
                -p3t0a * p1t0a * p2sqrt_price_xq96 * p2t0decimal
                + ec.Q96
                * Decimal.sqrt(
                    p3t0a
                    * p1t0a
                    * p3t1a
                    * p1t1a
                    * p2t0decimal
                    * p2t1decimal
                    * (
                        -p2fee * p3fee * p1fee
                        + p2fee * p3fee
                        + p2fee * p1fee
                        - p2fee
                        + p3fee * p1fee
                        - p3fee
                        - p1fee
                        + 1
                    )
                )
            )
            / (
                p3t0a * p2sqrt_price_xq96**2 * p2l * p2t0decimal
                + p3t0a
                * p2sqrt_price_xq96
                * p1t1a
                * p2fee
                * p1fee
                * ec.Q96
                * p2t0decimal
                * p2t1decimal
                - p3t0a
                * p2sqrt_price_xq96
                * p1t1a
                * p2fee
                * ec.Q96
                * p2t0decimal
                * p2t1decimal
                - p3t0a
                * p2sqrt_price_xq96
                * p1t1a
                * p1fee
                * ec.Q96
                * p2t0decimal
                * p2t1decimal
                + p3t0a * p2sqrt_price_xq96 * p1t1a * ec.Q96 * p2t0decimal * p2t1decimal
                + p1t1a * p2l * p2fee * p1fee * ec.Q96**2 * p2t1decimal
                - p1t1a * p2l * p2fee * ec.Q96**2 * p2t1decimal
                - p1t1a * p2l * p1fee * ec.Q96**2 * p2t1decimal
                + p1t1a * p2l * ec.Q96**2 * p2t1decimal
            )
        )

    @staticmethod
    def calculate_max_arb_constant_product_uni_v3_token0_in(
        p1t0a: Decimal,
        p1t1a: Decimal,
        p1fee: Decimal,
        p2l: Decimal,
        p2sqrt_price_xq96: Decimal,
        p2t0decimal: Decimal,
        p2t1decimal: Decimal,
        p2fee: Decimal,
        p3t0a: Decimal,
        p3t1a: Decimal,
        p3fee: Decimal,
    ):
        """This returns the optimal amount to trade into the set of pools when the input going into the Uniswap pool is its Token1"""
        p1fee, p3fee = Decimal(str(p1fee)), Decimal(str(p3fee))
        p2fee = Decimal(str(int(p2fee) / 1000000))
        return Decimal(
            (
                p2l
                * ec.Q96
                * (
                    -p3t0a * p1t0a * ec.Q96 * p2t1decimal
                    + p2sqrt_price_xq96
                    * Decimal.sqrt(
                        p3t0a
                        * p1t0a
                        * p3t1a
                        * p1t1a
                        * p2t0decimal
                        * p2t1decimal
                        * (
                            -p2fee * p3fee * p1fee
                            + p2fee * p3fee
                            + p2fee * p1fee
                            - p2fee
                            + p3fee * p1fee
                            - p3fee
                            - p1fee
                            + 1
                        )
                    )
                )
            )
            / (
                p3t0a
                * p2sqrt_price_xq96
                * p1t1a
                * p2fee
                * p1fee
                * ec.Q96
                * p2t0decimal
                * p2t1decimal
                - p3t0a
                * p2sqrt_price_xq96
                * p1t1a
                * p2fee
                * ec.Q96
                * p2t0decimal
                * p2t1decimal
                - p3t0a
                * p2sqrt_price_xq96
                * p1t1a
                * p1fee
                * ec.Q96
                * p2t0decimal
                * p2t1decimal
                + p3t0a * p2sqrt_price_xq96 * p1t1a * ec.Q96 * p2t0decimal * p2t1decimal
                + p3t0a * p2l * ec.Q96**2 * p2t1decimal
                + p2sqrt_price_xq96**2 * p1t1a * p2l * p2fee * p1fee * p2t0decimal
                - p2sqrt_price_xq96**2 * p1t1a * p2l * p2fee * p2t0decimal
                - p2sqrt_price_xq96**2 * p1t1a * p2l * p1fee * p2t0decimal
                + p2sqrt_price_xq96**2 * p1t1a * p2l * p2t0decimal
            )
        )

    @staticmethod
    def single_trade_result_constant_product(
        tokens_in, token0_amt, token1_amt, pool_fee
    ) -> Decimal:
        """This function returns the output of a trade (-Dy) given Dx in a constant product pool"""
        return Decimal(
            (tokens_in * token1_amt * (1 - Decimal(pool_fee)))
            / (tokens_in + token0_amt)
        )

    @staticmethod
    def get_in_given_out_constant_product(
        tokens_out, token0_amt, token1_amt, pool_fee
    ) -> Decimal:
        """This function returns the input of a trade (Dx) given -Dy in a constant product pool"""
        return Decimal(
            abs(
                (tokens_out * token0_amt)
                / (-tokens_out + pool_fee * token1_amt - token1_amt)
            )
        )

    @staticmethod
    def get_new_tkn_values_given_out_constant_product(
        tkns_out: Decimal, tkn0_amt: Decimal, tkn1_amt: Decimal
    ) -> Tuple[Decimal, Decimal]:
        pool_k = tkn0_amt * tkn1_amt
        new_tkn1_amt = tkn1_amt - tkns_out
        new_tkn0_amt = pool_k / new_tkn1_amt
        return new_tkn0_amt, new_tkn1_amt

    def get_liquidity_pool_after_trade_constant_product(
        self, tokens_in, liquidity_pool: LiquidityPool, is_forwards: bool
    ) -> LiquidityPool:
        """This function calculates the state of a liquidity pool after a trade"""
        trade_output = (
            self.single_trade_result_constant_product(
                tokens_in,
                liquidity_pool.tkn0.amt,
                liquidity_pool.tkn1.amt,
                liquidity_pool.fee,
            )
            if is_forwards
            else self.single_trade_result_constant_product(
                tokens_in,
                liquidity_pool.tkn1.amt,
                liquidity_pool.tkn0.amt,
                liquidity_pool.fee,
            )
        )

        new_token1_balance = (
            liquidity_pool.tkn1.amt - trade_output
            if is_forwards
            else liquidity_pool.tkn1.amt + tokens_in
        )
        new_token0_balance = (
            liquidity_pool.tkn0.amt + tokens_in
            if is_forwards
            else liquidity_pool.tkn0.amt - trade_output
        )

        liquidity_pool.tkn0.amt = new_token0_balance
        liquidity_pool.tkn1.amt = new_token1_balance

        return LiquidityPool(
            init_liquidity=False,
            exchange="bancor_v3",
            tkn0=liquidity_pool.tkn0,
            tkn1=liquidity_pool.tkn1,
            address=liquidity_pool.address,
            fee=liquidity_pool.fee,
        )

    def tick_to_sqrt_price_times_q96(self, next_starting_tick) -> Decimal:
        """This function converts a tick to a sqrt price times Q96"""
        return self.route.p2.tick_to_sqrt_price_q96(next_starting_tick)

    def calculate_max_swap_token0(
        self, next_sqrt_p, param, next_liquidity, t0decimal_mod, t1decimal_mod
    ):
        """
        This function calculates the maximum amount of token0 that can be swapped in a Uniswap pool
        """
        return self.route.p2.calculate_max_swap_token0(
            next_sqrt_p, param, next_liquidity, t0decimal_mod, t1decimal_mod
        )

    def calculate_max_swap_token1(
        self, next_sqrt_p, param, next_liquidity, t0decimal_mod, t1decimal_mod
    ):
        """
        This function calculates the maximum amount of token1 that can be swapped in a Uniswap pool
        """
        return self.route.p2.calculate_max_swap_token1(
            next_sqrt_p, param, next_liquidity, t0decimal_mod, t1decimal_mod
        )

    def best_route_univ3(
        self,
        route: Any,
    ) -> Any:
        """
        It first checks: p1 -> p2 -> p3
            If this returns a positive trade, it then checks the output of the first constant_product trade, then checks if that number of tokens vs the maximum input for the Uniswap V3 position before crossing ticks.
            If the swap will result in crossing tick boundaries, it will call recalculatePoolsForCrossTickTrades to recursively recalculate the maximum possible arbitrage.
        If the first set is not positive, it then checks p3 -> p2 -> p1, and repeats the process
        """
        from fastlane_bot.routes import Route

        best_route: Route = None
        is_tkn0 = (
            swap_bancor_eth_to_weth(route.p1.tkn1.address) == route.p2.tkn0.address
        )
        route0 = route.copy_route()
        route1 = route.copy_route()

        route0 = (
            route0 if is_tkn0 else route0.reverse_route(skip_idx=1).assert_bnt_order()
        )
        p1_r0, p2_r0, p3_r0 = route0.p1, route0.p2, route0.p3

        p1t0a: Decimal = Decimal(p1_r0.tkn0.amt)
        p1t1a: Decimal = Decimal(p1_r0.tkn1.amt)
        p1fee: Decimal = Decimal(p1_r0.fee)
        p2l: Decimal = Decimal(p2_r0.liquidity)
        p2sqrt_price_xq96: Decimal = Decimal(p2_r0.sqrt_price_q96)
        p2t0decimal: Decimal = Decimal(p2_r0.t0decimal_mod)
        p2t1decimal: Decimal = Decimal(p2_r0.t1decimal_mod)
        p2fee: Decimal = Decimal(p2_r0.fee)
        p3t0a: Decimal = Decimal(p3_r0.tkn0.amt)
        p3t1a: Decimal = Decimal(p3_r0.tkn1.amt)
        p3fee: Decimal = Decimal(p3_r0.fee)

        max_arb_trade_token0_in = (
            self.calculate_max_arb_constant_product_uni_v3_token0_in(
                p1t0a,
                p1t1a,
                p1fee,
                p2l,
                p2sqrt_price_xq96,
                p2t0decimal,
                p2t1decimal,
                p2fee,
                p3t0a,
                p3t1a,
                p3fee,
            )
        )

        route1 = (
            route1.reverse_route(skip_idx=1).assert_bnt_order() if is_tkn0 else route1
        )
        p1_r1, p2_r1, p3_r1 = route.p1, route.p2, route.p3

        p1t0a: Decimal = Decimal(p1_r1.tkn0.amt)
        p1t1a: Decimal = Decimal(p1_r1.tkn1.amt)
        p1fee: Decimal = Decimal(p1_r1.fee)
        p2l: Decimal = Decimal(p2_r1.liquidity)
        p2sqrt_price_xq96: Decimal = Decimal(p2_r1.sqrt_price_q96)
        p2t0decimal: Decimal = Decimal(p2_r1.t0decimal_mod)
        p2t1decimal: Decimal = Decimal(p2_r1.t1decimal_mod)
        p2fee: Decimal = Decimal(p2_r1.fee)
        p3t0a: Decimal = Decimal(p3_r1.tkn0.amt)
        p3t1a: Decimal = Decimal(p3_r1.tkn1.amt)
        p3fee: Decimal = Decimal(p3_r1.fee)

        max_arb_trade_token1_in = (
            self.calculate_max_arb_constant_product_uni_v3_token1_in(
                p1t0a,
                p1t1a,
                p1fee,
                p2l,
                p2sqrt_price_xq96,
                p2t0decimal,
                p2t1decimal,
                p2fee,
                p3t0a,
                p3t1a,
                p3fee,
            )
        )

        best_route = (
            route0 if max_arb_trade_token0_in > max_arb_trade_token1_in else route1
        )

        max_arb_trade = max(max_arb_trade_token0_in, max_arb_trade_token1_in)
        if max_arb_trade < 0:
            return None
        tkn0_in = (
            swap_bancor_eth_to_weth(best_route.p1.tkn1.address)
            == best_route.p2.tkn0.address
        )
        max_arb_trade = self.cross_tick_adjusted_arb(
            route=best_route, max_arb_trade=max_arb_trade, tkn0_in=tkn0_in
        )

        trade_results = self.calc_trade_result(
            max_arb_trade, best_route.p1, best_route.p2, best_route.p3
        )
        best_route.trade_path_amts = trade_results
        best_route.print()
        return best_route

    def cross_tick_adjusted_arb(
        self, route: Any, max_arb_trade: Decimal, tkn0_in: bool
    ):
        """
        Adjusts the max_arb_trade to account for the fact that the first trade may not be able to
        """
        result_first_trade = self.single_trade_result_constant_product(
            max_arb_trade,
            route.p1.tkn0.amt,
            route.p1.tkn1.amt,
            Decimal(route.p1.fee),
        )
        max_in = (
            route.p2.max_in_swap_token_0 if tkn0_in else route.p2.max_in_swap_token_1
        )
        max_out = (
            route.p2.max_out_swap_token_0 if tkn0_in else route.p2.max_out_swap_token_1
        )
        if result_first_trade > max_in:
            max_arb_trade = self.recalculate_pools_for_cross_tick_trades(
                max_arb_trade,
                route.p1,
                route.p2,
                route.p2.liquidity,
                route.p2.lower_tick if tkn0_in else route.p2.upper_tick,
                route.p3,
                max_in,
                max_out,
                0,
            )
        return max_arb_trade


# *******************************************************************************************
# RouteSolver - Carbon V1 Solver TODO: Add Carbon V1 Solver Logic
# *******************************************************************************************


@dataclass
class CarbonV1RouteSolver(BaseRouteSolver):
    """
    This class is used to solve the arbitrage for Carbon V1 routes

    ******************************* NOTE ****************************************
    See all method param definitions in the Route passed in via the :param route.
    *****************************************************************************
    """

    route: Any = (
        None  # Any is used to avoid circular imports. (should be `OrderBookDexRoute`)
    )

    def __post_init__(self):
        from fastlane_bot.routes import OrderBookDexRoute

        # Set the route type to the correct type for type hinting
        self.route: OrderBookDexRoute = self.route

    def simulate(self, trade_path: List[LiquidityPool] = None) -> Dict[str, Any]:
        """
        Takes 3 liquidity pools with token balances already populated as args, the first and last being Bancor V3 pools,
        and calculates potential arbitrage
        """
        route: Any = (
            self.route
        )  # Any is used to avoid circular imports. (`ConstantFunctionRoute` or `ConstantFunctionRoute`)
        p1: LiquidityPool = route.p1
        p2: LiquidityPool = route.p2
        p3: LiquidityPool = route.p3

        key: str = f"{p1.tkn0.symbol}_{p1.tkn1.symbol}->{p2.tkn0.symbol}_{p2.tkn1.symbol}->{p3.tkn0.symbol}_{p3.tkn1.symbol}"
        logger.debug(f"key1: {key}")

        if (
            p1 is None
            or p3 is None
            or p1.tkn0.amt == 0
            or p1.tkn1.amt == 0
            or p3.tkn0.amt == 0
            or p3.tkn1.amt == 0
        ):
            logger.debug("One of the pools was 'None'")
            return {"key": key, "results": 0}

        results = self.carbon_specific_methods()
        return {"key": key, "results": results}

    def carbon_specific_methods(self):
        """
        This method is used to add any Carbon specific methods that are needed for the solver

        TODO: Add Carbon V1 Solver Logic here
        """
        pass
