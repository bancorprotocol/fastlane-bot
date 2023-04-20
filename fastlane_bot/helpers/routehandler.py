"""
Route handler for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
# import itertools
# import random
# import time
from dataclasses import dataclass, asdict
from typing import List, Union, Any, Dict, Tuple, Optional
import eth_abi
import math
import pandas as pd

# import requests
from _decimal import Decimal
from alchemy import Network, Alchemy
from brownie.network.transaction import TransactionReceipt
from eth_utils import to_hex
from web3 import Web3
from web3._utils.threads import Timeout
from web3._utils.transactions import fill_nonce
from web3.contract import ContractFunction
from web3.exceptions import TimeExhausted
from web3.types import TxParams, TxReceipt

from fastlane_bot.abi import *  # TODO: PRECISE THE IMPORTS or from .. import abi
from fastlane_bot.config import *  # TODO: PRECISE THE IMPORTS or from .. import config
from fastlane_bot.models import Token, session, Pool
from fastlane_bot.tools.cpc import ConstantProductCurve

from .tradeinstruction import TradeInstruction


@dataclass
class RouteStruct:
    """
    A class that represents a single trade route in the format required by the arbitrage contract Route struct.

    Parameters
    ----------
    exchangeId: int
        The exchange ID. (0 = Bancor V2, 1 = Bancor V3, 2 = Uniswap V2, 3 = Uniswap V3, 4 = Sushiswap V2, 5 = Sushiswap, 6 = Carbon)
    targetToken: str
        The target token address.
    minTargetAmount: int
        The minimum target amount. (in wei)
    deadline: int
        The deadline for the trade.
    customAddress: str
        The custom address. Typically used for the Bancor V2 anchor address.
    customInt: int
        The custom integer. Typically used for the fee.
    _customData: dict
        The custom data. Required for trades on Carbon. (unencoded)
    customData: bytes
        The custom data abi-encoded. Required for trades on Carbon. (abi-encoded)
    """

    XCID_BANCOR_V2 = 0
    XCID_BANCOR_V3 = 1
    XCID_UNISWAP_V2 = 2
    XCID_UNISWAP_V3 = 3
    XCID_SUSHISWAP_V2 = 4
    XCID_SUSHISWAP_V1 = 5
    XCID_CARBON_V1 = 6

    exchangeId: int  # TODO: WHY IS THIS AN INT?
    targetToken: str
    minTargetAmount: int
    deadline: int
    customAddress: str
    customInt: int
    customData: bytes

@dataclass
class TxRouteHandlerBase:
    pass

@dataclass
class TxRouteHandler(TxRouteHandlerBase):
    """
    A class that handles the routing of the bot. Takes the `trade_instructions` and converts them into the variables needed to instantiate the `TxSubmitHandler` class.

    Parameters
    ----------
    trade_instructions_dic: List[Dict[str, Any]]
        The trade instructions. Formatted output from the `CPCOptimizer` class.
    trade_instructions_df: pd.DataFrame
        The trade instructions as a dataframe. Formatted output from the `CPCOptimizer` class.
    """

    trade_instructions_dic: List[TradeInstruction]
    trade_instructions_df: pd.DataFrame = None
    trade_instructions: List[ConstantProductCurve] = None

    @property
    def exchange_ids(self) -> List[int]:
        """
        Returns
        """
        return [trade.exchange_id for trade in self.trade_instructions]

    def __post_init__(self):
        self.contains_carbon = True
        self._validate_trade_instructions()

    def _validate_trade_instructions(self):
        """
        Validates the trade instructions.
        """
        if not self.trade_instructions_dic:
            raise ValueError("No trade instructions found.")
        if len(self.trade_instructions_dic) < 2:
            raise ValueError("Trade instructions must be greater than 1.")
        if len(self._get_carbon_indexes(self.trade_instructions_dic)) == 0:
            self.contains_carbon = False

    @staticmethod
    def _get_carbon_indexes(
        trade_instructions_dic: List[Dict[str, Any] or TradeInstruction]
    ) -> List[int]:
        """
        Gets the indexes of the trades that are on the Carbon exchange.

        Returns
        -------
        List[int]
            The indexes of the trades that are on the Carbon exchange.
        """
        if isinstance(trade_instructions_dic[0], TradeInstruction):
            return [
                idx
                for idx in range(len(trade_instructions_dic))
                if "-" in trade_instructions_dic[idx].cid
            ]
        return [
            idx
            for idx in range(len(trade_instructions_dic))
            if "-" in trade_instructions_dic[idx]["cid"]
        ]

    def is_weth(self, address: str) -> bool:
        """
        Checks if the address is WETH.

        Parameters
        ----------
        address: str
            The address.

        Returns
        -------
        bool
            Whether the address is WETH.
        """
        return address.lower() == WETH_ADDRESS.lower()

    @staticmethod
    def custom_data_encoder(
        wei_instructions: List[TradeInstruction],
    ) -> List[TradeInstruction]:
        for i in range(len(wei_instructions)):
            instr = wei_instructions[i]
            print("DETAILS", i, instr.amtin, instr.amtout)
            if instr.raw_txs == "[]":
                instr.customData = ""
                # instr.amtin =  int(instr.amtin * 0.9)
                wei_instructions[i] = instr
            else:
                tradeInfo = eval(instr.raw_txs)

                # convert strategyid to type int
                tradeActions = []
                for trade in tradeInfo:
                    tradeActions += [
                        {
                            "strategyId": int(trade["cid"].split("-")[0]),
                            "amount": int(
                                Decimal(trade["amtin"])
                                * 10**instr.tknin_decimals
                                * Decimal("0.99")
                            ),
                        }
                    ]

                # Define the types of the keys in the dictionaries
                types = ["uint256", "uint128"]

                # Extract the values from each dictionary and append them to a list
                values = [32, len(tradeActions)] + [
                    value
                    for data in tradeActions
                    for value in (data["strategyId"], data["amount"])
                ]

                # Create a list of ABI types based on the number of dictionaries
                all_types = ["uint32", "uint32"] + types * len(tradeActions)

                # Encode the extracted values using the ABI types
                encoded_data = eth_abi.encode(all_types, values)
                instr.customData = encoded_data
                wei_instructions[i] = instr

        # print(f"all_types: {all_types}")
        return wei_instructions

    def _abi_encode_data(
        self,
        idx_of_carbon_trades: List[int],
        trade_instructions: List[TradeInstruction],
    ) -> bytes:
        """
        Gets the custom data abi-encoded. Required for trades on Carbon. (abi-encoded)

        Parameters
        ----------
        idx_of_carbon_trades: List[int]
            The indices of the trades that are on Carbon.
        trade_instructions_dic: List[Dict[str, str]]
            The trade instructions dictionary.

        """
        trade_actions_dic = [
            {
                "strategyId": int(trade_instructions[idx].cid),
                "amount": math.floor(trade_instructions[idx].amtin_wei),
            }
            for idx in idx_of_carbon_trades
        ]

        types = ["uint256", "uint128"]
        values = [32, len(trade_actions_dic)] + [
            value
            for data in trade_actions_dic
            for value in (data["strategyId"], data["amount"])
        ]
        all_types = ["uint32", "uint32"] + types * len(trade_actions_dic)
        return eth_abi.encode(all_types, values)

    def to_route_struct(
        self,
        min_target_amount: Decimal,
        deadline: int,
        target_address: str,
        exchange_id: int,
        custom_address: str = None,
        fee: Any = None,
        customData: Any = None,
        override_min_target_amount: bool = True,
    ) -> RouteStruct:
        """
        Converts the trade instructions into the variables needed to instantiate the `TxSubmitHandler` class.

        Parameters
        ----------
        min_target_amount: Decimal
            The minimum target amount.
        deadline: int
            The deadline.
        web3: Web3
            The web3 instance.
        target_address: str
            The target address.
        exchange_id: int
            The exchange id.
        custom_address: str
            The custom address.
        fee: Any
            The fee.
        customData: Any
            The custom data.
        override_min_target_amount: bool
            Whether to override the minimum target amount.

        Returns
        -------
        RouteStruct
            The route struct.
        """
        if self.is_weth(target_address):
            target_address = ETH_ADDRESS

        target_address = w3.toChecksumAddress(target_address)

        if override_min_target_amount:
            min_target_amount = 1

        if exchange_id != 4:
            fee = Decimal(fee)
            fee *= Decimal(1000000)

        return RouteStruct(
            exchangeId=exchange_id,
            targetToken=target_address,
            minTargetAmount=int(min_target_amount),
            deadline=deadline,
            customAddress=custom_address,
            customInt=int(fee),
            customData=customData,
        )

    def get_route_structs(
        self, trade_instructions: List[TradeInstruction], deadline: int
    ) -> List[RouteStruct]:
        """
        Gets the RouteStruct objects into a list.

        Parameters
        ----------
        min_target_amount: Decimal
            The minimum target amount.
        deadline: int
            The deadline.
        target_address: str
            The target address.
        exchange_id: int
            The exchange id.
        custom_address: str

        """
        for t in trade_instructions:
            print(f"trade_instruction.cid: {t.cid}")

        pools = [
            self._cid_to_pool(trade_instruction.cid)
            for trade_instruction in trade_instructions
        ]

        return [
            self.to_route_struct(
                min_target_amount=Decimal(trade_instructions[idx].amtout_wei),
                deadline=deadline,
                target_address=trade_instructions[idx].tknout_address,
                exchange_id=trade_instructions[idx].exchange_id,
                custom_address=trade_instructions[
                    idx
                ].tknout_address,  # TODO: rework for bancor 2
                fee=pools[idx].fee,
                customData=trade_instructions[idx].customData,
                override_min_target_amount=True,
            )
            for idx, instructions in enumerate(trade_instructions)
        ]

    def get_arb_contract_args(
        self, trade_instructions: List[TradeInstruction], deadline: int
    ) -> Tuple[List[RouteStruct], int]:
        """
        Gets the arguments needed to instantiate the `ArbContract` class.

        Returns
        -------
        List[Any]
            The arguments needed to instantiate the `ArbContract` class.
        """
        route_struct = self.get_route_structs(
            trade_instructions=trade_instructions, deadline=deadline
        )
        # src_amount = int(self.trade_instructions_dic[0].amtin_wei)
        return route_struct

    @staticmethod
    def _agg_carbon_independentIDs(trade_instructions):
        listti = []
        for instr in trade_instructions:

            listti += [
                {
                    "cid": instr.cid + "-" + str(instr.cid_tkn)
                    if instr.cid_tkn
                    else instr.cid,
                    "tknin": instr.tknin,
                    "amtin": instr.amtin,
                    "tknout": instr.tknout,
                    "amtout": instr.amtout,
                }
            ]
        df = pd.DataFrame.from_dict(listti)
        carbons = df[df.cid.str.contains("-")].copy()
        nocarbons = df[~df.cid.str.contains("-")]
        dropindexes = []
        new_trade_instructions = []
        carbons["pair_sorting"] = carbons.tknin + carbons.tknout
        for pair_sorting in carbons.pair_sorting.unique():
            newdf = carbons[carbons.pair_sorting == pair_sorting]
            newoutput = {
                "pair_sorting": pair_sorting,
                "cid": newdf.cid.values[0],
                "tknin": newdf.tknin.values[0],
                "amtin": newdf.sum()["amtin"],
                "tknout": newdf.tknout.values[0],
                "amtout": newdf.sum()["amtout"],
                "raw_txs": str(newdf.to_dict(orient="records")),
            }
            new_trade_instructions.append(newoutput)

        print("new_trade_instructions", new_trade_instructions)
        nocarbons_instructions = []
        dictnocarbons = nocarbons.to_dict(orient="records")
        for dct in dictnocarbons:
            dct["pair_sorting"] = dct["tknin"] + dct["tknout"]
            dct["raw_txs"] = str([])
            nocarbons_instructions += [dct]

        new_trade_instructions += nocarbons_instructions
        trade_instructions = [
            TradeInstruction(**new_trade_instructions[i])
            for i in range(len(new_trade_instructions))
        ]
        return trade_instructions

    @staticmethod
    def _find_tradematches(trade_instructions):
        factor_high = 1.00001
        factor_low = 0.99999

        listti = []
        for instr in trade_instructions:
            listti += [
                {
                    "cid": instr.cid,
                    "tknin": instr.tknin,
                    "amtin": instr.amtin,
                    "tknout": instr.tknout,
                    "amtout": instr.amtout,
                }
            ]
        df = pd.DataFrame.from_dict(listti)
        df["matchedout"] = None
        df["matchedin"] = None

        for i in df.index:
            for j in df.index:
                if i != j:
                    if df.tknin[i] == df.tknout[j] and (
                        (df.amtin[i] <= -df.amtout[j] * factor_high)
                        & (df.amtin[i] >= -df.amtout[j] * factor_low)
                    ):
                        df.loc[i, "matchedin"] = j
                    if df.tknout[i] == df.tknin[j] and (
                        (df.amtout[i] >= -df.amtin[j] * factor_high)
                        & (df.amtout[i] <= -df.amtin[j] * factor_low)
                    ):
                        df.loc[i, "matchedout"] = j

        pos = df[df.matchedin.isna()].index.values[0]
        route = [pos]
        ismatchedin = True

        if pos is None:
            return trade_instructions

        while len(route) < len(df.index):
            pos = df.loc[pos, "matchedout"]
            route.append(pos)
            ismatchedin = not ismatchedin

        trade_instructions = [trade_instructions[i] for i in route if i is not None]
        return trade_instructions

    def _determine_trade_route(
        self, trade_instructions: List[TradeInstruction]
    ) -> List[int]:
        """
        Refactored determine trade route.

        Parameters
        ----------
        trade_instructions: Dict[str, Any]
            The trade instructions.

        Returns
        -------
        List[int]
            The route index.
        """
        data = self._match_trade(trade_instructions)
        return self._extract_route_index(data)

    def _extract_route_index(self, data: List[Any]) -> List[int]:
        """
        Refactored extract index.

        Parameters
        ----------
        data: List[Any]
            The data.

        Returns
        -------
        List[int]
            The route index.
        """
        result = []
        for item in data:
            if isinstance(item, tuple):
                result.append(item[0])
                sublist = self._extract_route_index(item[1:])
                result.extend(sublist)
            elif isinstance(item, list):
                sublist = self._extract_route_index(item)
                result.extend(sublist)
        return result

    @staticmethod
    def _find_match_for_tkn(
        trades: List[TradeInstruction], tkn: str, input="tknin"
    ) -> List[Any]:
        """
        Refactored find match for trade.

        Parameters
        ----------
        trades: List[TradeInstruction]
            The trades.
        tkn: str
            The token.
        input: str
            The input.

        Returns
        -------
        List[Any]
            The potential routes.
        """
        if input == "tknin":
            return [(i, x) for i, x in enumerate(trades) if x.tknout == tkn]
        else:
            return [(i, x) for i, x in enumerate(trades) if x.tknin == tkn]

    @staticmethod
    def _find_match_for_amount(
        trades: List[TradeInstruction], amount: Decimal, input="amtin"
    ) -> List[Any]:
        """
        Refactored find match for amount.

        Parameters
        ----------
        trades: List[TradeInstruction]
            The trades.
        amount: Decimal
            The amount.
        input: str
            The input.

        Returns
        -------
        List[Any]
            The potential routes.
        """
        factor_high = 1.00001
        factor_low = 0.99999
        if input == "amtin":
            return [
                (i, x)
                for i, x in enumerate(trades)
                if (x.amtout >= -amount * factor_high)
                & (x.amtout <= -amount * factor_low)
            ]
        else:
            return [
                (i, x)
                for i, x in enumerate(trades)
                if (x.amtin <= -amount * factor_high)
                & (x.amtin >= -amount * factor_low)
            ]

    def _match_trade(self, trade_instructions: List[TradeInstruction]) -> List[Any]:
        """
        Refactored match trade.

        Parameters
        ----------
        trade_instructions: Dict[str, Any]
            The trade instructions.

        Returns
        -------
        List[Any]
            The potential routes.
        """
        potential_route = []
        for i in range(len(trade_instructions)):
            trade = trade_instructions[i]
            tkn_matches = self._find_match_for_tkn(
                trade_instructions, trade.tknin, "tknin"
            )
            amt_matches = self._find_match_for_amount(
                trade_instructions, trade.amtout, "amtout"
            )
            if tkn_matches == amt_matches:
                potential_route += [(i, tkn_matches)]
        return potential_route

    def _reorder_trade_instructions(
        self, trade_instructions: List[TradeInstruction], new_route: List[int]
    ) -> List[TradeInstruction]:
        """
        Refactored reorder trade instructions.

        Parameters
        ----------
        trade_instructions_dic: List[Dict[str, str]]
            The trade instructions.
        new_route: List[int]
            The new route.

        Returns
        -------
        List[Dict[str, str]]
            The reordered trade instructions.
        """
        return [trade_instructions[i] for i in new_route]

    def _calc_amount0(
        self,
        liquidity: Decimal,
        sqrt_price_times_q96_lower_bound: Decimal,
        sqrt_price_times_q96_upper_bound: Decimal,
    ) -> Decimal:
        """
        Refactored calc amount0.

        Parameters
        ----------
        liquidity: Decimal
            The liquidity.
        sqrt_price_times_q96_lower_bound: Decimal
            The sqrt price times q96 lower bound.
        sqrt_price_times_q96_upper_bound: Decimal
            The sqrt price times q96 upper bound.

        Returns
        -------
        Decimal
            The amount0.
        """
        if sqrt_price_times_q96_lower_bound > sqrt_price_times_q96_upper_bound:
            sqrt_price_times_q96_lower_bound, sqrt_price_times_q96_upper_bound = (
                sqrt_price_times_q96_upper_bound,
                sqrt_price_times_q96_lower_bound,
            )
        return Decimal(
            liquidity
            * Q96
            * (sqrt_price_times_q96_upper_bound - sqrt_price_times_q96_lower_bound)
            / sqrt_price_times_q96_upper_bound
            / sqrt_price_times_q96_lower_bound
        )

    def _calc_amount1(
        self,
        liquidity: Decimal,
        sqrt_price_times_q96_lower_bound: Decimal,
        sqrt_price_times_q96_upper_bound: Decimal,
    ) -> Decimal:
        """
        Refactored calc amount1.

        Parameters
        ----------
        liquidity: Decimal
            The liquidity.
        sqrt_price_times_q96_lower_bound: Decimal
            The sqrt price times q96 lower bound.
        sqrt_price_times_q96_upper_bound: Decimal
            The sqrt price times q96 upper bound.

        Returns
        -------
        Decimal
            The amount1.
        """
        if sqrt_price_times_q96_lower_bound > sqrt_price_times_q96_upper_bound:
            sqrt_price_times_q96_lower_bound, sqrt_price_times_q96_upper_bound = (
                sqrt_price_times_q96_upper_bound,
                sqrt_price_times_q96_lower_bound,
            )
        return Decimal(
            liquidity
            * Q96
            * (sqrt_price_times_q96_upper_bound - sqrt_price_times_q96_lower_bound)
            / sqrt_price_times_q96_upper_bound
            / sqrt_price_times_q96_lower_bound
        )

    def _swap_token0_in(
        self,
        amount_in: Decimal,
        fee: Decimal,
        liquidity: Decimal,
        sqrt_price: Decimal,
        decimal_tkn0_modifier: Decimal,
        decimal_tkn1_modifier: Decimal,
    ) -> Decimal:
        """
        Refactored swap token0 in.

        Parameters
        ----------
        amount_in: Decimal
            The amount in.
        fee: Decimal
            The fee.
        liquidity: Decimal
            The liquidity.
        sqrt_price: Decimal
            The sqrt price.
        decimal_tkn0_modifier: Decimal
            The decimal tkn0 modifier.
        decimal_tkn1_modifier: Decimal
            The decimal tkn1 modifier.

        Returns
        -------
        Decimal
            The amount out.
        """
        amount_decimal_adjusted = (
            amount_in * decimal_tkn0_modifier * (Decimal(str(1)) - fee)
        )

        liquidity_x96 = Decimal(liquidity * Q96)
        price_next = Decimal(
            (liquidity_x96 * sqrt_price)
            / (liquidity_x96 + amount_decimal_adjusted * sqrt_price)
        )
        amount_out = self._calc_amount1(liquidity, sqrt_price, price_next)
        return Decimal(amount_out / decimal_tkn1_modifier)

    def _swap_token1_in(
        self,
        amount_in: Decimal,
        fee: Decimal,
        liquidity: Decimal,
        sqrt_price: Decimal,
        decimal_tkn0_modifier: Decimal,
        decimal_tkn1_modifier: Decimal,
    ) -> Decimal:
        """
        Refactored swap token1 in.

        Parameters
        ----------
        amount_in: Decimal
            The amount in.
        fee: Decimal
            The fee.
        liquidity: Decimal
            The liquidity.
        sqrt_price: Decimal
            The sqrt price.
        decimal_tkn0_modifier: Decimal
            The decimal tkn0 modifier.
        decimal_tkn1_modifier: Decimal
            The decimal tkn1 modifier.

        Returns
        -------
        Decimal
            The amount out.
        """
        amount = amount_in * decimal_tkn1_modifier * (Decimal(str(1)) - fee)
        price_diff = Decimal((amount * Q96) / liquidity)
        price_next = Decimal(sqrt_price + price_diff)
        amount_out = self._calc_amount0(liquidity, price_next, sqrt_price)
        return Decimal(amount_out / decimal_tkn0_modifier)

    def _calc_uniswap_v3_output(
        self,
        amount_in: Decimal,
        fee: Decimal,
        liquidity: Decimal,
        sqrt_price: Decimal,
        decimal_tkn0_modifier: Decimal,
        decimal_tkn1_modifier: Decimal,
        tkn_in: str,
        tkn_0_key: str,
    ) -> Decimal:
        """
        Refactored calc uniswap v3 output.

        Parameters
        ----------
        amount_in: Decimal
            The amount in.
        fee: Decimal
            The fee.
        liquidity: Decimal
            The liquidity.
        sqrt_price: Decimal
            The sqrt price.
        decimal_tkn0_modifier: Decimal
            The decimal tkn0 modifier.
        decimal_tkn1_modifier: Decimal
            The decimal tkn1 modifier.
        tkn_in: str
            The token in.
        tkn_0_key: str
            The token 0 key.

        Returns
        -------
        Decimal
            The amount out.
        """
        return (
            self._swap_token0_in(
                amount_in=amount_in,
                fee=fee,
                liquidity=liquidity,
                sqrt_price=sqrt_price,
                decimal_tkn0_modifier=decimal_tkn0_modifier,
                decimal_tkn1_modifier=decimal_tkn1_modifier,
            )
            if tkn_in == tkn_0_key
            else self._swap_token1_in(
                amount_in=amount_in,
                fee=fee,
                liquidity=liquidity,
                sqrt_price=sqrt_price,
                decimal_tkn0_modifier=decimal_tkn0_modifier,
                decimal_tkn1_modifier=decimal_tkn1_modifier,
            )
        )

    ONE = 2**48

    def decodeFloat(self, value):
        return (value % self.ONE) << (value // self.ONE)

    def decode(self, value):
        return self.decodeFloat(int(value)) / self.ONE

    @staticmethod
    def _get_input_trade_by_target_carbon(
        y, z, A, B, fee, tkns_out: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        Refactored get input trade by target fastlane_bot.

        Parameters
        ----------
        y: Decimal
            The y.
        z: Decimal
            The z.
        A: Decimal
            The A.
        B: Decimal
            The B.
        fee: Decimal
            The fee.
        tkns_out: Decimal
            The tokens out.

        Returns
        -------
        Tuple[Decimal, Decimal]
            The tokens in and tokens out.
        """

        fee = Decimal(str(fee))
        tkns_out = min(tkns_out, y)
        tkns_in = (
            (tkns_out * z**2) / ((A * y + B * z) * (A * y + B * z - A * tkns_out))
        ) * Decimal(1 - fee)

        return tkns_in, tkns_out

    def _get_output_trade_by_source_carbon(
        self, y, z, A, B, fee, tkns_in: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        Refactored get output trade by source fastlane_bot.

        Parameters
        ----------
        y: Decimal
            The y.
        z: Decimal
            The z.
        A: Decimal
            The A.
        B: Decimal
            The B.
        fee: Decimal
            The fee.
        tkns_in: Decimal
            The tokens in.

        Returns
        -------
        Tuple[Decimal, Decimal]
            The tuple of tokens in and tokens out.
        """

        fee = Decimal(str(fee))
        tkns_out = Decimal(
            (tkns_in * (B * z + A * y) ** 2)
            / (tkns_in * (B * A * z + A**2 * y) + z**2)
        )
        if tkns_out > y:
            tkns_in = self._get_input_trade_by_target_carbon(
                y=y, z=z, A=A, B=B, fee=fee, tkns_out=y
            )
            tkns_out = y

        tkns_out = tkns_out * (Decimal("1") - fee)
        return tkns_in, tkns_out

    def _calc_carbon_output(
        self, curve: Pool, tkn_in: str, tkn_out_decimals: int, amount_in: Decimal
    ) -> Decimal:
        """
        calc fastlane_bot output.

        Parameters
        ----------
        curve: Pool
            The pool.
        tkn_in: str
            The token in.
        amount_in: Decimal
            The amount in.

        Returns
        -------
        Decimal
            The amount out.
        """
        y, z, A, B = (
            (curve.y_0, curve.z_0, curve.A_0, curve.B_0)
            if tkn_in == curve.tkn0_key
            else (curve.y_1, curve.z_1, curve.A_1, curve.B_1)
        )

        A = Decimal(str(self.decode(A)))
        B = Decimal(str(self.decode(B)))
        y = Decimal(y) / Decimal("10") ** Decimal(str(tkn_out_decimals))
        z = Decimal(z) / Decimal("10") ** Decimal(str(tkn_out_decimals))

        amt_in, result = self._get_output_trade_by_source_carbon(
            y=y, z=z, A=A, B=B, fee=curve.fee, tkns_in=amount_in
        )
        return result

    @staticmethod
    def single_trade_result_constant_product(
        tokens_in, token0_amt, token1_amt, fee
    ) -> Decimal:
        return Decimal(
            (tokens_in * token1_amt * (1 - Decimal(fee))) / (tokens_in + token0_amt)
        )

    def _solve_trade_output(
        self, curve: Pool, trade: TradeInstruction, amount_in: Decimal = None
    ) -> Tuple[Decimal, Decimal, int, int]:

        if not isinstance(trade, TradeInstruction):
            raise Exception("trade in must be a TradeInstruction object.")

        tkn_in_decimals = (
            curve.tkn0_decimals
            if trade.tknin_key == curve.tkn0_key
            else curve.tkn1_decimals
        )
        tkn_out_decimals = (
            curve.tkn1_decimals
            if trade.tknin_key == curve.tkn0_key
            else curve.tkn0_decimals
        )

        amount_in = TradeInstruction._quantize(amount_in, tkn_in_decimals)

        if curve.exchange_name == UNISWAP_V3_NAME:
            amount_out = self._calc_uniswap_v3_output(
                tkn_in=trade.tknin_key,
                amount_in=amount_in,
                fee=Decimal(curve.fee),
                liquidity=curve.liquidity,
                sqrt_price=curve.sqrt_price_q96,
                decimal_tkn0_modifier=Decimal(10**curve.tkn0_decimals),
                decimal_tkn1_modifier=Decimal(10**curve.tkn1_decimals),
                tkn_0_key=curve.tkn0_key,
            )
        elif curve.exchange_name == CARBON_V1_NAME:
            amount_out = self._calc_carbon_output(
                curve, trade, tkn_out_decimals, amount_in
            )
        else:
            tkn0_amt, tkn1_amt = (
                (curve.tkn0_balance, curve.tkn1_balance)
                if trade == curve.tkn0_key
                else (curve.tkn1_balance, curve.tkn0_balance)
            )
            tkn0_amt = self._from_wei_to_decimals(tkn0_amt, curve.tkn0_decimals)
            tkn1_amt = self._from_wei_to_decimals(tkn1_amt, curve.tkn1_decimals)
            amount_out = self.single_trade_result_constant_product(
                tokens_in=amount_in,
                token0_amt=tkn0_amt,
                token1_amt=tkn1_amt,
                fee=curve.fee,
            )

        amount_out = amount_out * Decimal("0.999")
        amount_out = TradeInstruction._quantize(amount_out, tkn_out_decimals)
        amount_in_wei = TradeInstruction._convert_to_wei(amount_in, tkn_in_decimals)
        amount_out_wei = TradeInstruction._convert_to_wei(amount_out, tkn_out_decimals)
        return amount_in, amount_out, amount_in_wei, amount_out_wei

    def _calculate_trade_outputs(
        self, trade_instructions: List[TradeInstruction]
    ) -> List[TradeInstruction]:
        """
        Refactored calculate trade outputs.

        Parameters
        ----------
        trade_instructions: List[Dict[str, Any]]
            The trade instructions.

        Returns
        -------
        List[Dict[str, Any]]
            The trade outputs.
        """

        next_amount_in = trade_instructions[0].amtin
        for idx, trade in enumerate(trade_instructions):
            raw_txs_lst = []
            if trade.raw_txs != "[]":
                data = eval(trade.raw_txs)
                total_out = 0
                for tx in data:
                    cid = tx["cid"]
                    cid = cid.split("-")[0]
                    tknin_key = tx["tknin"]
                    curve = session.query(Pool).filter(Pool.cid == cid).first()
                    (
                        amount_in,
                        amount_out,
                        amount_in_wei,
                        amount_out_wei,
                    ) = self._solve_trade_output(
                        curve=curve, trade=trade, amount_in=next_amount_in
                    )

                    raw_txs = {
                        "cid": cid,
                        "amtin": amount_in_wei,
                        "tknin": tknin_key,
                        "amtout": amount_out_wei,
                    }
                    raw_txs_lst.append(raw_txs)

                    total_out += amount_out
                amount_out = total_out

            else:

                curve_cid = trade.cid
                curve = session.query(Pool).filter(Pool.cid == curve_cid).first()
                (
                    amount_in,
                    amount_out,
                    amount_in_wei,
                    amount_out_wei,
                ) = self._solve_trade_output(
                    curve=curve, trade=trade, amount_in=next_amount_in
                )
                trade_instructions[idx].amtin = amount_in_wei
                trade_instructions[idx].amtout = amount_out_wei

                next_amount_in = amount_out

            trade_instructions[idx].raw_txs = str(raw_txs_lst)

        return trade_instructions

    def _from_wei_to_decimals(self, tkn0_amt: Decimal, tkn0_decimals: int) -> Decimal:
        return tkn0_amt / Decimal("10") ** Decimal(str(tkn0_decimals))

    def _cid_to_pool(self, cid: str) -> Pool:
        return session.query(Pool).filter(Pool.cid == cid).first()
