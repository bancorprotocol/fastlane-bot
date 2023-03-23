"""
Class objects for AMM liquidity pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import math
import warnings
from abc import abstractmethod
from dataclasses import dataclass, field
from decimal import *
from typing import Tuple, List, Any

import pandas as pd

from fastlane_bot.exceptions import (
    InvalidPoolInitialization,
    InvalidExchangeException,
)
from fastlane_bot.networks import *
from fastlane_bot.token import ERC20Token
from fastlane_bot.utils import (
    get_abi_and_router,
    convert_decimals,
)

logger = ec.DEFAULT_LOGGER

contracts = {}


# *******************************************************************************************
# Base Pool
# *******************************************************************************************


@dataclass
class BaseLiquidityPool:
    """
    Represents a pool.
    """

    block_number: int = None
    pair: str = None
    pair_reverse: str = None
    init_liquidity: bool = True
    init_setup: bool = True
    contract_initialized: bool = False

    # expected fields for all pools
    address: str = None
    liquidity: Decimal = None
    fee: str or Decimal = None
    exchange: str = None
    exchange_id: int = None
    tokens: List[ERC20Token] = field(default_factory=list)
    liquidity_tokens: List[ERC20Token] = field(default_factory=list)
    id: int = None
    connection: Any = None

    def handle_eth_to_weth(self):
        """
        Convert ETH to WETH if necessary.
        """
        if self.tkn0.is_eth():
            self.tkn0 = self.tkn0.convert_to_weth()
        if self.tkn1.is_eth():
            self.tkn1 = self.tkn1.convert_to_weth()

    @property
    def contract(self):
        """
        Get the contract for the pool.
        """
        if not self.contract_initialized:
            contract = Contract.from_abi(
                name=f"{self.address}",
                address=f"{self.address}",
                abi=get_abi_and_router(self.exchange)[0],
            )
            contracts[self.id] = contract
        else:
            contract = contracts[self.id]
        return contract

    def get_tkn_state(self):
        """
        Returns the token state.
        """
        is_reversed = False
        if self.is_reversed:
            is_reversed = True
            tkn0, tkn1 = self.tkn1, self.tkn0
        else:
            tkn0, tkn1 = self.tkn0, self.tkn1
        return is_reversed, tkn0, tkn1

    def assert_valid_tkn_order(self):
        """
        Asserts that the order of the tokens is correct.
        """
        pair = f"{self.tkn0.symbol}_{self.tkn1.symbol}"
        if ec.DB[(ec.DB["pair"] == pair) & (ec.DB["exchange"] == self.exchange)].empty:
            warnings.warn(
                f"Pair {pair} not found in the database. Please add the pair to the database if it is valid. Reversing order of the tokens.",
            )
            self.reverse_tokens()
            self.tkn0._is_tkn0 = True
            self.tkn1._is_tkn0 = False

    @property
    def is_reversed(self):
        """
        Returns True if the order of the tokens is reversed (relative to the update_liquidity function expected token order,
        which is equal to the pair name tkn order).
        """
        return self.pair in [
            f"{self.tkn1.symbol}_{self.tkn0.symbol}",
            f"{self.tkn1.symbol}_{self.tkn0.symbol}_{self.fee}",
        ]

    @property
    def invalid_pair(self):
        """
        Tests if the pair is invalid.
        """
        return self.pair in [
            f"{self.tkn1.symbol}_{self.tkn0.symbol}",
            f"{self.tkn1.symbol}_{self.tkn0.symbol}_{self.fee}",
            f"{self.tkn0.symbol}_{self.tkn1.symbol}",
            f"{self.tkn0.symbol}_{self.tkn1.symbol}_{self.fee}",
        ]

    @property
    def tkn0(self):
        """
        Returns the first token in the pair.
        """
        return self.tokens[0]

    @tkn0.setter
    def tkn0(self, value):
        self.tokens[0] = value

    @property
    def tkn1(self):
        """
        Returns the second token in the pair.
        """
        return self.tokens[1]

    @tkn1.setter
    def tkn1(self, value):
        self.tokens[1] = value

    @abstractmethod
    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """
        pass

    @property
    def base_pair(self) -> str:
        """
        :return: the base pair name
        """
        return f"{self.tkn0.symbol}_{self.tkn1.symbol}"

    def reverse_tokens(self):
        """
        Reverse the order of the tokens in the pool.
        """
        tkn0 = self.tkn0
        tkn1 = self.tkn1
        self.tkn0 = tkn1
        self.tkn1 = tkn0
        return self

    def validate_pool(self):
        """
        Validate the pool.
        """
        self._setup_tokens()
        assert (
            self.exchange in ec.SUPPORTED_EXCHANGE_VERSIONS
        ), InvalidPoolInitialization(
            address=self.address,
            pair=self.pair,
            exchange=self.exchange,
            fee=self.fee,
            tkn0=self.tkn0,
            tkn1=self.tkn1,
        )
        assert self.tkn0.symbol != self.tkn1.symbol, InvalidPoolInitialization(
            address=self.address,
            pair=self.pair,
            exchange=self.exchange,
            fee=self.fee,
            tkn0=self.tkn0,
            tkn1=self.tkn1,
        )
        assert self.tkn0.address != self.tkn1.address, InvalidPoolInitialization(
            address=self.address,
            pair=self.pair,
            exchange=self.exchange,
            fee=self.fee,
            tkn0=self.tkn0,
            tkn1=self.tkn1,
        )

    def correct_decimals(self):
        """
        Correct the decimals of the tokens in the pool.
        """
        # convert the amount to the correct decimal
        self.tkn0.amt = convert_decimals(self.tkn0.amt, n=self.tkn0.decimals)
        self.tkn1.amt = convert_decimals(self.tkn1.amt, n=self.tkn1.decimals)

    def handle_tkn_set_order(self, is_reversed, tkn0, tkn1):
        """
        Handle resetting the order of the tokens in the pool after liquidity is updated.
        """

        self.block_number = self.connection.eth.block_number
        if is_reversed:
            self.tkn1 = tkn0
            self.tkn0 = tkn1
        else:
            self.tkn0 = tkn0
            self.tkn1 = tkn1
        self.correct_decimals()
        return self

    def setup(self):
        """
        Set the constants for the pool.
        """

        if self.address is not None:
            try:
                assert self.address in ec.DB["address"].values
            except Exception as e:
                raise InvalidPoolInitialization(
                    address=self.address,
                ) from e

        self._setup_tokens()

        if self.exchange in [
            ec.UNISWAP_V3_NAME,
            ec.UNISWAP_V2_NAME,
            ec.SUSHISWAP_V2_NAME,
        ]:
            if self.tkn0.is_eth():
                self.tkn0 = self.tkn0.convert_to_weth()
            if self.tkn1.is_eth():
                self.tkn1 = self.tkn1.convert_to_weth()

        _ABI, _POOL_INFO_FOR_EXCHANGE = get_abi_and_router(self.exchange)

        if self.pair is not None and _POOL_INFO_FOR_EXCHANGE is not None:
            if "WETH" in self.pair and self.exchange == ec.BANCOR_V2_NAME:
                self.pair = self.pair.replace("WETH", "ETH")
            if (
                self.pair in _POOL_INFO_FOR_EXCHANGE["pair"].unique()
                or self.pair in _POOL_INFO_FOR_EXCHANGE["pair_reverse"].unique()
            ):
                self._set_pool_attributes(_POOL_INFO_FOR_EXCHANGE)
            else:
                logger.error(
                    f"Pool {self.pair} not found in pool info for exchange {self.exchange}"
                )
                raise InvalidPoolInitialization(
                    address=self.address,
                    pair=self.pair,
                    exchange=self.exchange,
                    fee=self.fee,
                    tkn0=self.tkn0,
                    tkn1=self.tkn1,
                )

        tkn0, tkn1 = self.tkn0, self.tkn1

        pair = (
            f"{tkn0.symbol}_{tkn1.symbol}"
            if self.exchange != ec.UNISWAP_V3_NAME
            else f"{tkn0.symbol}_{tkn1.symbol}_{self.fee}"
        )
        if pair in _POOL_INFO_FOR_EXCHANGE["pair"].unique():
            # set the token order
            tkn0._is_tkn0 = True
            tkn1._is_tkn0 = False
        else:
            # set the token order
            tkn0._is_tkn0 = False
            tkn1._is_tkn0 = True
        self.tokens = [tkn0, tkn1]
        return self

    def _setup_tokens(self):
        if isinstance(self.tkn0, str):
            try:
                self.tkn0 = ERC20Token(symbol=self.tkn0)
            except Exception as e:
                logger.error(f"Token {self.tkn0} not found {e}")
                raise InvalidPoolInitialization(
                    address=self.address,
                    pair=self.pair,
                    exchange=self.exchange,
                    fee=self.fee,
                    tkn0=self.tkn0,
                    tkn1=self.tkn1,
                ) from e
        if isinstance(self.tkn1, str):
            try:
                self.tkn1 = ERC20Token(symbol=self.tkn1)
            except Exception as e:
                logger.error(f"Token {self.tkn1} not found {e}")
                raise InvalidPoolInitialization(
                    address=self.address,
                    pair=self.pair,
                    exchange=self.exchange,
                    fee=self.fee,
                    tkn0=self.tkn0,
                    tkn1=self.tkn1,
                ) from e

    def _set_pool_attributes(self, POOL_INFO_FOR_EXCHANGE):
        # Get the pool info subset
        subset = POOL_INFO_FOR_EXCHANGE[POOL_INFO_FOR_EXCHANGE["pair"] == self.pair]
        reverse_amts = False
        if len(subset) == 0:
            # If the pool is not found, try reversing the pair
            subset = POOL_INFO_FOR_EXCHANGE[
                POOL_INFO_FOR_EXCHANGE["pair_reverse"] == self.pair
            ]
            if self.exchange == ec.BANCOR_V2_NAME:
                reverse_amts = True

        if len(subset) == 0:
            # If the pool is still not found, raise an error
            raise InvalidPoolInitialization(
                address=self.address,
                pair=self.pair,
                exchange=self.exchange,
                fee=self.fee,
                tkn0=self.tkn0,
                tkn1=self.tkn1,
            )

        # Set the attributes for the pool object from the subset
        self.address = subset["address"].values[0]
        self.fee = subset["fee"].values[0]

        # validate address
        self.address = Web3.toChecksumAddress(self.address)

        # If the pool is a Bancor V2 pool, set the anchor address
        if self.exchange == ec.BANCOR_V2_NAME:
            self.anchor = subset["anchor"].values[0]
            self.anchor = Web3.toChecksumAddress(self.anchor)

        self.validate_pool()

    def to_pandas(
        self, idx: int = 0, amt_in: Decimal = None, amt_out: Decimal = None
    ) -> pd.DataFrame:
        """
        Exports values for inspection...
        """

        dic = {
            f"{idx}_id": self.id,
            f"{idx}_exchange": self.exchange,
            f"{idx}_pair_name": self.pair,
            f"{idx}_tkn0_amt": str(self.tkn0.amt),
            f"{idx}_tkn1_amt": str(self.tkn1.amt),
            f"{idx}_tkn0_symbol": self.tkn0.symbol,
            f"{idx}_tkn1_symbol": self.tkn1.symbol,
            f"{idx}_fee": self.fee,
            f"{idx}_liquidity": str(self.liquidity),
            f"{idx}_amt_in": str(amt_in),
            f"{idx}_amt_out": str(amt_out),
            f"{idx}_sqrt_price_q96": str(self.sqrt_price_q96) if idx == 1 else None,
        }
        return pd.DataFrame(dic, index=[0])


