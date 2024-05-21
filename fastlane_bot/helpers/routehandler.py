"""
Route handler for the Fastlane project.

Main classes defined here are

- ``RouteStruct``: represents a single trade route
- ``TxRouteHandler``: converts trade instructions from the optimizer into routes

It also defines a few helper function that should not be relied upon by external modules,
even if they happen to be exported.
---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
__VERSION__ = "1.1.1"
__DATE__ = "02/May/2023"

import decimal
from _decimal import Decimal
from dataclasses import dataclass
from typing import List, Any, Dict, Tuple

import eth_abi
import pandas as pd

from fastlane_bot.helpers.tradeinstruction import TradeInstruction
from fastlane_bot.events.interface import Pool
from fastlane_bot.utils import EncodedOrder
from fastlane_bot.config.constants import AGNI_V3_NAME, BUTTER_V3_NAME, CLEOPATRA_V3_NAME, PANCAKESWAP_V3_NAME, \
    ETHEREUM, METAVAULT_V3_NAME


@dataclass
class RouteStruct:
    """
    A class that represents a single trade route in the format required by the arbitrage contract Route struct.

    Parameters
    ----------
    platformId: int
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

    platformId: int
    sourceToken: str
    targetToken: str
    sourceAmount: int
    minTargetAmount: int
    deadline: int
    customAddress: str
    customInt: int
    customData: bytes


def maximize_last_trade_per_tkn(route_struct: List[Dict[str, Any]]):
    """
    Sets the source amount of the last trade to 0 per-token, ensuring that all tokens held will be used in the last trade.
    :param route_struct: the route struct object
    """

    tkns_traded = set([route_struct[0]["sourceToken"]])
    for j, trade in enumerate(reversed(route_struct)):
        idx = len(route_struct) - 1 - j
        if trade["sourceToken"] not in tkns_traded:
            tkns_traded.add(trade["sourceToken"])
            route_struct[idx]["sourceAmount"] = 0


