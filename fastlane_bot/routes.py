"""
Class objects for trade routes.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import copy
import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from decimal import *
from typing import List, Any, Dict

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import (
    InvalidTokenIndexException,
    InvalidPoolIndexException,
    InvalidRouteTypeException,
    TradePathSequenceException,
)
from fastlane_bot.pools import (
    ConstantProductLiquidityPool,
    UniswapV3LiquidityPool,
    LiquidityPool,
    BancorV2LiquidityPool,
    OrderBookDexLiquidityPool,
)
from fastlane_bot.solvers import (
    ConstantProductRouteSolver,
    CarbonV1RouteSolver,
    UniswapV3RouteSolver,
)
from fastlane_bot.utils import convert_weth_to_eth_symbol

# *******************************************************************************************
# Base Route
# *******************************************************************************************
logger = ec.DEFAULT_LOGGER


@dataclass
class BaseRoute:
    """
    Base class for all trade routes. A trade route is a sequence of trade_path that a trade can take.
    """

    id: int = None

    # The route solver to use for this route. This is (should be) set in the constructor of the child class.
    solver: ConstantProductRouteSolver or UniswapV3RouteSolver = (
        None  # Any is used here to avoid circular imports.
    )

    # The maximum length of the route trade_path.
    MAX_ROUTE_LENGTH: int = None
    BANCOR_BASE: str = ec.BANCOR_BASE

    # The trade path of the route consttains the pools (LiquidityPool's) that the trade will take.
    trade_path: List[LiquidityPool] = field(default_factory=list)

    # The trade path amounts contains the amounts to trade for each pool in the trade path.
    trade_path_amts: List[Decimal] = field(default_factory=list)

    # The ordered index keeps tracks of the order of the trade path relative to the original trade path.
    # This is used to reverse and reset the `trade_path` and `trade_path_amounts`.
    ordered_idx: List[int] = field(default_factory=list)

    # The logger to use for this route.
    logger: logging.Logger = None

    @abstractmethod
    def assert_logical_path(self):
        pass

    @abstractmethod
    def assert_bnt_order(self):
        """
        Corrects the order of BNT in the trade path if necessary.
        """
        pass

    @property
    def block_number(self):
        return self.trade_path[0].block_number

    @property
    def trade_path_name(self):
        """
        Returns the name of the trade path as (token0, token1, token2, ...)
        """
        return [pool.pair for pool in self.trade_path]

    @abstractmethod
    def simulate(self, trade_path: List[LiquidityPool] = None) -> Dict[str, Any]:
        """
        Main trade function for routes
        """
        pass

    @property
    def profit(self) -> Decimal:
        """
        Get the profit of the route.
        """
        try:
            return self.trade_path_amts[-1] - self.trade_path_amts[0]
        except IndexError:
            return Decimal(0)

    @property
    def p1(self):
        """the first pool in the trade path"""
        return self.trade_path[0]

    @p1.setter
    def p1(self, value):
        self.trade_path[0] = value

    @property
    def p2(self):
        """the second pool in the trade path"""
        return self.trade_path[1]

    @p2.setter
    def p2(self, value):
        self.trade_path[1] = value

    @property
    def p3(self):
        """the third pool in the trade path"""
        return self.trade_path[2]

    @p3.setter
    def p3(self, value):
        self.trade_path[2] = value

    def print(self):
        """
        Prints the route.
        """
        if not self.p2.contract_initialized:
            raise ValueError("Pool 2 is not initialized")
        logger.info(
            f"Route id: {self.id} \n"
            f"{self.p1.tkn0.symbol}:{self.p1.tkn0.amt} -> {self.p1.tkn1.symbol}{self.p1.tkn1.amt} \n"
            f"{self.p2.tkn0.symbol}_{self.p2.tkn1.symbol} => Liquidity -> {self.p2.liquidity} \n"
            f"{self.p3.tkn0.symbol}:{self.p3.tkn0.amt} -> {self.p3.tkn1.symbol}{self.p3.tkn1.amt} \n"
            f"Profit: {self.profit} \n"
            f"Trade path amounts: {self.trade_path_amts} \n"
        )

    def to_trade_struct(
        self, idx: int, min_target_amount: Decimal, deadline: int, web3, max_slippage
    ) -> Dict[str, Any]:
        """
        Returns the transaction dict for the route.
        """
        from fastlane_bot.utils import convert_decimals_to_wei_format

        target_token = self.trade_path[idx].tkn1

        if target_token.is_weth():
            target_token = target_token.to_eth()
        else:
            target_token = target_token.address

        target_token = web3.toChecksumAddress(target_token)
        min_expected = convert_decimals_to_wei_format(
            min_target_amount
            * (Decimal("100") - Decimal(max_slippage))
            / Decimal("100"),
            self.trade_path[idx].tkn1.decimals,
        )

        exchange_id = self.trade_path[idx].exchange_id

        return {
            "exchangeId": exchange_id,
            "targetToken": target_token,
            "minTargetAmount": min_expected,
            "deadline": deadline,
            "customAddress": web3.toChecksumAddress(
                self.trade_path[idx].anchor
                if isinstance(self.trade_path[idx], BancorV2LiquidityPool)
                else self.trade_path[idx].tkn1.address
            ),
            "customInt": int(self.trade_path[idx].fee)
            if isinstance(self.trade_path[idx], UniswapV3LiquidityPool)
            else 0,
            "customData": "",
        }

    def validate_pool_idx(self, idx: int):
        """
        Validate that the pool index is within the range of the Route.trade_path.
        """
        assert 0 <= idx < len(self.trade_path), InvalidPoolIndexException(
            idx, len(self.trade_path)
        )

    def reverse_route(self, skip_idx: int = -1):
        """
        Reverse the order of the trade_path for p1 and p3 and flip the order tokens for p2.
        """
        trade_path_rev = []
        for i, p in enumerate(list(reversed(self.trade_path))):
            if i != skip_idx:
                tkn0, tkn1 = p.tkn1, p.tkn0
                p.tkn0, p.tkn1 = tkn0, tkn1
            trade_path_rev.append(p)
        self.trade_path = trade_path_rev
        return self

    def _extracted_from_reverse_route(self, arg0, arg1):
        logger.debug(
            f"{arg0}{[(p.tkn0.symbol, p.tkn1.symbol) for p in self.trade_path]}"
        )
        logger.debug(
            f"{arg0}{[(str(p.tkn0.amt), str(p.tkn1.amt)) for p in self.trade_path]}"
        )
        logger.debug(
            f"{arg1}{self.p1.tkn0.symbol}, p1tkn0.amt: {str(self.p1.tkn0.amt)}, \np1tkn1: {self.p1.tkn1.symbol}, p1tkn1.amt: {str(self.p1.tkn1.amt)}, \np2tkn0: {self.p2.tkn0.symbol}, p1tkn0.amt: {str(self.p2.tkn0.amt)}, \np2tkn1: {self.p2.tkn1.symbol}, p2tkn1.amt: {str(self.p2.tkn1.amt)}, \np3tkn0: {self.p3.tkn0.symbol}, p3tkn0.amt: {str(self.p3.tkn0.amt)}, \np3tkn1: {self.p3.tkn1.symbol}, p3tkn1.amt: {str(self.p3.tkn1.amt)}, \n"
        )

    def copy_route(self):
        """
        Copy the route.
        """
        return copy.deepcopy(self)

    def validate(self):
        """
        Validate the route.
        """

        # Raised when the trade path specified is not of a supported type.

        try:
            assert self.trade_path[0].exchange == self.BANCOR_BASE
        except Exception as e:
            raise InvalidRouteTypeException(self.BANCOR_BASE) from e

        try:
            assert self.trade_path[-1].exchange == self.BANCOR_BASE
        except Exception as e:
            raise TradePathSequenceException(
                tkn0=self.trade_path[0].tkn1, tkn1=self.trade_path[-1].tkn1, idx=0
            ) from e

        try:
            assert self.trade_path[0].tkn1 == self.trade_path[-1].tkn1
        except Exception as e:
            raise TradePathSequenceException(
                tkn0=self.trade_path[0].tkn1, tkn1=self.trade_path[-1].tkn1, idx=0
            ) from e

        for i in range(len(self.trade_path) - 1):
            tkn0 = self.trade_path[i + 1].tkn0
            tkn1 = self.trade_path[i].tkn1

            # Raised when the tkn1 of PoolA does not match tkn0 of PoolB (the next pool in the path).
            try:
                assert tkn1.symbol == tkn0.symbol
            except Exception as e:
                raise TradePathSequenceException(
                    tkn0=tkn0.symbol, tkn1=tkn1.symbol, idx=i
                ) from e

        return True

    @staticmethod
    def validate_token_idx(idx: int):
        """
        Validate that the token index is 0 or 1.
        """
        assert idx in {0, 1}, InvalidTokenIndexException(idx)


# **********************************************************************************************************************
# Route - Constant Product Route
# **********************************************************************************************************************


@dataclass
class ConstantProductRoute(BaseRoute):
    """
    Represents a constant product trade route.
    """

    def assert_logical_path(self):
        """
        Asserts that the logical path is correct.
        """
        if self.p1.tkn0.symbol != "BNT":
            self.p1.reverse_tokens()
        if self.p3.tkn1.symbol != "BNT":
            self.p3.reverse_tokens()
        if convert_weth_to_eth_symbol(
            self.p2.tkn0.symbol
        ) != convert_weth_to_eth_symbol(self.p1.tkn1.symbol) and not isinstance(
            self, ConstantFunctionRoute
        ):
            self.p2.reverse_tokens()
        return self

    def assert_bnt_order(self):
        """
        Corrects the order of BNT in the trade path if necessary.
        """
        if self.p1.tkn1.is_bnt():
            self.p1.reverse_tokens()
        if self.p3.tkn0.is_bnt():
            self.p3.reverse_tokens()
        return self

    def simulate(
        self, trade_path: List[LiquidityPool or ConstantProductLiquidityPool] = None
    ) -> Dict[str, Any]:
        """
        Main trade function for routes
        """
        return self.solver.simulate(trade_path=trade_path)


# **********************************************************************************************************************
# Route - Constant Function Route (e.g. Uniswap v3)
# **********************************************************************************************************************


@dataclass
class ConstantFunctionRoute(BaseRoute):
    """
    Represents a constant function trade route.
    """

    def assert_logical_path(self):
        """
        Asserts that the logical path is correct.
        """
        if self.p1.tkn0.symbol != "BNT":
            self.p1.reverse_tokens()
        if self.p3.tkn1.symbol != "BNT":
            self.p3.reverse_tokens()
        return self

    def assert_bnt_order(self):
        """
        Corrects the order of BNT in the trade path if necessary.
        """
        if self.p1.tkn1.is_bnt():
            self.p1.reverse_tokens()
        if self.p3.tkn0.is_bnt():
            self.p3.reverse_tokens()
        return self

    def simulate(self, trade_path: List[LiquidityPool] = None):
        """
        Simulate the trade for route
        """
        self.trade_path = trade_path
        self.solver.route = self
        return self.solver.simulate(trade_path=trade_path)

    def correct_sqrt_q96_bounds(self):
        """
        Correct the sqrt_q96 bounds for the given pool.
        """
        lower_bound = self.pool_from_index(1).sqrt_price_lower_bound_x96
        upper_bound = self.pool_from_index(1).sqrt_price_upper_bound_x96
        if lower_bound > upper_bound:
            (
                self.pool_from_index(1).sqrt_price_lower_bound_x96,
                self.pool_from_index(1).sqrt_price_upper_bound_x96,
            ) = (
                upper_bound,
                lower_bound,
            )

    def max_tick_from_index(self, p_idx: int) -> int:
        """
        Get the maximum tick of the pool at index p_idx.
        """
        self.validate_pool_idx(p_idx)
        if not isinstance(self.trade_path[p_idx], UniswapV3LiquidityPool):
            self.logger.warning("Pool must be UniswapV3LiquidityPool, returning 0")
            return 0
        return self.trade_path[p_idx].max_tick

    def min_tick_from_index(self, p_idx: int) -> int:
        """
        Get the minimum tick of the pool at index p_idx.
        """
        self.validate_pool_idx(p_idx)
        if not isinstance(self.trade_path[p_idx], UniswapV3LiquidityPool):
            self.logger.warning("Pool must be UniswapV3LiquidityPool, returning 0")
            return 0
        return self.trade_path[p_idx].min_tick


# **********************************************************************************************************************
# Route - Order Book DEX Route (e.g. Carbon V1)
# **********************************************************************************************************************


@dataclass
class OrderBookDexRoute(BaseRoute):
    """
    Represents a constant function trade route. (e.g. Carbon V1)
    """

    def simulate(self, trade_path: List[LiquidityPool] = None):
        """
        Simulate the trade for route
        """
        self.trade_path = trade_path
        self.solver.route = self
        self.solver.simulate(trade_path=trade_path)

    def other_carbon_specific_methods(self):
        """
        TODO: Add other Carbon specific methods as needed. Reuse utils.py methods where possible / general-use.
        """
        pass


@dataclass
class Route(BaseRoute, ABC):
    """Dynamic Route Type class.
    This class is used to auto-determine the route type and instantiate the correct route class.

    :param id (int): Route ID
    :param trade_path (List[LiquidityPool]): List of liquidity pools in the trade path
    """

    def __eq__(self, other) -> bool:
        assert isinstance(
            other, Route or ConstantProductRoute or ConstantFunctionRoute
        ), "Equality can only be evaluated against another Erc20Token"
        return (
            (self.id == other.id)
            & all(
                p1.tkn0.symbol == p2.tkn0.symbol
                for p1, p2 in zip(self.trade_path, other.trade_path)
            )
            & all(
                p1.tkn1.symbol == p2.tkn1.symbol
                for p1, p2 in zip(self.trade_path, other.trade_path)
            )
            & all(
                p1.tkn0.amt == p2.tkn0.amt
                for p1, p2 in zip(self.trade_path, other.trade_path)
            )
            & all(
                p1.tkn1.amt == p2.tkn1.amt
                for p1, p2 in zip(self.trade_path, other.trade_path)
            )
        )

    def __post_init__(self):
        cls = self.__class__
        if isinstance(self.trade_path[1], UniswapV3LiquidityPool):
            # Assign the correct route type if Uniswap V3 is detected
            cls = ConstantFunctionRoute(
                id=self.id,
                trade_path=self.trade_path,
                solver=UniswapV3RouteSolver(route=self),
            )
        elif isinstance(self.trade_path[1], OrderBookDexLiquidityPool):
            # Assign the correct route type if Carbon V1 is detected
            cls = OrderBookDexRoute(
                id=self.id,
                trade_path=self.trade_path,
                solver=CarbonV1RouteSolver(route=self),
            )
        else:
            # Default to ConstantProductRoute if no other route type is detected
            cls = ConstantProductRoute(
                id=self.id,
                trade_path=self.trade_path,
                solver=ConstantProductRouteSolver(route=self),
            )

        # reassign the exchange-specific class attributes to the generic Route class
        self.__class__ = cls.__class__
        for k, v in cls.__dict__.items():
            self.__dict__[k] = v
        return self