@dataclass
class ConstantProductLiquidityPool(BaseLiquidityPool, ABC):
    """
    Represents a constant product liquidity pool. Used for typechecking via inheritance.
    """


# *******************************************************************************************
# Uniswap V2 Pool
# *******************************************************************************************


@dataclass
class UniswapV2LiquidityPool(ConstantProductLiquidityPool):
    """
    Represents a Uniswap V2 liquidity pool.
    """

    exchange: str = ec.UNISWAP_V2_NAME
    exchange_id: int = ec.EXCHANGE_IDS[ec.UNISWAP_V2_NAME][0]

    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """
        self.handle_eth_to_weth()
        is_reversed, tkn0, tkn1 = self.get_tkn_state()
        self.liquidity = self.contract.getReserves()
        tkn0.amt, tkn1.amt = self.liquidity[0], self.liquidity[1]
        self.contract_initialized = True
        return self.handle_tkn_set_order(is_reversed, tkn0, tkn1)

    def __post_init__(self):
        if self.init_setup:
            self.setup()


# *******************************************************************************************
# Bancor V2 Pool
# *******************************************************************************************


@dataclass
class BancorV2LiquidityPool(ConstantProductLiquidityPool):
    """
    Represents a Bancor V2 liquidity pool.
    """

    exchange: str = ec.BANCOR_V2_NAME
    exchange_id: int = ec.EXCHANGE_IDS[ec.BANCOR_V2_NAME][0]

    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """

        is_reversed, tkn0, tkn1 = self.get_tkn_state()
        tkn0.amt, tkn1.amt = self.contract.reserveBalances()
        self.liquidity = tkn0.amt * tkn1.amt
        self.contract_initialized = True
        return self.handle_tkn_set_order(is_reversed, tkn0, tkn1)

    def __post_init__(self):
        if self.init_setup:
            self.setup()


