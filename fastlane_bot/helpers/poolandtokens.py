"""
Defines the ``PoolAndTokens`` class, representing a pool and its tokens in a single object. This is not a database model, but a helper class.

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
__VERSION__ = "1.2"
__DATE__ = "05/May/2023"

import decimal
import math
from _decimal import Decimal
from dataclasses import dataclass
from typing import Dict, Any, List, Union

from fastlane_bot.config import Config

# from fastlane_bot.config import SUPPORTED_EXCHANGES, CARBON_V1_NAME, UNISWAP_V3_NAME
from fastlane_bot.helpers.univ3calc import Univ3Calculator
from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.utils import EncodedOrder


class SolidlyV2StablePoolsNotSupported(Exception):
    pass

FEE_LOOKUP = {
        0.000001: Univ3Calculator.FEE1,
        0.000008: Univ3Calculator.FEE8,
        0.00001: Univ3Calculator.FEE10,
        0.00004: Univ3Calculator.FEE40,
        0.00008: Univ3Calculator.FEE80,
        0.0001: Univ3Calculator.FEE100,
        0.00025: Univ3Calculator.FEE250,
        0.0003: Univ3Calculator.FEE300,
        0.00045: Univ3Calculator.FEE450,
        0.0005: Univ3Calculator.FEE500,
        0.0010: Univ3Calculator.FEE1000,
        0.0025: Univ3Calculator.FEE2500,
        0.0030: Univ3Calculator.FEE3000,
        0.01: Univ3Calculator.FEE10000,
    }

@dataclass
class PoolAndTokens:
    """
    Represents a pool and its tokens in a single object. This is not a database model, but a helper class.

    Parameters
    ----------
    id : int
        The id of the pool
    cid : str
        The cid of the pool
    last_updated : str
        The last time the pool was updated
    last_updated_block : int
        The last block the pool was updated
    descr : str
        The description of the pool
    pair_name : str
        The name of the pool
    exchange_name : str
        The name of the exchange
    fee : Decimal
        The fee of the pool
    tkn0_balance : Decimal
        The balance of token 0
    tkn1_balance : Decimal
        The balance of token 1
    z_0 : Decimal
        The z_0 value
    y_0 : Decimal
        The y_0 value
    A_0 : Decimal
        The A_0 value
    B_0 : Decimal
        The B_0 value
    z_1 : Decimal
        The z_1 value
    y_1 : Decimal
        The y_1 value
    A_1 : Decimal
        The A_1 value
    B_1 : Decimal
        The B_1 value
    sqrt_price_q96 : Decimal
        The sqrt_price_q96 value
    tick : int
        The tick value
    tick_spacing : int
        The tick spacing value
    liquidity : Decimal
        The liquidity value
    address : str
        The address of the pool
    anchor : str
        The anchor of the pool
    tkn0 : str
        The token 0 key
    tkn1 : str
        The token 1 key
    tkn0_address : str
        The address of token 0
    tkn0_decimals : int
        The decimals of token 0
    tkn1_address : str
        The address of token 1
    tkn1_decimals : int
        The decimals of token 1

    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    ConfigObj: Config
    id: int
    cid: str
    strategy_id: int
    last_updated: str
    last_updated_block: int
    descr: str
    pair_name: str
    exchange_name: str
    fee: Decimal
    fee_float: float
    tkn0_balance: Decimal
    tkn1_balance: Decimal
    z_0: Decimal
    y_0: Decimal
    A_0: Decimal
    B_0: Decimal
    z_1: Decimal
    y_1: Decimal
    A_1: Decimal
    B_1: Decimal
    sqrt_price_q96: Decimal
    tick: int
    tick_spacing: int
    liquidity: Decimal
    address: str
    anchor: str
    tkn0: str
    tkn1: str
    tkn0_address: str
    tkn0_decimals: int
    tkn1_address: str
    tkn1_decimals: int
    router: str = None
    tkn0_weight: float = None
    tkn1_weight: float = None
    tkn2: str = None
    tkn2_balance: Decimal = None
    tkn2_address: str = None
    tkn2_decimals: int = None
    tkn2_weight: float = None
    tkn3: str = None
    tkn3_balance: Decimal = None
    tkn3_address: str = None
    tkn3_decimals: int = None
    tkn3_weight: float = None
    tkn4: str = None
    tkn4_balance: Decimal = None
    tkn4_address: str = None
    tkn4_decimals: int = None
    tkn4_weight: float = None
    tkn5: str = None
    tkn5_balance: Decimal = None
    tkn5_address: str = None
    tkn5_decimals: int = None
    tkn5_weight: float = None
    tkn6: str = None
    tkn6_balance: Decimal = None
    tkn6_address: str = None
    tkn6_decimals: int = None
    tkn6_weight: float = None
    tkn7: str = None
    tkn7_balance: Decimal = None
    tkn7_address: str = None
    tkn7_decimals: int = None
    tkn7_weight: float = None

    tkn0_symbol: str = None
    tkn1_symbol: str = None
    tkn2_symbol: str = None
    tkn3_symbol: str = None
    tkn4_symbol: str = None
    tkn5_symbol: str = None
    tkn6_symbol: str = None
    tkn7_symbol: str = None
    ADDRDEC = None

    pool_type: str = None


    def __post_init__(self):

        self.A_1 = self.A_1 or 0
        self.B_1 = self.B_1 or 0
        self.A_0 = self.A_0 or 0
        self.B_0 = self.B_0 or 0
        self.z_0 = self.z_0 or 0
        self.y_0 = self.y_0 or 0
        self.z_1 = self.z_1 or 0
        self.y_1 = self.y_1 or 0

        self.tokens = (
            self.get_tokens
        )
        self.token_weights = self.remove_nan(
            [
                self.tkn0_weight,
                self.tkn1_weight,
                self.tkn2_weight,
                self.tkn3_weight,
                self.tkn4_weight,
                self.tkn5_weight,
                self.tkn6_weight,
                self.tkn7_weight,
            ]
        )
        self.token_balances = self.remove_nan(
            [
                self.tkn0_balance,
                self.tkn1_balance,
                self.tkn2_balance,
                self.tkn3_balance,
                self.tkn4_balance,
                self.tkn5_balance,
                self.tkn6_balance,
                self.tkn7_balance,
            ]
        )
        self.token_decimals = self.remove_nan(
            [
                self.tkn0_decimals,
                self.tkn1_decimals,
                self.tkn2_decimals,
                self.tkn3_decimals,
                self.tkn4_decimals,
                self.tkn5_decimals,
                self.tkn6_decimals,
                self.tkn7_decimals,
            ]
        )

    @property
    def get_tokens(self):
        """
        returns all tokens in a curve
        """
        tokens = [
            self.tkn0_address,
            self.tkn1_address,
            self.tkn2_address,
            self.tkn3_address,
            self.tkn4_address,
            self.tkn5_address,
            self.tkn6_address,
            self.tkn7_address,
        ]
        tokens = [tkn for tkn in tokens if type(tkn) == str]
        return [tkn for tkn in tokens if tkn is not None]

    @property
    def get_token_addresses(self):
        """
        returns all tokens in a curve
        """
        tokens = [self.tkn0_address, self.tkn1_address, self.tkn2_address, self.tkn3_address, self.tkn4_address, self.tkn5_address,
                  self.tkn6_address, self.tkn7_address]
        tokens = [tkn for tkn in tokens if type(tkn) == str]
        return [tkn for tkn in tokens if tkn is not None]

    def to_cpc(self) -> Union[ConstantProductCurve, List[Any]]:
        """
        converts self into an instance of the ConstantProductCurve class.
        """

        self.fee = float(Decimal(str(self.fee)))
        if self.exchange_name in self.ConfigObj.UNI_V3_FORKS:
            out = self._univ3_to_cpc()
        elif self.exchange_name in [
            self.ConfigObj.BANCOR_POL_NAME,
        ] + self.ConfigObj.CARBON_V1_FORKS:
            out = self._carbon_to_cpc()
        elif self.exchange_name in self.ConfigObj.BALANCER_NAME:
            out = self._balancer_to_cpc()
        elif self.exchange_name in self.ConfigObj.SOLIDLY_V2_FORKS:
            if self.pool_type == "volatile":
                out = self._other_to_cpc()
            else:
                raise SolidlyV2StablePoolsNotSupported(f"exchange {self.exchange_name}")
        elif self.exchange_name in self.ConfigObj.SUPPORTED_EXCHANGES:
            out = self._other_to_cpc()
        else:
            raise NotImplementedError(f"exchange {self.exchange_name}")

        return out

    @property
    def _params(self):
        """
        creates the parameter dict for the ConstantProductCurve class
        """
        return {
            "exchange": str(self.exchange_name),
            "tknx_dec": int(self.tkn0_decimals),
            "tkny_dec": int(self.tkn1_decimals),
            "tknx_addr": str(self.tkn0_address),
            "tkny_addr": str(self.tkn1_address),
            "blocklud": int(self.last_updated_block),
        }

    def _balancer_to_cpc(self) -> List[Any]:
        """
        constructor: from Uniswap V2 pool (see class docstring for other parameters)

        :x_tknb:    current pool liquidity in token x (base token of the pair)*
        :y_tknq:    current pool liquidity in token y (quote token of the pair)*
        :k:         uniswap liquidity parameter (k = xy)*

        *exactly one of k,x,y must be None; all other parameters must not be None;
        a reminder that x is TKNB and y is TKNQ
        """

        typed_args_all = []

        for idx, tkn in enumerate(self.tokens):
            for _idx, _tkn in enumerate(self.tokens[idx:], start=idx):
                if _idx >= len(self.tokens) or tkn == _tkn:
                    continue

                # convert tkn0_balance and tkn1_balance to Decimal from wei
                tkn0_balance = self.convert_decimals(
                    self.token_balances[idx], self.token_decimals[idx]
                )
                tkn1_balance = self.convert_decimals(
                    self.token_balances[_idx], self.token_decimals[_idx]
                )
                weight0 = float(str(self.token_weights[idx]))
                weight1 = float(str(self.token_weights[_idx]))
                eta = weight0 / weight1
                _pair_name = tkn + "/" + _tkn
                # create a typed-dictionary of the arguments
                typed_args_all.append(
                    {
                        "x": tkn0_balance,
                        "y": tkn1_balance,
                        # "alpha": weight0,
                        "eta": eta,
                        "pair": _pair_name.replace(self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS),
                        "fee": self.fee,
                        "cid": self.cid,
                        "descr": self.descr,
                        "params": self._params,
                    }
                )
        return [
            ConstantProductCurve.from_xyal(**self._convert_to_float(typed_args))
            for typed_args in typed_args_all
        ]

    class DoubleInvalidCurveError(ValueError):
        pass

    def _other_to_cpc(self) -> List[Any]:
        """
        constructor: from Uniswap V2 pool (see class docstring for other parameters)

        :x_tknb:    current pool liquidity in token x (base token of the pair)*
        :y_tknq:    current pool liquidity in token y (quote token of the pair)*
        :k:         uniswap liquidity parameter (k = xy)*

        *exactly one of k,x,y must be None; all other parameters must not be None;
        a reminder that x is TKNB and y is TKNQ
        """

        # convert tkn0_balance and tkn1_balance to Decimal from wei
        tkn0_balance = self.convert_decimals(self.tkn0_balance, self.tkn0_decimals)
        tkn1_balance = self.convert_decimals(self.tkn1_balance, self.tkn1_decimals)

        # create a typed-dictionary of the arguments
        typed_args = {
            "x_tknb": tkn0_balance,
            "y_tknq": tkn1_balance,
            "pair": self.pair_name.replace(self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS),
            "fee": self.fee,
            "cid": self.cid,
            "descr": self.descr,
            "params": self._params,
        }
        return [ConstantProductCurve.from_univ2(**self._convert_to_float(typed_args))]

    class DoubleInvalidCurveError(ValueError):
        pass

    def _carbon_to_cpc(self) -> ConstantProductCurve:
        """
        constructor: from a single Carbon order (see class docstring for other parameters)*

        :yint:      current pool y-intercept**
        :y:         current pool liquidity in token y
        :pa:        fastlane_bot price range left bound (higher price in dy/dx)
        :pb:        fastlane_bot price range right bound (lower price in dy/dx)
        :A:         alternative to pa, pb: A = sqrt(pa) - sqrt(pb) in dy/dy
        :B:         alternative to pa, pb: B = sqrt(pb) in dy/dy
        :tkny:      token y
        :isdydx:    if True prices in dy/dx, if False in quote direction of the pair

        *Note that ALL parameters are mandatory, except that EITHER pa, bp OR A, B
        must be given but not both; we do not correct for incorrect assignment of
        pa and pb, so if pa <= pb IN THE DY/DX DIRECTION, MEANING THAT THE NUMBERS
        ENTERED MAY SHOW THE OPPOSITE RELATIONSHIP, then an exception will be raised

        **note that the result does not depend on yint, and for the time being we
        allow to omit yint (in which case it is set to y, but this does not make
        a difference for the result)
        """
        def calculate_parameters(y: Decimal, pa: Decimal, pb: Decimal, pm: Decimal, n: Decimal):
            H = pa.sqrt() ** n
            L = pb.sqrt() ** n
            M = pm.sqrt() ** n
            A = H - L
            B = L
            z = y * (H - L) / (M - L) if M > L else y
            return z
        
        def check_overlap(pa0, pb0, pa1, pb1):
            min0, max0 = sorted([pa0, pb0]) 
            min1, max1 = sorted([1 / pa1, 1 / pb1]) 
            prices_overlap = max(min0, min1) < min(max0, max1)
            return prices_overlap 

        # if idx == 0, use the first curve, otherwise use the second curve. change the numerical values to Decimal
        lst = []
        errors = []
        strategy_typed_args = []
        for i in [0, 1]:

            S = Decimal(self.A_1) if i == 0 else Decimal(self.A_0)
            B = Decimal(self.B_1) if i == 0 else Decimal(self.B_0)
            try:
                if B <= 0:
                    continue
            except decimal.InvalidOperation:
                continue
            y = Decimal(self.y_1) if i == 0 else Decimal(self.y_0)
            z = yint = Decimal(self.z_1) if i == 0 else Decimal(self.z_0)
            try:
                if y <= Decimal("0"):
                    continue
            except decimal.InvalidOperation:
                # print(
                #     f"decimal.InvalidOperation attributes: {self.exchange_name}, {self.pair_name}, {self.cid}, y={y}, y_0={self.y_0}, y_1={self.y_1}, skipping..."
                # )
                continue
            encoded_order = EncodedOrder(
                **{
                    "token": self.pair_name.split("/")[i].replace(
                        self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
                    ),
                    "A": S,
                    "B": B,
                    "y": y,
                    "z": z,
                }
            )

            def decimal_converter(idx):
                if idx == 0:
                    dec0 = self.tkn0_decimals
                    dec1 = self.tkn1_decimals
                else:
                    dec0 = self.tkn1_decimals
                    dec1 = self.tkn0_decimals
                return Decimal(str(10 ** (dec0 - dec1)))

            decimal_converter = decimal_converter(i)

            p_start = Decimal(encoded_order.p_start) * decimal_converter
            p_marg = Decimal(encoded_order.p_marg) * decimal_converter
            p_end = Decimal(encoded_order.p_end) * decimal_converter
            yint = Decimal(yint) / (
                Decimal("10") ** [self.tkn1_decimals, self.tkn0_decimals][i]
            )
            y = Decimal(y) / (
                Decimal("10") ** [self.tkn1_decimals, self.tkn0_decimals][i]
            )
            is_limit_order = p_start==p_end

            tkny = 1 if i == 0 else 0
            typed_args = {
                "cid": f"{self.cid}-{i}"
                if self.exchange_name in self.ConfigObj.CARBON_V1_FORKS
                else self.cid,
                "yint": yint,
                "y": y,
                "pb": p_end,
                "p_marg": p_marg,  # deleted later since not supported by from_carbon()
                "pa": p_start,
                "is_limit_order": is_limit_order, # deleted later since not supported by from_carbon()
                "tkny": self.pair_name.split("/")[tkny].replace(
                    self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
                ),
                "pair": self.pair_name.replace(self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS),
                "params": {"exchange": self.exchange_name},
                "fee": self.fee,
                "descr": self.descr,
                "params": self._params,
            }

            strategy_typed_args += [typed_args]

        # Only overlapping strategies are selected for modification
        if len(strategy_typed_args) == 2:
            
            is_overlapping = False
            pmarg_threshold = Decimal("0.01") # 1%  # WARNING using this condition alone can included stable/stable pairs incidently

            # evaluate that the marginal prices are within the pmarg_threshold
            pmarg0, pmarg1 = [x['p_marg'] for x in strategy_typed_args]
            pmarg0_inv = 1/pmarg0  # one of the orders must be flipped since prices are always dy/dx - but must flip same geomean_pmarg later
            percent_component = pmarg_threshold * max(pmarg0_inv, pmarg1)
            percent_component_met = abs(pmarg0_inv - pmarg1) <= percent_component

            # overlapping strategies by defintion cannot have A=0 i.e. there must be no limit orders
            no_limit_orders = (strategy_typed_args[0]['is_limit_order'] == False) and (strategy_typed_args[1]['is_limit_order'] == False)

            # evaluate if the price boundaries pa/pb overlap at one end # TODO check logic and remove duplicate logic if necessary
            prices_overlap = check_overlap(strategy_typed_args[0]['pa'], strategy_typed_args[0]['pb'], strategy_typed_args[1]['pa'], strategy_typed_args[1]['pb'])

            # Prevents stable-stable strategies from being modified
            not_little_fee = strategy_typed_args[0]['fee'] > 10

            # if the threshold is met and neither is a limit order and prices overlap then likely to be overlapping
            is_overlapping = percent_component_met and no_limit_orders and prices_overlap and not_little_fee

            if is_overlapping:
                # calculate the geometric mean
                geomean_p_marg = Decimal.sqrt(pmarg0_inv * pmarg1)
                
                # modify the y_int based on the new geomean to the limit of y    #TODO check that this math is correct
                typed_args0 = strategy_typed_args[0]
                new_yint0 = calculate_parameters(y=typed_args0['y'], pa=typed_args0['pa'], pb=typed_args0['pb'], pm=(1/geomean_p_marg), n=1)
                if new_yint0 < typed_args0['y']:
                    new_yint0 = typed_args0['y']
                typed_args0['yint'] = new_yint0

                typed_args1 = strategy_typed_args[1]
                new_yint1 = calculate_parameters(y=typed_args1['y'], pa=typed_args1['pa'], pb=typed_args1['pb'], pm=(geomean_p_marg), n=1)
                if new_yint1 < typed_args1['y']:
                    new_yint1 = typed_args1['y']
                typed_args1['yint'] = new_yint1

                # repack the strateg_typed_args
                strategy_typed_args = [typed_args0, typed_args1]

        for typed_args in strategy_typed_args:
            # delete new args that arent supported by from_carbon()
            del typed_args["p_marg"]
            del typed_args["is_limit_order"]
            try:
                if typed_args["y"] > 0:
                    lst.append(
                        ConstantProductCurve.from_carbon(
                            **self._convert_to_float(typed_args)
                        )
                    )
                # else:
                #     self.ConfigObj.logger.debug(f"empty carbon pool [{typed_args['cid']}]")
            except Exception as e:
                errmsg = f"[_carbon_to_cpc] error in curve {i} [probably empty: {typed_args}] - [{e}]\n"
                self.ConfigObj.logger.debug(errmsg)
                errors += [errmsg]

        return lst



    def _univ3_to_cpc(self) -> List[Any]:
        """
        Preprocesses a Uniswap V3 pool params in order to create a ConstantProductCurve instance for optimization.

        :return: ConstantProductCurve
            :k:        pool constant k = xy [x=k/y, y=k/x]
            :x:        (virtual) pool state x (virtual number of base tokens for sale)
            :x_act:    actual pool state x (actual number of base tokens for sale)
            :y_act:    actual pool state y (actual number of quote tokens for sale)
            :pair:     tkn_address pair in slash notation ("TKNB/TKNQ"); TKNB is on the x-axis, TKNQ on the y-axis
            :cid:      unique id (optional)
            :fee:      fee (optional); eg 0.01 for 1%
            :descr:    description (optional; eg. "UniV3 0.1%")
            :params:   additional parameters (optional)

        """
        args = {
            "token0": self.tkn0_address,
            "token1": self.tkn1_address,
            "sqrt_price_q96": self.sqrt_price_q96,
            "tick": self.tick,
            "liquidity": self.liquidity,
        }
        feeconst = FEE_LOOKUP.get(float(self.fee_float))
        if feeconst is None:
            raise ValueError(
                f"Illegal fee for Uniswap v3 pool: {self.fee_float} [{FEE_LOOKUP}]]"
            )
        uni3 = Univ3Calculator.from_dict(args, feeconst, addrdec=self.ADDRDEC)
        params = uni3.cpc_params()
        # print("u3params", params)
        if params["uniL"] == 0:
            self.ConfigObj.logger.debug(f"empty univ3 pool [{self.cid}]")
            return []
        params["cid"] = self.cid
        params["descr"] = self.descr
        params["params"] = self._params
        return [ConstantProductCurve.from_univ3(**params)]

    @staticmethod
    def convert_decimals(tkn_balance_wei: Decimal, tkn_decimals: int) -> Decimal:
        """
        Converts wei balance to token balance (returns a Decimal)
        """
        # TODO: why Decimal?!?
        return Decimal(
            str(
                Decimal(str(tkn_balance_wei))
                / (Decimal("10") ** Decimal(str(tkn_decimals)))
            )
        )

    @staticmethod
    def _convert_to_float(typed_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        converts Decimal to float
        """
        convert = lambda x: float(x) if isinstance(x, Decimal) else x
        return {k: convert(v) for k, v in typed_args.items()}
        # MIKE: this code converted the dict in place AND returned it;
        # that may work but is ugly...
        # for key, value in typed_args.items():
        #     if isinstance(value, (Decimal, float)):
        #         typed_args[key] = float(value)
        # return typed_args

    def get_token_weight(self, tkn):
        """
        :param tkn: the token key

        This function returns the weight of a token in a Balancer pool.

        """
        idx = self._get_token_index(tkn=tkn)
        return self.token_weights[idx]

    def get_token_balance(self, tkn):
        """
        :param tkn: the token key

        This function returns the balance of a token in a Balancer pool.
        """
        idx = self._get_token_index(tkn=tkn)
        return self.token_balances[idx]

    def get_token_decimals(self, tkn):
        """
        :param tkn: the token key

        This function returns the balance of a token in a Balancer pool.
        """
        idx = self._get_token_index(tkn=tkn)
        return self.token_decimals[idx]

    def _get_token_index(self, tkn):
        """
        :param tkn: the token key

        This function returns the index of a token within the pool.

        """

        for idx, token in enumerate(self.tokens):
            if tkn == token:
                return idx

    @staticmethod
    def remove_nan(item_list: List) -> List:
        """
        Removes empty items from a list.
        :param item_list: List

        Returns: List
        """
        return [item for item in item_list if item is not None and not math.isnan(item)]
