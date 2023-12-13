"""
Route handler for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.1.1"
__DATE__="02/May/2023"

import decimal
import math
from _decimal import Decimal
from dataclasses import dataclass, asdict
from typing import List, Any, Dict, Tuple

import eth_abi
import pandas as pd

from .tradeinstruction import TradeInstruction
from ..events.interface import Pool
from ..tools.cpc import T


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

    XCID_BANCOR_V2 = 0
    XCID_BANCOR_V3 = 1
    XCID_UNISWAP_V2 = 2
    XCID_UNISWAP_V3 = 3
    XCID_SUSHISWAP_V2 = 4
    XCID_SUSHISWAP_V1 = 5
    XCID_CARBON_V1 = 6
    XCID_BALANCER = 7
    XCID_CARBON_POL = 8
    XCID_PANCAKESWAP_V2 = 9
    XCID_PANCAKESWAP_V3 = 10

    platformId: int  # TODO: WHY IS THIS AN INT?
    sourceToken: str
    targetToken: str
    sourceAmount: int
    minTargetAmount: int
    deadline: int
    customAddress: str
    customInt: int
    customData: bytes
    # ConfigObj: Config
@dataclass
class TxRouteHandlerBase:
    __VERSION__=__VERSION__
    __DATE__=__DATE__


def maximize_last_trade_per_tkn(route_struct: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sets the source amount of the last trade to 0 per-token, ensuring that all tokens held will be used in the last trade.

    :param route_struct: the route struct object

    Returns:
    List[RouteStruct] the route struct object with the sourceAmount adjusted to 0 for each last-trade per token.

    """

    tkns_traded = []
    for j, trade in enumerate(reversed(route_struct)):
        idx = len(route_struct) - 1 - j
        if type(trade) == dict:
            if trade["sourceToken"] in tkns_traded:
                continue
            else:
                route_struct[idx]["sourceAmount"] = 0
                tkns_traded.append(trade["sourceToken"])
        elif type(trade) == RouteStruct:
            if trade.sourceToken in tkns_traded:
                continue
            else:
                route_struct[idx].sourceAmount = 0
                tkns_traded.append(trade.sourceToken)

    return route_struct


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
    __VERSION__=__VERSION__
    __DATE__=__DATE__

    trade_instructions: List[TradeInstruction]

    @property
    def exchange_ids(self) -> List[int]:
        """
        Returns
        """
        return [trade.platform_id for trade in self.trade_instructions]

    def __post_init__(self):
        self.contains_carbon = True
        self._validate_trade_instructions()
        self.ConfigObj = self.trade_instructions[0].ConfigObj

    def _validate_trade_instructions(self):
        """
        Validates the trade instructions.
        """
        if not self.trade_instructions:
            raise ValueError("No trade instructions found.")
        if len(self.trade_instructions) < 2:
            raise ValueError("Trade instructions must be greater than 1.")
        if sum([1 if self.trade_instructions[i]._is_carbon else 0 for i in range(len(self.trade_instructions))]) == 0:
            self.contains_carbon = False

    def is_wrapped_gas_token(self, address: str) -> bool:
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
        return address.lower() == self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS.lower()

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
                            "strategyId": int(trade["cid"].split("-")[0]),
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
                instr.custom_data = '0x'+str(encoded_data.hex())
                agg_trade_instructions[i] = instr
        return agg_trade_instructions

    @staticmethod
    def _abi_encode_data(
        idx_of_carbon_trades: List[int],
        trade_instructions: List[TradeInstruction],
    ) -> bytes:
        """
        Gets the custom data abi-encoded. Required for trades on Carbon. (abi-encoded)

        Parameters
        ----------
        idx_of_carbon_trades: List[int]
            The indices of the trades that are on Carbon.
        trade_instructions: List[TradeInstruction]
            The trade instructions.

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
        platform_id: int,
        custom_address: str = None,
        fee_float: Any = None,
        customData: Any = None,
        override_min_target_amount: bool = True,
        customInt: int = None,
        source_token: str = None,
        source_amount: Decimal = None,

    ) -> RouteStruct:
        """
        Converts the trade instructions into the variables needed to instantiate the `TxSubmitHandler` class.

        Parameters
        ----------
        min_target_amount: Decimal
            The minimum target amount.
        deadline: int
            The deadline.
        target_address: str
            The target address.
        platform_id: int
            The exchange id.
        custom_address: str
            The custom address.
        fee_float: Any
            The fee_float.
        customData: Any
            The custom data.
        override_min_target_amount: bool
            Whether to override the minimum target amount.
        sourceToken: str
            The source token of the trade. V2 routes only.
        sourceAmount: float,
            The source token amount for the trade. V2 routes only.
        Returns
        -------
        RouteStruct
            The route struct.
        """
        target_address = self.wrapped_gas_token_to_native(target_address)
        target_address = self.ConfigObj.w3.toChecksumAddress(target_address)
        source_token = self.wrapped_gas_token_to_native(source_token)
        source_token = self.ConfigObj.w3.toChecksumAddress(source_token)
        fee_customInt_specifier = int(Decimal(fee_float)*Decimal(1000000)) if platform_id != 7 else int(eval(fee_float))

        return RouteStruct(
            platformId=platform_id,
            targetToken=target_address,
            sourceToken=source_token,
            sourceAmount=int(source_amount),
            minTargetAmount=int(min_target_amount),
            deadline=deadline,
            customAddress=custom_address,
            customInt=fee_customInt_specifier,
            customData=customData,
        )

    def get_wrap_or_unwrap_native_gas_tkn_struct(self, deadline: int, wrap: bool, source_amount: int = 0):
        """
        This function provides a trade struct to wrap or unwrap the native gas token.

        :param deadline: the deadline
        :param wrap: if True, wrap the native gas token, else unwrap the native gas token
        :param source_amount: the number of tokens to wrap or unwrap. If 0, this will wrap or unwrap the current balance of tokens.

        returns: RouteStruct

        """
        return RouteStruct(
            platformId=self.ConfigObj.PLATFORM_ID_WRAP_UNWRAP,
            targetToken=self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS if wrap else self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS,
            sourceToken=self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS if wrap else self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS,
            sourceAmount=int(source_amount),
            minTargetAmount=int(source_amount),
            deadline=deadline,
            customAddress=self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS if wrap else self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS,
            customInt=0,
            customData="0x",
        )

    def add_wrap_or_unwrap_trades_to_route(self, trade_instructions: List[TradeInstruction], route_struct: List[Dict], flashloan_struct: List
    ) -> List[Dict]:
        """
        Adds native token wrap and unwrap trades as necessary to the route struct.
        :param trade_instructions: the processed trade instructions
        :param route_struct: the processed route struct
        :param flashloan_struct: the processed route struct

        returns: List of RouteStruct
        """

        # balancer = {"platformId": 7, "sourceTokens": [], "sourceAmounts": []}

        flashloan_native_gas_token = False
        flashloan_wrapped_gas_token = False

        # Check if we are flashloaning wrapped or native gas tokens
        for flash in flashloan_struct:
            if self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS in flash["sourceTokens"]:
                flashloan_wrapped_gas_token = True
            if self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS in flash["sourceTokens"]:
                flashloan_native_gas_token = True
        # Ensure we didn't try to flashloan wrapped & native gas token
        assert not flashloan_wrapped_gas_token or not flashloan_native_gas_token, f"Cannot flashloan both wrapped & native gas tokens! Flashloan struct = {flashloan_struct}"

        new_route_struct = []
        for idx, route in enumerate(route_struct):
            # Ensure tokens are set according to the pool's token
            if route["platformId"] == self.ConfigObj.PLATFORM_ID_WRAP_UNWRAP:
                continue
            if trade_instructions[idx].tknin_is_native:
                route["sourceToken"] = self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS
            elif trade_instructions[idx].tknin_is_wrapped:
                route["sourceToken"] = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
            if trade_instructions[idx].tknout_is_native:
                route["targetToken"] = self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS
            elif trade_instructions[idx].tknout_is_wrapped:
                route["targetToken"] = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS

            if idx == 0:
                if flashloan_wrapped_gas_token and trade_instructions[idx].tknin_is_native:
                    # First trade, we took flashloan of wrapped tokens but need Native tokens, add unwrap
                    new_route_struct.append(asdict(self.get_wrap_or_unwrap_native_gas_tkn_struct(deadline=route["deadline"],
                                                                                           wrap=False,
                                                                                           source_amount=route["sourceAmount"])))

                elif flashloan_native_gas_token and trade_instructions[idx].tknin_is_wrapped:
                    # First trade, we took flashloan of wrapped tokens but need Native tokens, add unwrap
                    new_route_struct.append(asdict(self.get_wrap_or_unwrap_native_gas_tkn_struct(deadline=route["deadline"],
                                                                                           wrap=True,
                                                                                           source_amount=route["sourceAmount"])))
                new_route_struct.append(route)
            # Received wrapped tokens from last trade, native tokens going into next trade
            elif trade_instructions[idx - 1].tknout_is_wrapped and trade_instructions[idx].tknin_is_native:
                new_route_struct.append(asdict(self.get_wrap_or_unwrap_native_gas_tkn_struct(deadline=route["deadline"],
                                                                                       wrap=False,
                                                                                       source_amount=route["sourceAmount"])))
                new_route_struct.append(route)
            # Received native tokens from last trade, wrapped going into next trade
            elif trade_instructions[idx - 1].tknout_is_native and trade_instructions[idx].tknin_is_wrapped:
                new_route_struct.append(asdict(self.get_wrap_or_unwrap_native_gas_tkn_struct(deadline=route["deadline"],
                                                                                       wrap=True,
                                                                                       source_amount=route["sourceAmount"])))
                new_route_struct.append(route)
            else:
                new_route_struct.append(route)
            if idx == len(route_struct) - 1:
                # Flashloaned native, get wrapped out of last trade, convert to native
                if flashloan_native_gas_token and trade_instructions[idx].tknout_is_wrapped:
                    new_route_struct.append(asdict(self.get_wrap_or_unwrap_native_gas_tkn_struct(deadline=route["deadline"],
                                                                                           wrap=False,
                                                                                           source_amount=0)))

                # Flashloaned wrapped, get native out of last trade, convert to wrapped
                elif flashloan_wrapped_gas_token and trade_instructions[idx].tknout_is_native:
                    new_route_struct.append(asdict(self.get_wrap_or_unwrap_native_gas_tkn_struct(deadline=route["deadline"],
                                                                                           wrap=True,
                                                                                           source_amount=0)))
        return new_route_struct


    def get_route_structs(
        self, trade_instructions: List[TradeInstruction]=None, deadline: int=None
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

        pools = [
            self._cid_to_pool(trade_instruction.cid, trade_instruction.db)
            for trade_instruction in trade_instructions
        ]
        try:
            fee_float = [pools[idx].fee_float for idx, _ in enumerate(trade_instructions)]
        except:
            fee_float = [0 for idx, _ in enumerate(trade_instructions)]

        return [
            self.to_route_struct(
                min_target_amount=Decimal(str(trade_instructions[idx].amtout_wei)),
                deadline=deadline,
                target_address=trade_instructions[idx].tknout_address,
                custom_address=self.get_custom_address(pool=pools[idx]),
                platform_id=trade_instructions[idx].platform_id,
                fee_float=fee_float[idx] if trade_instructions[idx].platform_id != 7 else pools[idx].anchor,
                customData=trade_instructions[idx].custom_data,
                override_min_target_amount=True,
                source_token=trade_instructions[idx].tknin_address,
                source_amount=Decimal(str(trade_instructions[idx].amtin_wei)),
            )
            for idx, instructions in enumerate(trade_instructions)
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
        elif pool.exchange_name in self.ConfigObj.CARBON_V1_FORKS:
            return self.ConfigObj.CARBON_CONTROLLER_ADDRESS
        elif pool.exchange_name in self.ConfigObj.UNI_V3_FORKS:
            return self.ConfigObj.UNI_V3_ROUTER_MAPPING[pool.exchange_name]
        else:
            return pool.tkn0_address


    def generate_flashloan_struct(self, trade_instructions_objects: List[TradeInstruction]) -> List:
        """
        Generates the flashloan struct for submitting FlashLoanAndArbV2 transactions
        :param trade_instructions_objects: a list of TradeInstruction objects

        :return:
            int
        """
        return self._get_flashloan_struct(trade_instructions_objects=trade_instructions_objects)

    def _get_flashloan_platform_id(self, tkn: str) -> int:
        """
        Returns the platform ID to take the flashloan from
        :param tkn: str

        :return:
            int
        """

        if self.ConfigObj.NETWORK not in ["ethereum", "tenderly"]:
            return 7

        # Using Bancor V3 to flashloan BNT, ETH, WBTC, LINK, USDC, USDT
        if tkn in [self.ConfigObj.BNT_ADDRESS, self.ConfigObj.ETH_ADDRESS, self.ConfigObj.WBTC_ADDRESS, self.ConfigObj.LINK_ADDRESS, self.ConfigObj.BNT_KEY, self.ConfigObj.ETH_KEY, self.ConfigObj.WBTC_KEY, self.ConfigObj.LINK_KEY]:
            return 2
        else:
            return 7

    def _get_flashloan_struct(self, trade_instructions_objects: List[TradeInstruction]) -> List:
        """
        Turns an object containing trade instructions into a struct with flashloan tokens and amounts ready to send to the smart contract.
        :param flash_tokens: an object containing flashloan tokens in the format {tkn: {"tkn": tkn_address, "flash_amt": tkn_amt}}
        """
        flash_tokens = self._extract_single_flashloan_token(trade_instructions=trade_instructions_objects)
        flashloans = []
        balancer = {"platformId": 7, "sourceTokens": [], "sourceAmounts": []}
        has_balancer = False
        for tkn in flash_tokens.keys():
            platform_id = self._get_flashloan_platform_id(tkn)
            source_token = flash_tokens[tkn]["tkn"]
            source_amounts = abs(flash_tokens[tkn]["flash_amt"])
            if platform_id == 7:
                has_balancer = True
                balancer["sourceTokens"].append(source_token)
                balancer["sourceAmounts"].append(source_amounts)
            else:
                source_token = self.wrapped_gas_token_to_native(source_token)
                flashloans.append(
                    {"platformId": platform_id, "sourceTokens": [source_token], "sourceAmounts": [source_amounts]})
        if has_balancer:
            flashloans.append(balancer)

        return flashloans

    def wrapped_gas_token_to_native(self, tkn: str):
        """
        Checks if a Token is a wrapped gas token and converts it to the native gas token.

        This is only relevant on the Ethereum network

        :param tkn: the token address

        returns:
        the token address
        """

        if self.ConfigObj.NETWORK not in ["ethereum", "tenderly"]:
            return tkn

        if tkn in [self.ConfigObj.WRAPPED_GAS_TOKEN_KEY, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS]:
            return self.ConfigObj.NATIVE_GAS_TOKEN_KEY if tkn == self.ConfigObj.WRAPPED_GAS_TOKEN_KEY else self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS
        else:
            return tkn

    def _extract_single_flashloan_token(self, trade_instructions: List[TradeInstruction]) -> Dict:
        """
        Generate a flashloan tokens and amounts.
        :param trade_instructions: A list of trade instruction objects
        """

        if self.ConfigObj.ARB_CONTRACT_VERSION >= 10:
            tknin_key = None
            tknin_address = None
            if trade_instructions[0].tknin_is_native:
                tknin_key = self.ConfigObj.NATIVE_GAS_TOKEN_KEY
                tknin_address = self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS
            elif trade_instructions[0].tknin_is_wrapped:
                tknin_key = self.ConfigObj.WRAPPED_GAS_TOKEN_KEY
                tknin_address = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
            else:
                tknin_key = trade_instructions[0].tknin_key
                tknin_address = trade_instructions[0].tknin_address
            assert  tknin_key is not None and tknin_address is not None, f"routehandler _extract_single_flashloan_token, tknin_key is {tknin_key} and tknin_address is {tknin_address}, must not be None"
            flash_tokens = {
                tknin_key :
                {
                "tkn": tknin_address,
                "flash_amt": trade_instructions[0].amtin_wei,
                "decimals": trade_instructions[0].tknin_decimals}
            }
        else:
            flash_tokens = {self.wrapped_gas_token_to_native(trade_instructions[0].tknin_key): {
                "tkn": self.wrapped_gas_token_to_native(trade_instructions[0]._tknin_address),
                "flash_amt": trade_instructions[0].amtin_wei,
                "decimals": trade_instructions[0].tknin_decimals}}
        return flash_tokens

    def _extract_flashloan_tokens(self, trade_instructions: List[TradeInstruction]) -> Dict:
        """
        Generate a list of the flashloan tokens and amounts.
        :param trade_instructions: A list of trade instruction objects
        """
        token_change = {}
        flash_tokens = {}
        for trade in trade_instructions:
            tknin_key = self.wrapped_gas_token_to_native(trade.tknin_key)
            tknout_key = self.wrapped_gas_token_to_native(trade.tknout_key)

            token_change[tknin_key] = {"tkn": tknin_key, "amtin": 0, "amtout": 0, "balance": 0}
            token_change[tknout_key] = {"tkn": tknout_key, "amtin": 0, "amtout": 0, "balance": 0}

        for trade in trade_instructions:
            tknin_key = self.wrapped_gas_token_to_native(trade.tknin_key)
            tknout_key = self.wrapped_gas_token_to_native(trade.tknout_key)

            token_change[tknin_key]["amtin"] = token_change[tknin_key]["amtin"] + trade.amtin_wei
            token_change[tknin_key]["balance"] = token_change[tknin_key]["balance"] - trade.amtin_wei
            token_change[tknout_key]["amtout"] = token_change[tknout_key]["amtout"] + trade.amtout_wei
            token_change[tknout_key]["balance"] = token_change[tknout_key]["balance"] + trade.amtout_wei

            if token_change[tknin_key]["balance"] < 0:
                flash_tokens[tknin_key] = {"tkn": trade._tknin_address, "flash_amt": token_change[tknin_key]["amtin"],
                                           "decimals": trade.tknin_decimals}

        return flash_tokens

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
        return route_struct

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
                if trade.exchange_name == "bancor_v3" and calculated_trade_instructions[idx - 1].exchange_name == "bancor_v3":
                    trade_before = calculated_trade_instructions[idx - 1]
                    # This checks for a two-hop trade through BNT and combines them
                    if trade_before.tknout_key == "BNT-FF1C" and trade.tknin_key == "BNT-FF1C":
                        new_trade_instruction = TradeInstruction(ConfigObj=trade.ConfigObj, cid=trade_before.cid,
                                                                 amtin=trade_before.amtin, amtout=trade.amtout,
                                                                 tknin=trade_before.tknin_key, tknout=trade.tknout_key,
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
                "cid": newdf.cid.values[0],
                "tknin": newdf.tknin.values[0],
                "amtin": newdf.amtin.sum(),
                "_amtin_wei": newdf._amtin_wei.sum(),
                "tknout": newdf.tknout.values[0],
                "amtout": newdf.amtout.sum(),
                "_amtout_wei": newdf._amtout_wei.sum(),
                "raw_txs": str(newdf.to_dict(orient="records")),
                "ConfigObj" : config_object,
                "db" : db,
            }
            for min_index, newdf in result}

        new_trade_instructions_carbons.update(new_trade_instructions_nocarbons)
        agg_trade_instructions = []
        for i in sorted(list(new_trade_instructions_carbons.keys())):
            agg_trade_instructions += [TradeInstruction(**new_trade_instructions_carbons[i])]
        return agg_trade_instructions

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

        price_next = Decimal(str(math.floor((
            int(liquidity * self.ConfigObj.Q96 * sqrt_price)
            / int(liquidity * self.ConfigObj.Q96 + amount_in * decimal_tkn0_modifier * sqrt_price)))
        ))
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
        result = (((liquidity * self.ConfigObj.Q96 * ((((amount_in * decimal_tkn1_modifier * self.ConfigObj.Q96) / liquidity) + sqrt_price) - sqrt_price) / (
           (((amount_in * decimal_tkn1_modifier * self.ConfigObj.Q96) / liquidity) + sqrt_price)) / (
               sqrt_price)) / decimal_tkn0_modifier))

        return result
        #amount = amount_in * decimal_tkn1_modifier * (Decimal(str(1)) - fee)
        #
        # price_diff = Decimal((amount_in * decimal_tkn1_modifier * self.ConfigObj.Q96) / liquidity)
        # price_next = Decimal(sqrt_price + price_diff)
        #
        # print(f"p_next: {price_next}")
        # amount_out = self._calc_amount0(liquidity, price_next, sqrt_price) / self.ConfigObj.Q96
        #
        # print(f"Equation result = {result}, calc0 result={amount_out / decimal_tkn0_modifier}")
        #
        # return Decimal(amount_out / decimal_tkn0_modifier)

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
        tkn_0_key: str,
        tkn_1_key: str
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
        assert tkn_in == tkn_0_key or tkn_out == tkn_0_key, f"Uniswap V3 swap token mismatch, tkn_in: {tkn_in}, tkn_0_key: {tkn_0_key}, tkn_1_key: {tkn_1_key}"
        assert tkn_in == tkn_1_key or tkn_out == tkn_1_key, f"Uniswap V3 swap token mismatch, tkn_in: {tkn_in}, tkn_0_key: {tkn_0_key}, tkn_1_key: {tkn_1_key}"

        liquidity = Decimal(str(liquidity))
        fee = Decimal(str(fee))
        sqrt_price = Decimal(str(sqrt_price))
        decimal_tkn0_modifier = Decimal(str(decimal_tkn0_modifier))
        decimal_tkn1_modifier = Decimal(str(decimal_tkn1_modifier))

        #print(f"[_calc_uniswap_v3_output] tkn_in={tkn_in}, tkn_0_key={tkn_0_key}, tkn_1_key={tkn_1_key}, tkn0_in={tkn_in == tkn_0_key}, liquidity={liquidity}, fee={fee}, sqrt_price={sqrt_price}, decimal_tkn0_modifier={decimal_tkn0_modifier}, decimal_tkn1_modifier={decimal_tkn1_modifier}")

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
            (tkns_out * z**2) / ((A * y + B * z) * (A * y + B * z - A * tkns_out))
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
            / (tkns_in * (B * A * z + A**2 * y) + z**2)
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
        amount_in = Decimal(str(amount_in))

        tkn0_key = curve.pair_name.split("/")[0]
        tkn1_key = curve.pair_name.split("/")[1]

        if self.ConfigObj.NETWORK in "ethereum":
            tkn0_key = "WETH-6Cc2" if tkn0_key == "ETH-EEeE" and tkn_in == "WETH-6Cc2" else tkn0_key
            tkn1_key = "WETH-6Cc2" if tkn1_key == "ETH-EEeE" and tkn_in == "WETH-6Cc2" else tkn1_key

        #print(f"[_calc_carbon_output] tkn0_key={tkn0_key}, tkn1_key={tkn1_key}, ")

        assert tkn_in == tkn0_key or tkn_in == tkn1_key, f"Token in: {tkn_in} does not match tokens in Carbon Curve: {tkn0_key} & {tkn1_key}"

        #print(f"[_calc_carbon_output] tkn0_key={tkn0_key}, tkn1_key={tkn1_key}, tkn_int={tkn_in}, using curve0={tkn_in == tkn1_key}")
        y, z, A, B = (
            (curve.y_0, curve.z_0, curve.A_0, curve.B_0)
            if tkn_in == tkn1_key
            else (curve.y_1, curve.z_1, curve.A_1, curve.B_1)
        )

        if A is None:
            A = 0

        #print('[_calc_carbon_output] before decode: ', y, z, A, B)
        A = self.decode_decimal_adjustment(value=Decimal(str(self.decode(A))), tkn_in_decimals=tkn_in_decimals, tkn_out_decimals=tkn_out_decimals)
        B = self.decode_decimal_adjustment(value=Decimal(str(self.decode(B))), tkn_in_decimals=tkn_in_decimals, tkn_out_decimals=tkn_out_decimals)
        y = Decimal(y) / Decimal("10") ** Decimal(str(tkn_out_decimals))
        z = Decimal(z) / Decimal("10") ** Decimal(str(tkn_out_decimals))
        #print('[_calc_carbon_output] after decode: ', y, z, A, B)
        assert y > 0, f"Trade incoming to empty Carbon curve: {curve}"

        #print(f"[_calc_carbon_output] Carbon curve decoded: {y, z, A, B}, fee = {Decimal(curve.fee)}, amount_in={amount_in}")

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
        tkn_in_balance = Decimal(str(curve.get_token_balance(tkn=tkn_in))) / 10 ** Decimal(str(curve.get_token_decimals(tkn=tkn_in)))
        tkn_out_weight = Decimal(str(curve.get_token_weight(tkn=tkn_out)))
        tkn_out_balance = Decimal(str(curve.get_token_balance(tkn=tkn_out))) / 10 ** Decimal(str(curve.get_token_decimals(tkn=tkn_out)))
        self.ConfigObj.logger.debug(f"[routehandler.py _calc_balancer_output] tknin {tkn_in} weight: {tkn_in_weight}, tknout {tkn_out} tknout weight: {tkn_out_weight}")


        # Extract trade fee from amount in
        fee = Decimal(str(amount_in)) * Decimal(str(curve.fee_float))
        amount_in = amount_in - fee

        if amount_in > (tkn_in_balance * Decimal("0.3")):
            raise BalancerInputTooLargeError("Balancer has a hard constraint that amount in must be less than 30% of the pool balance of tkn in, making this trade invalid.")

        amount_out = self._calc_balancer_out_given_in(balance_in=tkn_in_balance, weight_in=tkn_in_weight, balance_out=tkn_out_balance, weight_out=tkn_out_weight, amount_in=amount_in)
        if amount_out > (tkn_out_balance * Decimal("0.3")):
            raise BalancerOutputTooLargeError("Balancer has a hard constraint that the amount out must be less than 30% of the pool balance of tkn out, making this trade invalid.")

        #amount_in = (1 - Decimal(str(curve.fee_float))) * Decimal(str(amount_in))
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

    @staticmethod
    def _calc_balancer_input_given_output(balance_in: Decimal,
                                          weight_in: Decimal,
                                          balance_out: Decimal,
                                          weight_out: Decimal,
                                          amount_out: Decimal):
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

        base = divUp(balance_out, (balance_out - amount_out))
        exponent = divUp(weight_out, weight_in)
        power = powUp(base, exponent)
        ratio = power - Decimal(1)
        result = mulUp(balance_in, ratio)
        return result

    def _solve_trade_output(
        self, curve: Pool, trade: TradeInstruction, amount_in: Decimal = None
    ) -> Tuple[Decimal, Decimal, int, int]:

        if not isinstance(trade, TradeInstruction):
            raise Exception("trade in must be a TradeInstruction object.")

        if curve.exchange_name != "balancer":
            tkn0_key = curve.pair_name.split("/")[0]
            tkn1_key = curve.pair_name.split("/")[1]
            tkn0_decimals = int(trade.db.get_token(key=tkn0_key).decimals)
            tkn1_decimals = int(trade.db.get_token(key=tkn1_key).decimals)
            if self.ConfigObj.NETWORK in ["ethereum", "tenderly"]:
                tkn0_key = "WETH-6Cc2" if tkn0_key == "ETH-EEeE" and (trade.tknin_key == "WETH-6Cc2" or trade.tknout_key == "WETH-6Cc2") else tkn0_key
                tkn1_key = "WETH-6Cc2" if tkn1_key == "ETH-EEeE" and (trade.tknin_key == "WETH-6Cc2" or trade.tknout_key == "WETH-6Cc2") else tkn1_key

            assert tkn0_key == trade.tknin_key or tkn0_key == trade.tknout_key, f"[_solve_trade_output] tkn0_key {tkn0_key} !=  trade.tknin_key {trade.tknin_key} or trade.tknout_key {trade.tknout_key}"
            assert tkn1_key == trade.tknin_key or tkn1_key == trade.tknout_key, f"[_solve_trade_output] tkn1_key {tkn1_key} !=  trade.tknin_key {trade.tknin_key} or trade.tknout_key {trade.tknout_key}"
            assert tkn0_key != tkn1_key, f"[_solve_trade_output] tkn0_key == tkn_1_key {tkn0_key}, {tkn1_key}"

        else:
            tokens = curve.get_tokens
            assert trade.tknin_key in tokens, f"[_solve_trade_output] trade.tknin_key {trade.tknin_key} not in Balancer curve tokens: {tokens}"
            assert trade.tknout_key in tokens, f"[_solve_trade_output] trade.tknout_key {trade.tknout_key} not in Balancer curve tokens: {tokens}"

        tkn_in_decimals = int(trade.db.get_token(key=trade.tknin_key).decimals)
        tkn_out_decimals = int(trade.db.get_token(key=trade.tknout_key).decimals)

        amount_in = TradeInstruction._quantize(amount_in, tkn_in_decimals)

        if curve.exchange_name in self.ConfigObj.UNI_V3_FORKS:
            amount_out = self._calc_uniswap_v3_output(
                tkn_in=trade.tknin_key,
                tkn_out=trade.tknout_key,
                amount_in=amount_in,
                fee=Decimal(curve.fee_float),
                liquidity=curve.liquidity,
                sqrt_price=curve.sqrt_price_q96,
                decimal_tkn0_modifier=Decimal(10**tkn0_decimals),
                decimal_tkn1_modifier=Decimal(10**tkn1_decimals),
                tkn_0_key=tkn0_key,
                tkn_1_key=tkn1_key
            )
        elif curve.exchange_name == self.ConfigObj.CARBON_V1_NAME or curve.exchange_name == self.ConfigObj.BANCOR_POL_NAME:
            amount_in, amount_out = self._calc_carbon_output(
                            curve=curve, tkn_in=trade.tknin_key, tkn_in_decimals=tkn_in_decimals, tkn_out_decimals=tkn_out_decimals, amount_in=amount_in
                        )
        elif curve.exchange_name == self.ConfigObj.BALANCER_NAME:
            amount_out = self._calc_balancer_output(curve=curve, tkn_in=trade.tknin_key, tkn_out=trade.tknout_key, amount_in=amount_in)

        else:
            tkn0_amt, tkn1_amt = (
                (curve.tkn0_balance, curve.tkn1_balance)
                if trade.tknin_key == tkn0_key
                else (curve.tkn1_balance, curve.tkn0_balance)
            )
            tkn0_dec = tkn0_decimals if trade.tknin_key == tkn0_key else tkn1_decimals
            tkn1_dec = tkn1_decimals if trade.tknout_key == tkn1_key else tkn0_decimals

            tkn0_amt = self._from_wei_to_decimals(tkn0_amt, tkn0_dec)
            tkn1_amt = self._from_wei_to_decimals(tkn1_amt, tkn1_dec)
            #print(f"[_solve_trade_output] constant product solve: tkn0_amt={tkn0_amt}, tkn1_amt={tkn1_amt}, tkn0_dec={tkn0_dec}, tkn1_dec={tkn1_dec}, tkn_in={trade.tknin_key}, tkn_out={trade.tknout_key} ,tkn0_key={tkn0_key}, tkn1_key={tkn1_key}")

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
        flt = trade_instructions[0].tknin_key

        for trade in trade_instructions:
            if trade.tknin_key == flt:
                sum_in += abs(trade.amtin)
            elif trade.tknout_key == flt:
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
            if trade.amtin <=0:
                trade_instructions.pop(idx)
                continue
            if trade.raw_txs != "[]":
                data = eval(trade.raw_txs)
                total_out = 0
                total_in = 0
                total_in_wei = 0
                total_out_wei = 0
                expected_in = trade_instructions[idx].amtin

                remaining_tkn_in = Decimal(str(next_amount_in))

                for tx in data:
                    try:
                        tx["percent_in"] = Decimal(str(tx["amtin"]))/Decimal(str(expected_in))
                    except decimal.InvalidOperation:
                        tx["percent_in"] = 0
                        # total_percent += tx["amtin"]/expected_in
                        self.ConfigObj.logger.warning(f"[calculate_trade_outputs] Invalid operation: {tx['amtin']}/{expected_in}")

                last_tx = len(data) - 1

                for _idx, tx in enumerate(data):
                    cid = tx["cid"]
                    cid = cid.split("-")[0]
                    tknin_key = tx["tknin"]

                    _next_amt_in = Decimal(str(next_amount_in)) * tx["percent_in"]
                    if _next_amt_in > remaining_tkn_in:
                        _next_amt_in = remaining_tkn_in


                    if _idx == last_tx:
                        if _next_amt_in < remaining_tkn_in:
                            _next_amt_in = remaining_tkn_in

                    curve = trade_instructions[idx].db.get_pool(cid=cid)
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
                        "tknin": tx["tknin"],
                        "amtin": amount_in,
                        "_amtin_wei": amount_in_wei,
                        "tknout": tx["tknout"],
                        "amtout": amount_out,
                        "_amtout_wei": amount_out_wei,
                    }
                    raw_txs_lst.append(raw_txs)

                    remaining_tkn_in = TradeInstruction._quantize(amount=remaining_tkn_in, decimals=trade.tknin_decimals)
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

    def _cid_to_pool(self, cid: str, db: any) -> Pool:
        return db.get_pool(cid=cid)


def mulUp(a: Decimal, b: Decimal) -> Decimal:
    return a * b


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


def powDown(a: Decimal, b: Decimal) -> Decimal:
    return a ** b

class BalancerInputTooLargeError(AssertionError):
    pass
class BalancerOutputTooLargeError(AssertionError):
    pass