# *******************************************************************************************
# Bancor V3 Pool
# *******************************************************************************************


@dataclass
class BancorV3LiquidityPool(ConstantProductLiquidityPool):
    """
    Represents a Bancor V3 liquidity pool.
    """

    exchange: str = ec.BANCOR_V3_NAME
    exchange_id: int = ec.EXCHANGE_IDS[ec.BANCOR_V3_NAME][0]

    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """

        if tkn0 is not None and tkn1 is not None and contract is not None:
            self.tkn0 = tkn0
            self.tkn1 = tkn1

        is_reversed, tkn0, tkn1 = self.get_tkn_state()
        tkn0.amt, tkn1.amt = contract.tradingLiquidity(tkn1.address)
        self.contract_initialized = True
        return self.handle_tkn_set_order(is_reversed, tkn0, tkn1)

    def __post_init__(self):
        if self.init_setup:
            self.setup()


# *******************************************************************************************
# SuhsiSwap Pool
# *******************************************************************************************


@dataclass
class SushiswapLiquidityPool(ConstantProductLiquidityPool):
    """
    Represents a Sushiswap liquidity pool.
    """

    exchange: str = ec.SUSHISWAP_V2_NAME
    exchange_id: int = ec.EXCHANGE_IDS[ec.SUSHISWAP_V2_NAME][0]

    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """
        self.handle_eth_to_weth()
        is_reversed, tkn0, tkn1 = self.get_tkn_state()
        self.liquidity = self.contract.getReserves()
        tkn0.amt, tkn1.amt = self.liquidity[0], self.liquidity[1]
        return self.handle_tkn_set_order(is_reversed, tkn0, tkn1)

    def __post_init__(self):
        if self.init_setup:
            self.setup()