@dataclass
class TxRouteHandler:
    """
    A class that handles the routing of the bot by converting trade instructions into routes.

    Parameters
    ----------
    trade_instructions_dic: List[Dict[str, Any]]
        The trade instructions. Formatted output from the `CPCOptimizer` class.
    trade_instructions_df: pd.DataFrame
        The trade instructions as a dataframe. Formatted output from the `CPCOptimizer` class.
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    trade_instructions: List[TradeInstruction]

    def __post_init__(self):
        if len(self.trade_instructions) < 2:
            raise ValueError("Length of trade instructions must be greater than 1.")
        self.ConfigObj = self.trade_instructions[0].ConfigObj

    @staticmethod
    def custom_data_encoder(
            agg_trade_instructions: List[TradeInstruction],
    ) -> List[TradeInstruction]:
        for i in range(len(agg_trade_instructions)):
            instr = agg_trade_instructions[i]
            if instr.raw_txs == "[]":
                instr.custom_data = "0x"
                agg_trade_instructions[i] = instr
            else:
                tradeInfo = eval(instr.raw_txs)
                tradeActions = []
                for trade in tradeInfo:
                    tradeActions += [
                        {
                            "strategyId": int(trade["strategy_id"]),
                            "amount": int(
                                trade["_amtin_wei"]
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
                instr.custom_data = '0x' + str(encoded_data.hex())
                agg_trade_instructions[i] = instr
        return agg_trade_instructions

    def _to_route_struct(
            self,
            min_target_amount: int,
            deadline: int,
            target_address: str,
            platform_id: int,
            custom_address: str,
            customData: Any,
            customInt: int,
            source_token: str,
            source_amount:int,
            exchange_name: str
    ) -> RouteStruct:
        """
        Converts trade instructions into routes.

        Parameters
        ----------
        min_target_amount: int
            The minimum target amount.
        deadline: int
            The deadline.
        target_address: str
            The target address.
        platform_id: int
            The exchange id.
        custom_address: str
            The custom address.
        customData: Any
            The custom data.
        override_min_target_amount: bool
            Whether to override the minimum target amount.
        sourceToken: str
            The source token of the trade. V2 routes only.
        sourceAmount: float,
            The source token amount for the trade. V2 routes only.
        exchange_name: str
            The name of the exchange. This is specifically for toggling router overrides.

        Returns
        -------
        RouteStruct
            The route struct.
        """
        target_address = self.ConfigObj.w3.to_checksum_address(target_address)
        source_token = self.ConfigObj.w3.to_checksum_address(source_token)
        customData = self._handle_custom_data_extras(
            platform_id=platform_id,
            custom_data=customData,
            exchange_name=exchange_name
        )

        return RouteStruct(
            platformId=platform_id,
            targetToken=target_address,
            sourceToken=source_token,
            sourceAmount=source_amount,
            minTargetAmount=min_target_amount,
            deadline=deadline,
            customAddress=custom_address,
            customInt=customInt,
            customData=customData,
        )

    def _handle_custom_data_extras(self, platform_id: int, custom_data: bytes, exchange_name: str):
        """
        This function toggles between Uniswap V3 routers used by the Fast Lane contract. This is input in the customData field.

        :param platform_id: int
        :param custom_data: bytes
        :param exchange_name: str

        returns:
            custom_data: bytes
        """

        if platform_id == self.ConfigObj.network.EXCHANGE_IDS.get(self.ConfigObj.network.UNISWAP_V3_NAME):
            assert custom_data == "0x", f"[routehandler.py _handle_custom_data_extras] attempt to override input custom_data {custom_data}"
            if self.ConfigObj.network.NETWORK == ETHEREUM or exchange_name in [PANCAKESWAP_V3_NAME, BUTTER_V3_NAME, AGNI_V3_NAME, CLEOPATRA_V3_NAME, METAVAULT_V3_NAME]:
                return '0x0000000000000000000000000000000000000000000000000000000000000000'
            else:
                return '0x0100000000000000000000000000000000000000000000000000000000000000'

        if platform_id == self.ConfigObj.network.EXCHANGE_IDS.get(self.ConfigObj.network.AERODROME_V2_NAME):
            assert custom_data == "0x", f"[routehandler.py _handle_custom_data_extras] attempt to override input custom_data {custom_data}"
            return '0x' + eth_abi.encode(['address'], [self.ConfigObj.network.FACTORY_MAPPING[exchange_name]]).hex()

        return custom_data

    def get_route_structs(
            self, trade_instructions: List[TradeInstruction] = None, deadline: int = None
    ) -> List[RouteStruct]:
        """
        Gets the RouteStruct objects into a list.

        Parameters
        ----------
        trade_instructions: List[TradeInstruction]
            The trade instructions.
        deadline: int
            The deadline.


        """
        if trade_instructions is None:
            trade_instructions = self.trade_instructions

        assert not deadline is None, "deadline cannot be None"

        return [
            self._to_route_struct(
                min_target_amount=trade_instruction.amtout_wei,
                deadline=deadline,
                target_address=trade_instruction.get_real_tkn_out,
                custom_address=self.get_custom_address(trade_instruction.db.get_pool(cid=trade_instruction.cid)),
                platform_id=trade_instruction.platform_id,
                customInt=trade_instruction.custom_int,
                customData=trade_instruction.custom_data,
                source_token=trade_instruction.get_real_tkn_in,
                source_amount=trade_instruction.amtin_wei,
                exchange_name=trade_instruction.exchange_name,
            )
            for trade_instruction in trade_instructions
        ]

    def get_custom_address(
            self,
            pool: Pool
    ):
        """
        This function gets the custom address field. For Bancor V2 this is the anchor. For Uniswap V2/V3 forks, this is the router address.
        :param pool: Pool

        returns: str
        """
        if pool.exchange_name == self.ConfigObj.BANCOR_V2_NAME:
            return pool.anchor
        elif pool.exchange_name in self.ConfigObj.CARBON_V1_FORKS:
            return self.ConfigObj.CARBON_CONTROLLER_MAPPING[pool.exchange_name]
        elif pool.exchange_name in self.ConfigObj.UNI_V2_FORKS:
            return self.ConfigObj.UNI_V2_ROUTER_MAPPING[pool.exchange_name]
        elif pool.exchange_name in self.ConfigObj.SOLIDLY_V2_FORKS:
            return self.ConfigObj.SOLIDLY_V2_ROUTER_MAPPING[pool.exchange_name]
        elif pool.exchange_name in self.ConfigObj.CARBON_V1_FORKS:
            return self.ConfigObj.CARBON_CONTROLLER_ADDRESS
        elif pool.exchange_name in self.ConfigObj.UNI_V3_FORKS:
            return self.ConfigObj.UNI_V3_ROUTER_MAPPING[pool.exchange_name]
        else:
            return pool.tkn0_address

    def generate_flashloan_struct(self, trade_instructions_objects: List[TradeInstruction]) -> List[Dict]:
        """
        Generates the flashloan struct for submitting FlashLoanAndArbV2 transactions
        :param trade_instructions_objects: a list of TradeInstruction objects

        :return:
            list
        """
        is_FL_NATIVE_permitted = self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_ETHEREUM

        if trade_instructions_objects[0].tknin_is_native and not is_FL_NATIVE_permitted:
            source_token = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
        elif trade_instructions_objects[0].tknin_is_native and is_FL_NATIVE_permitted:
            source_token = self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS
        elif trade_instructions_objects[0].tknin_is_wrapped:
            source_token = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
        else:
            source_token = trade_instructions_objects[0].tknin_address

        if self.ConfigObj.NETWORK in [
            self.ConfigObj.NETWORK_ETHEREUM,
            self.ConfigObj.NETWORK_TENDERLY
        ] and source_token in [
            self.ConfigObj.BNT_ADDRESS,
            self.ConfigObj.ETH_ADDRESS,
            self.ConfigObj.WBTC_ADDRESS,
            self.ConfigObj.LINK_ADDRESS
        ]:
            return [
                {
                    "platformId": 2,
                    "sourceTokens": [self.wrapped_gas_token_to_native(source_token)],
                    "sourceAmounts": [abs(trade_instructions_objects[0].amtin_wei)]
                }
            ]
        else:
            return [
                {
                    "platformId": 7,
                    "sourceTokens": [source_token],
                    "sourceAmounts": [abs(trade_instructions_objects[0].amtin_wei)]
                }
            ]

    def native_gas_token_to_wrapped(self, tkn: str):
        """
        This function returns the wrapped gas token address if the input token is the native gas token, otherwise it returns the input token address.
        :param tkn: str
            The token address
        returns: str
            The token address, converted to wrapped gas token if the input was the native gas token
        """
        return self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS if tkn == self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS else tkn

    def wrapped_gas_token_to_native(self, tkn: str):
        """
        This function returns the native gas token address if the input token is the wrapped gas token, otherwise it returns the input token address.
        :param tkn: str
            The token address
        returns: str
            The token address, converted to native gas token if the input was the wrapped gas token
        """
        return self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS if tkn == self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS else tkn

    @staticmethod
    def _get_trade_dicts_from_objects(trade_instructions: List[TradeInstruction]) -> List[Dict[str, Any]]:
        return [
            {
                "cid": instr.cid + "-" + str(instr.cid_tkn)
                if instr.cid_tkn
                else instr.cid,
                "tknin": instr.tknin,
                "amtin": instr.amtin,
                "_amtin_wei": instr.amtin_wei,
                "tknout": instr.tknout,
                "amtout": instr.amtout,
                "_amtout_wei": instr.amtout_wei,
            }
            for instr in trade_instructions
        ]

    @staticmethod
    def _slice_dataframe(df: pd.DataFrame) -> List[Tuple[int, pd.DataFrame]]:
        """
        Slices a dataframe into a list of dataframes.

        Parameters
        ----------
        df: pd.DataFrame
            The dataframe to slice.

        Returns
        -------
        List[Tuple[int, pd.DataFrame]]
            The list of dataframes.

        """
        slices = []
        current_pair_sorting = df.pair_sorting.values[0]
        current_slice = []

        for index, row in df.iterrows():
            if row['pair_sorting'] == current_pair_sorting:
                current_slice.append(index)
            else:
                slices.append(df.loc[current_slice])
                current_pair_sorting = row['pair_sorting']
                current_slice = [index]

        slices.append(df.loc[current_slice])

        min_index = []
        for df in slices:
            min_index += [min(df.index.values)]

        return list(zip(min_index, slices))

    @staticmethod
    def aggregate_bancor_v3_trades(calculated_trade_instructions: List[TradeInstruction]):
        """
        This function aggregates Bancor V3 trades into a single multi-hop when possible

        Parameters
        ----------
        calculated_trade_instructions: List[TradeInstruction]
            Trade instructions that have already had trades calculated


        Returns
        -------
        calculated_trade_instructions
            The trade instructions now with Bancor V3 trades combined into single trades when possible.
        """

        for idx, trade in enumerate(calculated_trade_instructions):
            if idx > 0:
                if trade.exchange_name == calculated_trade_instructions[idx - 1].exchange_name == "bancor_v3":
                    trade_before = calculated_trade_instructions[idx - 1]
                    # This checks for a two-hop trade through BNT and combines them
                    if trade_before.tknout_address == trade.tknin_address == trade.ConfigObj.BNT_ADDRESS:
                        new_trade_instruction = TradeInstruction(ConfigObj=trade.ConfigObj, cid=trade_before.cid,
                                                                 amtin=trade_before.amtin, amtout=trade.amtout,
                                                                 tknin=trade_before.tknin_address,
                                                                 tknout=trade.tknout_address,
                                                                 pair_sorting="", raw_txs="[]", db=trade.db)
                        new_trade_instruction.tknout_is_native = trade.tknout_is_native
                        new_trade_instruction.tknout_is_wrapped = trade.tknout_is_wrapped
                        calculated_trade_instructions[idx - 1] = new_trade_instruction
                        calculated_trade_instructions.pop(idx)

        return calculated_trade_instructions

    def aggregate_carbon_trades(self, trade_instructions_objects: List[TradeInstruction]) -> List[TradeInstruction]:
        """
        Aggregate carbon independent IDs and create trade instructions.

        This function takes a list of dictionaries containing trade instructions,
        aggregates the instructions with carbon independent IDs, and creates
        a list of TradeInstruction objects.

        Parameters
        ----------
        trade_instructions_objects: List[TradeInstruction]
            The trade instructions objects.

        Returns
        -------
        List[TradeInstruction]
            The trade instructions objects.

        """
        config_object = trade_instructions_objects[0].ConfigObj
        db = trade_instructions_objects[0].db

        listti = self._get_trade_dicts_from_objects(trade_instructions_objects)
        df = pd.DataFrame(listti)
        df["pair_sorting"] = df.tknin + df.tknout
        df['carbon'] = [True if '-' in df.cid[i] else False for i in df.index]

        carbons = df[df['carbon']].copy()
        nocarbons = df[~df['carbon']].copy()
        nocarbons["raw_txs"] = str([])
        nocarbons["ConfigObj"] = config_object
        nocarbons["db"] = db

        carbons.drop(['carbon'], axis=1, inplace=True)
        nocarbons.drop(['carbon'], axis=1, inplace=True)

        new_trade_instructions_nocarbons = {i: nocarbons.loc[i].to_dict() for i in nocarbons.index}

        result = self._slice_dataframe(carbons)
        new_trade_instructions_carbons = {min_index:
            {
                "pair_sorting": newdf.pair_sorting.values[0],
                "cid": newdf.cid.values[0].split("-")[0],
                "strategy_id": db.get_pool(cid=newdf.cid.values[0].split("-")[0]).strategy_id,
                "tknin": newdf.tknin.values[0],
                "amtin": newdf.amtin.sum(),
                "_amtin_wei": newdf._amtin_wei.sum(),
                "tknout": newdf.tknout.values[0],
                "amtout": newdf.amtout.sum(),
                "_amtout_wei": newdf._amtout_wei.sum(),
                "raw_txs": str(newdf.to_dict(orient="records")),
                "ConfigObj": config_object,
                "db": db,
            }
            for min_index, newdf in result}

        new_trade_instructions_carbons.update(new_trade_instructions_nocarbons)
        agg_trade_instructions = []
        for i in sorted(list(new_trade_instructions_carbons.keys())):
            agg_trade_instructions += [TradeInstruction(**new_trade_instructions_carbons[i])]
        return agg_trade_instructions

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
            * (sqrt_price_times_q96_upper_bound - sqrt_price_times_q96_lower_bound)
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
        amount_in = amount_in * (Decimal(str(1)) - fee)

        price_next = Decimal(
            int(liquidity * self.ConfigObj.Q96 * sqrt_price)
            // int(liquidity * self.ConfigObj.Q96 + amount_in * decimal_tkn0_modifier * sqrt_price)
        )
        amount_out = self._calc_amount1(liquidity, sqrt_price, price_next) / self.ConfigObj.Q96

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

        amount_in = amount_in * (Decimal(str(1)) - fee)
        result = (((liquidity * self.ConfigObj.Q96 * ((((
                                                                amount_in * decimal_tkn1_modifier * self.ConfigObj.Q96) / liquidity) + sqrt_price) - sqrt_price) / (
                        (((amount_in * decimal_tkn1_modifier * self.ConfigObj.Q96) / liquidity) + sqrt_price)) / (
                        sqrt_price)) / decimal_tkn0_modifier))

        return result

    def _calc_uniswap_v3_output(
            self,
            amount_in: Decimal,
            fee: Decimal,
            liquidity: Decimal,
            sqrt_price: Decimal,
            decimal_tkn0_modifier: Decimal,
            decimal_tkn1_modifier: Decimal,
            tkn_in: str,
            tkn_out: str,
            tkn_0_address: str,
            tkn_1_address: str
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
        tkn_0_address: str
            The token 0 key.

        Returns
        -------
        Decimal
            The amount out.
        """
        assert tkn_in == tkn_0_address or tkn_out == tkn_0_address, f"Uniswap V3 swap token mismatch, tkn_in: {tkn_in}, tkn_0_address: {tkn_0_address}, tkn_1_address: {tkn_1_address}"
        assert tkn_in == tkn_1_address or tkn_out == tkn_1_address, f"Uniswap V3 swap token mismatch, tkn_in: {tkn_in}, tkn_0_address: {tkn_0_address}, tkn_1_address: {tkn_1_address}"

        liquidity = Decimal(str(liquidity))
        fee = Decimal(str(fee))
        sqrt_price = Decimal(str(sqrt_price))
        decimal_tkn0_modifier = Decimal(str(decimal_tkn0_modifier))
        decimal_tkn1_modifier = Decimal(str(decimal_tkn1_modifier))

        # print(f"[_calc_uniswap_v3_output] tkn_in={tkn_in}, tkn_0_address={tkn_0_address}, tkn_1_address={tkn_1_address}, tkn0_in={tkn_in == tkn_0_address}, liquidity={liquidity}, fee={fee}, sqrt_price={sqrt_price}, decimal_tkn0_modifier={decimal_tkn0_modifier}, decimal_tkn1_modifier={decimal_tkn1_modifier}")

        return (
            self._swap_token0_in(
                amount_in=amount_in,
                fee=fee,
                liquidity=liquidity,
                sqrt_price=sqrt_price,
                decimal_tkn0_modifier=decimal_tkn0_modifier,
                decimal_tkn1_modifier=decimal_tkn1_modifier,
            )
            if tkn_in == tkn_0_address
            else self._swap_token1_in(
                amount_in=amount_in,
                fee=fee,
                liquidity=liquidity,
                sqrt_price=sqrt_price,
                decimal_tkn0_modifier=decimal_tkn0_modifier,
                decimal_tkn1_modifier=decimal_tkn1_modifier,
            )
        )

    def decode_decimal_adjustment(self, value: Decimal, tkn_in_decimals: int or str, tkn_out_decimals: int or str):
        tkn_in_decimals = int(tkn_in_decimals)
        tkn_out_decimals = int(tkn_out_decimals)
        return value * Decimal("10") ** (
                (tkn_in_decimals - tkn_out_decimals) / Decimal("2")
        )

    @staticmethod
    def _get_input_trade_by_target_carbon(
            y, z, A, B, fee, tkns_out: Decimal, trade_by_source: bool = True
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
        # Fee set to 0 to avoid
        fee = Decimal(str(fee))
        tkns_out = min(tkns_out, y)
        tkns_in = (
                (tkns_out * z ** 2) / ((A * y + B * z) * (A * y + B * z - A * tkns_out))
        )

        if not trade_by_source:
            # Only taking fee if calculating by trade by target. Otherwise fee will be calculated in trade by source function.
            tkns_in = tkns_in * Decimal(1 - fee)

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
            / (tkns_in * (B * A * z + A ** 2 * y) + z ** 2)
        )
        if tkns_out > y:
            tkns_in, tkns_out = self._get_input_trade_by_target_carbon(
                y=y, z=z, A=A, B=B, fee=fee, tkns_out=y, trade_by_source=True
            )

        tkns_out = tkns_out * (Decimal("1") - fee)
        return tkns_in, tkns_out

    def _calc_carbon_output(
            self, curve: Pool, tkn_in: str, tkn_in_decimals: int, tkn_out_decimals: int, amount_in: Decimal
    ):
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
        assert tkn_in != self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, "[routehandler.py _calc_carbon_output] Function does not expect native gas token as input."
        amount_in = Decimal(str(amount_in))

        tkn0_address = curve.pair_name.split("/")[0]
        tkn1_address = curve.pair_name.split("/")[1]
        tkn0_address = self.native_gas_token_to_wrapped(tkn=tkn0_address)
        tkn1_address = self.native_gas_token_to_wrapped(tkn=tkn1_address)

        # print(f"[_calc_carbon_output] tkn0_address={tkn0_address}, tkn1_address={tkn1_address}, ")

        assert tkn_in == tkn0_address or tkn_in == tkn1_address, f"Token in: {tkn_in} does not match tokens in Carbon Curve: {tkn0_address} & {tkn1_address}"

        # print(f"[_calc_carbon_output] tkn0_address={tkn0_address}, tkn1_address={tkn1_address}, tkn_int={tkn_in}, using curve0={tkn_in == tkn1_address}")
        y, z, A, B = (
            (curve.y_0, curve.z_0, curve.A_0, curve.B_0)
            if tkn_in == tkn1_address
            else (curve.y_1, curve.z_1, curve.A_1, curve.B_1)
        )

        if A is None:
            A = 0

        # print('[_calc_carbon_output] before decode: ', y, z, A, B)
        A = self.decode_decimal_adjustment(value=Decimal(str(EncodedOrder.decode(A))), tkn_in_decimals=tkn_in_decimals,
                                           tkn_out_decimals=tkn_out_decimals)
        B = self.decode_decimal_adjustment(value=Decimal(str(EncodedOrder.decode(B))), tkn_in_decimals=tkn_in_decimals,
                                           tkn_out_decimals=tkn_out_decimals)
        y = Decimal(y) / Decimal("10") ** Decimal(str(tkn_out_decimals))
        z = Decimal(z) / Decimal("10") ** Decimal(str(tkn_out_decimals))
        # print('[_calc_carbon_output] after decode: ', y, z, A, B)
        assert y > 0, f"Trade incoming to empty Carbon curve: {curve}"

        # print(f"[_calc_carbon_output] Carbon curve decoded: {y, z, A, B}, fee = {Decimal(curve.fee)}, amount_in={amount_in}")

        amt_in, result = self._get_output_trade_by_source_carbon(
            y=y, z=z, A=A, B=B, fee=Decimal(curve.fee_float), tkns_in=amount_in
        )
        return amt_in, result

    @staticmethod
    def _single_trade_result_constant_product(
            tokens_in, token0_amt, token1_amt, fee
    ) -> Decimal:
        return Decimal(
            (tokens_in * token1_amt * (1 - Decimal(fee))) / (tokens_in + token0_amt)
        )

    def _calc_balancer_output(self, curve: Pool, tkn_in: str, tkn_out: str, amount_in: Decimal):
        """
        This is a wrapper function that extracts the necessary pool values to pass into the Balancer swap equation and passes them into the low-level function.
        curve: Pool
            The pool.
        tkn_in: str
            The token in.
        tkn_out: str
            The token out.
        amount_in: Decimal
            The amount in.

        returns:
            The number of tokens expected to be received by the trade.
        """
        tkn_in_weight = Decimal(str(curve.get_token_weight(tkn=tkn_in)))
        tkn_in_balance = Decimal(str(curve.get_token_balance(tkn=tkn_in))) / 10 ** Decimal(
            str(curve.get_token_decimals(tkn=tkn_in)))
        tkn_out_weight = Decimal(str(curve.get_token_weight(tkn=tkn_out)))
        tkn_out_balance = Decimal(str(curve.get_token_balance(tkn=tkn_out))) / 10 ** Decimal(
            str(curve.get_token_decimals(tkn=tkn_out)))
        self.ConfigObj.logger.debug(
            f"[routehandler.py _calc_balancer_output] tknin {tkn_in} weight: {tkn_in_weight}, tknout {tkn_out} tknout weight: {tkn_out_weight}")

        # Extract trade fee from amount in
        fee = Decimal(str(amount_in)) * Decimal(str(curve.fee_float))
        amount_in = amount_in - fee

        if amount_in > (tkn_in_balance * Decimal("0.3")):
            raise BalancerInputTooLargeError(
                "Balancer has a hard constraint that amount in must be less than 30% of the pool balance of tkn in, making this trade invalid.")

        amount_out = self._calc_balancer_out_given_in(balance_in=tkn_in_balance, weight_in=tkn_in_weight,
                                                      balance_out=tkn_out_balance, weight_out=tkn_out_weight,
                                                      amount_in=amount_in)
        if amount_out > (tkn_out_balance * Decimal("0.3")):
            raise BalancerOutputTooLargeError(
                "Balancer has a hard constraint that the amount out must be less than 30% of the pool balance of tkn out, making this trade invalid.")

        # amount_in = (1 - Decimal(str(curve.fee_float))) * Decimal(str(amount_in))
        return amount_out

    @staticmethod
    def _calc_balancer_out_given_in(balance_in: Decimal,
                                    weight_in: Decimal,
                                    balance_out: Decimal,
                                    weight_out: Decimal,
                                    amount_in: Decimal) -> Decimal:
        """
        This function uses the Balancer swap equation to calculate the token output, given an input.

        :param balance_in: the pool balance of the source token
        :param weight_in: the pool weight of the source token
        :param balance_out: the pool balance of the target token
        :param weight_out: the pool weight of the target token
        :param amount_in: the number of source tokens trading into the pool

        returns:
        The number of tokens expected to be received by the trade.

        """

        denominator = balance_in + amount_in
        base = divUp(balance_in, denominator)  # balanceIn.divUp(denominator);
        exponent = divDown(weight_in, weight_out)  # weightIn.divDown(weightOut);
        power = powUp(base, exponent)  # base.powUp(exponent);

        return mulDown(balance_out, complement(power))  # balanceOut.mulDown(power.complement());

    def _solve_trade_output(
            self, curve: Pool, trade: TradeInstruction, amount_in: Decimal = None
    ) -> Tuple[Decimal, Decimal, int, int]:

        if not isinstance(trade, TradeInstruction):
            raise Exception("trade in must be a TradeInstruction object.")

        if curve.exchange_name != "balancer":
            tkn0_address = curve.pair_name.split("/")[0]
            tkn1_address = curve.pair_name.split("/")[1]
            tkn0_decimals = int(trade.db.get_token(tkn_address=tkn0_address).decimals)
            tkn1_decimals = int(trade.db.get_token(tkn_address=tkn1_address).decimals)

            tkn0_address = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS if tkn0_address in self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS and (
                    trade.tknin_address in self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS or trade.tknout_address in self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS) else tkn0_address
            tkn1_address = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS if tkn1_address == self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS and (
                    trade.tknin_address == self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS or trade.tknout_address == self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS) else tkn1_address

            assert tkn0_address == trade.tknin_address or tkn0_address == trade.tknout_address, f"[_solve_trade_output] tkn0_address {tkn0_address} !=  trade.tknin_address {trade.tknin_address} or trade.tknout_address {trade.tknout_address}"
            assert tkn1_address == trade.tknin_address or tkn1_address == trade.tknout_address, f"[_solve_trade_output] tkn1_address {tkn1_address} !=  trade.tknin_address {trade.tknin_address} or trade.tknout_address {trade.tknout_address}"
            assert tkn0_address != tkn1_address, f"[_solve_trade_output] tkn0_address == tkn_1_address {tkn0_address}, {tkn1_address}"

        else:
            tokens = curve.get_tokens
            assert trade.tknin_address in tokens, f"[_solve_trade_output] trade.tknin_address {trade.tknin_address} not in Balancer curve tokens: {tokens}"
            assert trade.tknout_address in tokens, f"[_solve_trade_output] trade.tknout_address {trade.tknout_address} not in Balancer curve tokens: {tokens}"

        tkn_in_decimals = int(trade.db.get_token(tkn_address=trade.tknin_address).decimals)
        tkn_out_decimals = int(trade.db.get_token(tkn_address=trade.tknout_address).decimals)

        amount_in = TradeInstruction._quantize(amount_in, tkn_in_decimals)

        if curve.exchange_name in self.ConfigObj.UNI_V3_FORKS:
            amount_out = self._calc_uniswap_v3_output(
                tkn_in=trade.tknin_address,
                tkn_out=trade.tknout_address,
                amount_in=amount_in,
                fee=Decimal(curve.fee_float),
                liquidity=curve.liquidity,
                sqrt_price=curve.sqrt_price_q96,
                decimal_tkn0_modifier=Decimal(10 ** tkn0_decimals),
                decimal_tkn1_modifier=Decimal(10 ** tkn1_decimals),
                tkn_0_address=tkn0_address,
                tkn_1_address=tkn1_address
            )
        elif curve.exchange_name in self.ConfigObj.CARBON_V1_FORKS or curve.exchange_name == self.ConfigObj.BANCOR_POL_NAME:
            amount_in, amount_out = self._calc_carbon_output(
                curve=curve, tkn_in=trade.tknin_address, tkn_in_decimals=tkn_in_decimals,
                tkn_out_decimals=tkn_out_decimals, amount_in=amount_in
            )
        elif curve.exchange_name == self.ConfigObj.BALANCER_NAME:
            amount_out = self._calc_balancer_output(curve=curve, tkn_in=trade.tknin_address,
                                                    tkn_out=trade.tknout_address, amount_in=amount_in)

        elif curve.exchange_name in self.ConfigObj.SOLIDLY_V2_FORKS and curve.pool_type in "stable":
            raise ExchangeNotSupportedError(
                f"[routerhandler.py _solve_trade_output] Solidly V2 stable pools are not yet supported")
        else:
            tkn0_amt, tkn1_amt = (
                (curve.tkn0_balance, curve.tkn1_balance)
                if trade.tknin_address == tkn0_address
                else (curve.tkn1_balance, curve.tkn0_balance)
            )
            tkn0_dec = tkn0_decimals if trade.tknin_address == tkn0_address else tkn1_decimals
            tkn1_dec = tkn1_decimals if trade.tknout_address == tkn1_address else tkn0_decimals

            tkn0_amt = self._from_wei_to_decimals(tkn0_amt, tkn0_dec)
            tkn1_amt = self._from_wei_to_decimals(tkn1_amt, tkn1_dec)

            amount_out = self._single_trade_result_constant_product(
                tokens_in=amount_in,
                token0_amt=tkn0_amt,
                token1_amt=tkn1_amt,
                fee=curve.fee_float,
            )

        amount_out = amount_out * Decimal("0.9999")
        amount_out = TradeInstruction._quantize(amount_out, tkn_out_decimals)
        amount_in_wei = TradeInstruction._convert_to_wei(amount_in, tkn_in_decimals)
        amount_out_wei = TradeInstruction._convert_to_wei(amount_out, tkn_out_decimals)
        return amount_in, amount_out, amount_in_wei, amount_out_wei

    def calculate_trade_profit(
            self, trade_instructions: List[TradeInstruction]
    ) -> int or float or Decimal:
        """
        Calculates the profit of the trade in the Flashloan token by calculating the sum in vs sum out
        """
        sum_in = 0
        sum_out = 0
        flt = trade_instructions[0].tknin_address

        for trade in trade_instructions:
            if trade.tknin_address == flt:
                sum_in += abs(trade.amtin)
            elif trade.tknout_address == flt:
                sum_out += abs(trade.amtout)
        sum_profit = sum_out - sum_in
        return sum_profit

    def calculate_trade_outputs(
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
            # total_percent = 0
            if trade.amtin <= 0:
                trade_instructions.pop(idx)
                continue
            if trade.raw_txs != "[]":
                data = eval(trade.raw_txs)
                expected_in = trade_instructions[idx].amtin

                remaining_tkn_in = Decimal(str(next_amount_in))

                for tx in data:
                    try:
                        tx["percent_in"] = Decimal(str(tx["amtin"])) / Decimal(str(expected_in))
                    except decimal.InvalidOperation:
                        tx["percent_in"] = 0
                        # total_percent += tx["amtin"]/expected_in
                        self.ConfigObj.logger.warning(
                            f"[calculate_trade_outputs] Invalid operation: {tx['amtin']}/{expected_in}")

                last_tx = len(data) - 1

                for _idx, tx in enumerate(data):
                    cid = tx["cid"].split("-")[0]
                    curve = trade_instructions[idx].db.get_pool(cid=cid)
                    strategy_id = curve.strategy_id

                    _next_amt_in = Decimal(str(next_amount_in)) * tx["percent_in"]
                    if _next_amt_in > remaining_tkn_in:
                        _next_amt_in = remaining_tkn_in

                    if _idx == last_tx:
                        if _next_amt_in < remaining_tkn_in:
                            _next_amt_in = remaining_tkn_in


                    (
                        amount_in,
                        amount_out,
                        amount_in_wei,
                        amount_out_wei,
                    ) = self._solve_trade_output(
                        curve=curve, trade=trade, amount_in=_next_amt_in
                    )

                    remaining_tkn_in -= amount_in

                    if amount_in_wei <= 0:
                        continue
                    raw_txs = {
                        "cid": cid,
                        "strategy_id": strategy_id,
                        "tknin": tx["tknin"],
                        "amtin": amount_in,
                        "_amtin_wei": amount_in_wei,
                        "tknout": tx["tknout"],
                        "amtout": amount_out,
                        "_amtout_wei": amount_out_wei,
                    }
                    raw_txs_lst.append(raw_txs)

                    remaining_tkn_in = TradeInstruction._quantize(amount=remaining_tkn_in,
                                                                  decimals=trade.tknin_decimals)
                    if _idx == last_tx and remaining_tkn_in > 0:

                        for __idx, _tx in enumerate(raw_txs_lst):
                            adjusted_next_amt_in = _tx["amtin"] + remaining_tkn_in
                            _curve = trade_instructions[idx].db.get_pool(cid=_tx["cid"])
                            (
                                _amount_in,
                                _amount_out,
                                _amount_in_wei,
                                _amount_out_wei,
                            ) = self._solve_trade_output(
                                curve=_curve, trade=trade, amount_in=adjusted_next_amt_in
                            )

                            test_remaining = remaining_tkn_in - _amount_in + _tx["amtin"]
                            remaining_tkn_in = TradeInstruction._quantize(amount=remaining_tkn_in,
                                                                          decimals=trade.tknin_decimals)
                            if test_remaining < 0:
                                continue

                            remaining_tkn_in = remaining_tkn_in + _tx["amtin"] - _amount_in

                            _raw_txs = {
                                "cid": _tx["cid"],
                                "strategy_id": _curve.strategy_id,
                                "tknin": _tx["tknin"],
                                "amtin": _amount_in,
                                "_amtin_wei": _amount_in_wei,
                                "tknout": _tx["tknout"],
                                "amtout": _amount_out,
                                "_amtout_wei": _amount_out_wei,
                            }

                            raw_txs_lst[__idx] = _raw_txs

                            if remaining_tkn_in == 0:
                                break

                _total_in = 0
                _total_in_wei = 0
                _total_out = 0
                _total_out_wei = 0
                for raw_tx in raw_txs_lst:
                    _total_in += raw_tx["amtin"]
                    _total_in_wei += raw_tx["_amtin_wei"]
                    _total_out += raw_tx["amtout"]
                    _total_out_wei += raw_tx["_amtout_wei"]

                trade_instructions[idx].amtin = _total_in
                trade_instructions[idx].amtout = _total_out
                trade_instructions[idx]._amtin_wei = _total_in_wei
                trade_instructions[idx]._amtout_wei = _total_out_wei
                trade_instructions[idx].raw_txs = str(raw_txs_lst)
                amount_out = _total_out

            else:

                curve_cid = trade.cid
                curve = trade_instructions[idx].db.get_pool(cid=curve_cid)
                (
                    amount_in,
                    amount_out,
                    amount_in_wei,
                    amount_out_wei,
                ) = self._solve_trade_output(
                    curve=curve, trade=trade, amount_in=next_amount_in
                )
                trade_instructions[idx].amtin = amount_in
                trade_instructions[idx].amtout = amount_out
                trade_instructions[idx]._amtin_wei = amount_in_wei
                trade_instructions[idx]._amtout_wei = amount_out_wei

            next_amount_in = amount_out

        return trade_instructions

    def _from_wei_to_decimals(self, tkn0_amt: Decimal, tkn0_decimals: int) -> Decimal:
        return Decimal(str(tkn0_amt)) / Decimal("10") ** Decimal(str(tkn0_decimals))

# TODO: Those functions should probably be private; also -- are they needed at
# all? Most of them seem to be extremely trivial

def divUp(a: Decimal, b: Decimal) -> Decimal:
    if a * b == 0:
        return Decimal(0)
    else:
        return a / b


def mulDown(a: Decimal, b: Decimal) -> Decimal:
    return a * b


def divDown(a: Decimal, b: Decimal) -> Decimal:
    result = a / b
    return result


def complement(a: Decimal) -> Decimal:
    return Decimal(1 - a) if a < 1 else Decimal(0)


def powUp(a: Decimal, b: Decimal) -> Decimal:
    return a ** b


class BalancerInputTooLargeError(AssertionError):
    pass


class BalancerOutputTooLargeError(AssertionError):
    pass


class ExchangeNotSupportedError(AssertionError):
    pass