# *******************************************************************************************
# Uniswap V3 Pool
# *******************************************************************************************


@dataclass
class UniswapV3LiquidityPool(BaseLiquidityPool):
    """
    Represents a Uniswap V3 pool.
    """

    exchange: str = ec.UNISWAP_V3_NAME
    exchange_id: int = ec.EXCHANGE_IDS[ec.UNISWAP_V3_NAME][0]

    # UNI V3 specific fields
    sqrt_price_q96: Decimal = None
    tick: int = None
    nxt_sqrt_price_q96: Decimal = None
    slot0: Tuple[int, int, int, int, int, int] = None

    _max_in_swap_token_0: Decimal = None
    _max_in_swap_token_1: Decimal = None
    _max_out_swap_token_0: Decimal = None
    _max_out_swap_token_1: Decimal = None
    _sqrt_price_q96_upper_bound: Decimal = None
    _sqrt_price_q96_lower_bound: Decimal = None
    _max_swap_token1: Tuple[Decimal, Decimal] = None
    _max_swap_token0: Tuple[Decimal, Decimal] = None

    @property
    def t0decimal_mod(self) -> Decimal:
        """
        Returns the decimal modifier for token 0.
        """
        return Decimal(str(10**self.tkn0_decimal))

    @property
    def t1decimal_mod(self) -> Decimal:
        """
        Returns the decimal modifier for token 1.
        """
        return Decimal(str(10**self.tkn1_decimal))

    @property
    def tkn0_decimal(self):
        """
        Returns the token decimal to use when calculating modifier for token 0.
        """
        return self.tkn1.decimals if self.is_reversed else self.tkn0.decimals

    @property
    def tkn1_decimal(self):
        """
        Returns the token decimal to use when calculating modifier for token 1.
        """
        return self.tkn0.decimals if self.is_reversed else self.tkn1.decimals

    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """

        is_reversed = bool(self.is_reversed)
        slot0 = self.contract.slot0()
        self.tick = slot0[1]
        self.slot0 = slot0
        self.sqrt_price_q96 = slot0[0]
        self.liquidity = Decimal(self.contract.liquidity())
        self.block_number = self.connection.eth.block_number

        self.correct_decimals()

        if not self.contract_initialized:
            self.contract_initialized = True
            self.setup_properties()

        return self

    @staticmethod
    def fee_tier_to_tick_spacing(fee_tier: int):
        """Returns the tick spacing for the Uni V3 pool, i.e. pools that charge a 0.003 fee have tick ranges of 60 ticks"""
        return {100: 1, 500: 10, 3000: 60, 10000: 200}.get(fee_tier, 60)

    def tick_to_sqrt_price_q96(self, tick: Decimal) -> Decimal:
        """returns the price given a tick"""
        return (
            Decimal((ec.TICK_BASE ** Decimal((tick / Decimal("2")))) * ec.Q96)
            if self.contract_initialized
            else None
        )

    @property
    def tick_spacing(self) -> int:
        """
        Returns the tick spacing of the pool.
        """
        return self.fee_tier_to_tick_spacing(int(self.fee))

    @property
    def lower_tick(self) -> Decimal:
        """
        Returns the lower tick of the pool.
        """
        if self.contract_initialized:
            return Decimal(
                math.floor(self.tick / self.tick_spacing) * self.tick_spacing
            )
        else:
            return Decimal(0)

    @property
    def upper_tick(self) -> Decimal:
        """
        Returns the upper tick of the pool.
        """
        if self.contract_initialized:
            return Decimal(self.lower_tick + self.tick_spacing)
        else:
            return Decimal(0)

    @staticmethod
    def calc_amount0(
        liquidity: Decimal,
        sqrt_price_times_q96_lower_bound: Decimal,
        sqrt_price_times_q96_upper_bound: Decimal,
    ) -> Decimal:
        """returns the amount of token 0 - this is used to calculate amounts in the pool, and swap outputs"""
        if sqrt_price_times_q96_lower_bound > sqrt_price_times_q96_upper_bound:
            sqrt_price_times_q96_lower_bound, sqrt_price_times_q96_upper_bound = (
                sqrt_price_times_q96_upper_bound,
                sqrt_price_times_q96_lower_bound,
            )
        return Decimal(
            liquidity
            * ec.Q96
            * (sqrt_price_times_q96_upper_bound - sqrt_price_times_q96_lower_bound)
            / sqrt_price_times_q96_upper_bound
            / sqrt_price_times_q96_lower_bound
        )

    @staticmethod
    def calc_amount1(
        liquidity: Decimal,
        sqrt_price_times_q96_lower_bound: Decimal,
        sqrt_price_times_q96_upper_bound: Decimal,
    ) -> Decimal:
        """returns the amount of token 1 - this is used to calculate amounts in the pool, and swap outputs"""
        if sqrt_price_times_q96_lower_bound > sqrt_price_times_q96_upper_bound:
            sqrt_price_times_q96_lower_bound, sqrt_price_times_q96_upper_bound = (
                sqrt_price_times_q96_upper_bound,
                sqrt_price_times_q96_lower_bound,
            )
        return Decimal(
            liquidity
            * (sqrt_price_times_q96_upper_bound - sqrt_price_times_q96_lower_bound)
            / ec.Q96
        )

    def calculate_max_swap_token0(
        self,
        sqrt_price: Decimal,
        price_range_limit: Decimal,
        liquidity: Decimal,
        decimal0_modifier: Decimal,
        decimal1_modifier: Decimal,
    ) -> Tuple[Decimal, Decimal]:
        """Returns the max output when swapping token 0 to token 1 in the current price range"""
        amount_in_calc = self.calc_amount0(liquidity, price_range_limit, sqrt_price)
        amount_out_calc = self.calc_amount1(liquidity, price_range_limit, sqrt_price)

        max_in = Decimal(amount_in_calc / decimal0_modifier)
        max_out = Decimal(amount_out_calc / decimal1_modifier)
        self._max_swap_token0 = max_in, max_out
        return self._max_swap_token0

    def calculate_max_swap_token1(
        self,
        sqrt_price: Decimal,
        price_range_limit: Decimal,
        liquidity: Decimal,
        decimal0_modifier: Decimal,
        decimal1_modifier: Decimal,
    ) -> Tuple[Decimal, Decimal]:
        """Returns the max output when swapping token 1 to token 0 in the current price range"""
        amount_in_calc = self.calc_amount1(liquidity, price_range_limit, sqrt_price)
        amount_out_calc = self.calc_amount0(liquidity, price_range_limit, sqrt_price)
        max_in = Decimal(amount_in_calc / decimal1_modifier)
        max_out = Decimal(amount_out_calc / decimal0_modifier)
        self._max_swap_token1 = max_in, max_out
        return self._max_swap_token1

    @property
    def max_swap_token0(self) -> Tuple[Decimal, Decimal]:
        """
        Returns the max swap amount for token 0.
        """
        if not self.contract_initialized:
            return [None, None]

        return (
            self._max_swap_token0
            if self._max_swap_token0 is not None
            else self.calculate_max_swap_token0(
                self.sqrt_price_q96,
                self.sqrt_price_q96_lower_bound,
                self.liquidity,
                self.t0decimal_mod,
                self.t1decimal_mod,
            )
        )

    @property
    def max_in_swap_token_0(self) -> Decimal:
        """
        Returns the max swap amount for token 0.
        """
        return self._max_in_swap_token_0

    @max_in_swap_token_0.setter
    def max_in_swap_token_0(self, value: Decimal):
        self._max_in_swap_token_0 = value

    @property
    def max_out_swap_token_0(self) -> Decimal:
        """
        Returns the max swap amount for token 0.
        """
        return self._max_out_swap_token_0

    @max_out_swap_token_0.setter
    def max_out_swap_token_0(self, value: Decimal):
        self._max_out_swap_token_0 = value

    @property
    def max_swap_token1(self) -> Tuple[Decimal, Decimal]:
        """
        Returns the max swap amount for token 1.
        """
        if not self.contract_initialized:
            return [None, None]

        return (
            self._max_swap_token1
            if self._max_swap_token1 is not None
            else self.calculate_max_swap_token1(
                self.sqrt_price_q96,
                self.sqrt_price_q96_upper_bound,
                self.liquidity,
                self.t0decimal_mod,
                self.t1decimal_mod,
            )
        )

    @property
    def max_in_swap_token_1(self) -> Decimal:
        """
        Returns the max swap amount for token 1.
        """
        return self._max_in_swap_token_1

    @max_in_swap_token_1.setter
    def max_in_swap_token_1(self, value: Decimal):
        self._max_in_swap_token_1 = value

    @property
    def max_out_swap_token_1(self) -> Decimal:
        """
        Returns the max swap amount for token 1.
        """
        return self._max_out_swap_token_1

    @max_out_swap_token_1.setter
    def max_out_swap_token_1(self, value: Decimal):
        self._max_out_swap_token_1 = value

    @property
    def sqrt_price_q96_upper_bound(self) -> Decimal:
        """
        Returns the upper bound of the price range.
        """
        return (
            self._sqrt_price_q96_upper_bound
            if self._sqrt_price_q96_upper_bound is not None
            else self.tick_to_sqrt_price_q96(self.upper_tick)
        )

    @property
    def sqrt_price_q96_lower_bound(self) -> Decimal:
        """
        Returns the lower bound of the price range.
        """
        return (
            self._sqrt_price_q96_lower_bound
            if self._sqrt_price_q96_lower_bound is not None
            else self.tick_to_sqrt_price_q96(self.lower_tick)
        )

    def setup_properties(self):
        self._sqrt_price_q96_upper_bound = self.tick_to_sqrt_price_q96(self.upper_tick)
        self._sqrt_price_q96_lower_bound = self.tick_to_sqrt_price_q96(self.lower_tick)
        self._max_in_swap_token_0 = self.max_swap_token0[0]
        self._max_out_swap_token_0 = self.max_swap_token0[1]
        self._max_in_swap_token_1 = self.max_swap_token1[0]
        self._max_out_swap_token_1 = self.max_swap_token1[1]

    def __post_init__(self):
        if self.init_setup:
            self.setup()
            if self.contract_initialized:
                self.setup_properties()


# *******************************************************************************************
# Carbon Pool
# *******************************************************************************************


@dataclass
class OrderBookDexLiquidityPool(BaseLiquidityPool, ABC):
    """
    Represents an Order-Book-Like DEX (e.g. Carbon V1). Used for typechecking via inheritance.
    Meant to support deliniation of the different Carbon versions and/or copycat DEXs
    into the future.
    """


@dataclass
class CarbonV1LiquidityPool(OrderBookDexLiquidityPool):
    """
    Represents a Carbon V1 pool.
    """

    # optional fields (automatically populated if not provided)
    address: str = None
    liquidity: Decimal = None
    fee: str or Decimal = None
    contract: Contract = None
    exchange: str = ec.CARBON_V1_NAME
    exchange_id: int = ec.EXCHANGE_IDS[ec.CARBON_V1_NAME][0]

    # Carbon specific fields
    # ...
    # ...

    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """
        return self

    def __post_init__(self):
        self.setup()


# *******************************************************************************************
# Liquidity Pool
# *******************************************************************************************


@dataclass
class LiquidityPool(BaseLiquidityPool):
    """Dynamically assigns pool class types for all supported AMM Exchanges.
    This class is used to auto-determine the pool type and instantiate the correct pool class.

    # *********
    # ********* req'd fields
    # *********
    :param exchange (str): The exchange name (e.g. Uniswap V2)
    :param tkn0 (ERC20Token or str): The first token in the pool
    :param tkn1 (ERC20Token or str): The second token in the pool
    :param init_liquidity (bool): Whether the pool has been initialized with liquidity

    # *********
    # ********* optional fields (automatically populated if not provided) *********
    # *********
    :param address (str): The address of the pool
    :param liquidity (Decimal): The amount of liquidity in the pool
    :param fee (str or Decimal): The fee of the pool
    :param contract (Contract): The contract object of the pool
    :param block_number (int): The block number of the pool
    :param pair (str): The pair of the pool (e.g. "UNI-V2")

    # *********
    # ********* Uniswap V3 specific fields (optional)
    # *********
    :param sqrt_price_q96 (Decimal): The sqrt price of the pool
    :param tick (int): The tick of the pool
    :param nxt_sqrt_price_q96 (Decimal): The next sqrt price of the pool
    :param max_in_swap_token_0 (Decimal): The max in swap for token 0
    :param max_in_swap_token_1 (Decimal): The max in swap for token 1
    :param max_out_swap_token_0 (Decimal): The max out swap for token 0
    :param max_out_swap_token_1 (Decimal): The max out swap for token 1
    :param sqrt_price_q96_lower_bound (Decimal): The sqrt price lower bound of the pool
    :param sqrt_price_q96_upper_bound (Decimal): The sqrt price upper bound of the pool
    :param tick_spacing (int): The tick spacing of the pool
    :param lower_tick (int): The lower tick of the pool
    :param upper_tick (int): The upper tick of the pool
    """

    # required fields
    block_number: int = None
    connection: Any = None
    tkn0: ERC20Token or str = None
    tkn1: ERC20Token or str = None
    exchange: str = None
    fee: str or Decimal = None
    pair: str = None
    pair_reverse: str = None
    init_liquidity: bool = True
    liquidity: Decimal = None

    # UNI V3 specific fields
    sqrt_price_q96: Decimal = None
    tick: int = None
    nxt_sqrt_price_q96: Decimal = None
    max_in_swap_token_0: Decimal = None
    max_in_swap_token_1: Decimal = None
    max_out_swap_token_0: Decimal = None
    max_out_swap_token_1: Decimal = None
    sqrt_price_q96_lower_bound: Decimal = None
    sqrt_price_q96_upper_bound: Decimal = None
    tick_spacing: int = None
    lower_tick: Decimal = None
    upper_tick: Decimal = None
    t0decimal_mod: Decimal = None
    t1decimal_mod: Decimal = None

    id: int = None

    def update_liquidity(
        self,
        contract: Contract = None,
        tkn0: ERC20Token = None,
        tkn1: ERC20Token = None,
    ):
        """
        Update the liquidity of the pool.
        """
        pass

    def __post_init__(self):
        cls = self.__class__

        if self.pair is None and (self.tkn0 is None or self.tkn1 is None):
            raise InvalidPoolInitialization(
                pair=self.pair,
                tkn0=self.tkn0,
                tkn1=self.tkn1,
                exchange=self.exchange,
                fee=self.fee,
            )

        # Assign the correct class to the liquidity pool object based on the exchange
        if self.exchange == ec.UNISWAP_V2_NAME:
            cls = UniswapV2LiquidityPool(
                init_liquidity=self.init_liquidity,
                exchange=self.exchange,
                tokens=[self.tkn0, self.tkn1],
                fee=self.fee,
                block_number=self.block_number,
                pair=self.pair,
                pair_reverse=self.pair_reverse,
                liquidity=self.liquidity,
                id=self.id,
                connection=self.connection,
            )
        elif self.exchange == ec.UNISWAP_V3_NAME:
            cls = UniswapV3LiquidityPool(
                init_liquidity=self.init_liquidity,
                exchange=self.exchange,
                tokens=[self.tkn0, self.tkn1],
                fee=self.fee,
                block_number=self.block_number,
                pair=self.pair,
                pair_reverse=self.pair_reverse,
                sqrt_price_q96=self.sqrt_price_q96,
                tick=self.tick,
                nxt_sqrt_price_q96=self.nxt_sqrt_price_q96,
                liquidity=self.liquidity,
                id=self.id,
                connection=self.connection,
            )
        elif self.exchange == ec.SUSHISWAP_NAME:
            cls = SushiswapLiquidityPool(
                init_liquidity=self.init_liquidity,
                exchange=self.exchange,
                tokens=[self.tkn0, self.tkn1],
                fee=self.fee,
                block_number=self.block_number,
                pair=self.pair,
                pair_reverse=self.pair_reverse,
                liquidity=self.liquidity,
                id=self.id,
                connection=self.connection,
            )
        elif self.exchange == ec.BANCOR_V2_NAME:
            cls = BancorV2LiquidityPool(
                init_liquidity=self.init_liquidity,
                exchange=self.exchange,
                tokens=[self.tkn0, self.tkn1],
                fee=self.fee,
                block_number=self.block_number,
                pair=self.pair,
                pair_reverse=self.pair_reverse,
                liquidity=self.liquidity,
                id=self.id,
                connection=self.connection,
            )
        elif self.exchange == ec.BANCOR_V3_NAME:
            cls = BancorV3LiquidityPool(
                init_liquidity=self.init_liquidity,
                exchange=self.exchange,
                tokens=[self.tkn0, self.tkn1],
                fee=self.fee,
                block_number=self.block_number,
                pair=self.pair,
                pair_reverse=self.pair_reverse,
                liquidity=self.liquidity,
                id=self.id,
                connection=self.connection,
            )
        else:
            raise InvalidExchangeException(exchange=self.exchange)

        # if the token is not found, return None
        if not cls.tkn0:
            return None

        if not cls.tkn1:
            return None

        # reassign the exchange-specific class attributes to the generic LiquidityPool class
        self.__class__ = cls.__class__
        for k, v in cls.__dict__.items():
            self.__dict__[k] = v
        return self


ConstantFunctionLiquidityPool = UniswapV3LiquidityPool
