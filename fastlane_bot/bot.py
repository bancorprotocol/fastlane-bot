"""
Main integration point for the bot optimizer and other infrastructure.

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.

                      ,(&@(,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
               ,%@@@@@@@@@@,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.
          @@@@@@@@@@@@@@@@@&,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.
          @@@@@@@@@@@@@@@@@@/,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
          @@@@@@@@@@@@@@@@@@@,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
          @@@@@@@@@@@@@@@@@@@%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.
          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.
      (((((((((&@@@@@@@@@@@@@@@@@@@@@@@@@@@(,,,,,,,%@@@@@,
      (((((((((@@@@@@@@@@@@@@@@@@@@@@@@@@((((,,,,,,,#@@.
     ,((((((((#@@@@@@@@@@@/////////////((((((/,,,,,,,,
     *((((((((#@@@@@@@@@@@#,,,,,,,,,,,,/((((((/,,,,,,,,
     /((((((((#@@@@@@@@@@@@*,,,,,,,,,,,,(((((((*,,,,,,,,
     (((((((((%@@@@@@@@@@@@&,,,,,,,,,,,,/(((((((,,,,,,,,,.
    .(((((((((&@@@@@@@@@@@@@/,,,,,,,,,,,,((((((((,,,,,,,,,,
    *(((((((((@@@@@@@@@@@@@@@,,,,,,,,,,,,*((((((((,,,,,,,,,,
    /((((((((#@@@@@@@@@@@@@@@@/,,,,,,,,,,,((((((((/,,,,,,,,,,.
    (((((((((%@@@@@@@@@@@@@@@@@(,,,,,,,,,,*((((((((/,,,,,,,,,,,
    (((((((((%@@@@@@@@@@@@@@@@@@%,,,,,,,,,,(((((((((*,,,,,,,,,,,
    ,(((((((((&@@@@@@@@@@@@@@@@@@@&,,,,,,,,,*(((((((((*,,,,,,,,,,,.
    ((((((((((@@@@@@@@@@@@@@@@@@@@@@*,,,,,,,,((((((((((,,,,,,,,,,,,,
    ((((((((((@@@@@@@@@@@@@@@@@@@@@@@(,,,,,,,*((((((((((,,,,,,,,,,,,,
    (((((((((#@@@@@@@@@@@@&#(((((((((/,,,,,,,,/((((((((((,,,,,,,,,,,,,
    %@@@@@@@@@@@@@@@@@@((((((((((((((/,,,,,,,,*(((((((#&@@@@@@@@@@@@@.
    &@@@@@@@@@@@@@@@@@@#((((((((((((*,,,,,,,,,/((((%@@@@@@@@@@@@@%
     &@@@@@@@@@@@@@@@@@@%(((((((((((*,,,,,,,,,*(#@@@@@@@@@@@@@@*
     /@@@@@@@@@@@@@@@@@@@%((((((((((*,,,,,,,,,,,,,,,,,,,,,,,,,
     %@@@@@@@@@@@@@@@@@@@@&(((((((((*,,,,,,,,,,,,,,,,,,,,,,,,,,
     @@@@@@@@@@@@@@@@@@@@@@@((((((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,
    ,@@@@@@@@@@@@@@@@@@@@@@@@#((((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
    #@@@@@@@@@@@@@@@@@@@@@@@@@#(((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.
    &@@@@@@@@@@@@@@@@@@@@@@@@@@%((((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@&(((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
    (@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@((,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
"""
__VERSION__ = "3-b2.2"
__DATE__ = "20/June/2023"

import json
import os
from _decimal import Decimal
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, List, Dict, Tuple, Optional

from fastlane_bot.config import Config
from fastlane_bot.helpers import (
    TxRouteHandler,
    TxHelpers,
    TradeInstruction,
    Univ3Calculator,
    SolidlyV2StablePoolsNotSupported,
    add_wrap_or_unwrap_trades_to_route,
    split_carbon_trades,
    maximize_last_trade_per_tkn
)
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
from .config.constants import FLASHLOAN_FEE_MAP
from .events.interface import QueryInterface
from .modes.base import ArbitrageFinderBase
from .modes.pairwise_multi_all import ArbitrageFinderMultiPairwiseAll
from .modes.pairwise_multi_pol import ArbitrageFinderMultiPairwisePol
from .modes.triangle_multi import ArbitrageFinderTriangleMulti
from .modes.triangle_multi_complete import ArbitrageFinderTriangleMultiComplete
from .modes.triangle_bancor_v3_two_hop import ArbitrageFinderTriangleBancor3TwoHop
from .modes.base import get_prices_simple, custom_sort
from .utils import num_format, rand_item


@dataclass
class CarbonBot:
    """
    Base class for the business logic of the bot.

    Attributes
    ----------
    db: QueryInterface
        the database manager.
    tx_helpers: TxHelpers
        the tx-helpers utility.
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    db: QueryInterface = field(init=False)
    tx_helpers: TxHelpers = None
    ConfigObj: Config = None

    SCALING_FACTOR = 0.999

    def __post_init__(self):
        """
        The post init method.
        """

        if self.ConfigObj is None:
            self.ConfigObj = Config()

        if self.tx_helpers is None:
            self.tx_helpers = TxHelpers(cfg=self.ConfigObj)

        self.db = QueryInterface(ConfigObj=self.ConfigObj)
        self.RUN_FLASHLOAN_TOKENS = [*self.ConfigObj.CHAIN_FLASHLOAN_TOKENS.values()]

    def get_curves(self) -> CPCContainer:
        """
        Gets the curves from the database.

        Returns
        -------
        CPCContainer
            The container of curves.
        """
        self.db.refresh_pool_data()
        pools_and_tokens = self.db.get_pool_data_with_tokens()
        curves = []
        tokens = self.db.get_tokens()
        ADDRDEC = {t.address: (t.address, int(t.decimals)) for t in tokens}

        for p in pools_and_tokens:
            p.ADDRDEC = ADDRDEC
            try:
                curves += [
                    curve for curve in p.to_cpc()
                    if all(curve.params[tkn] not in self.ConfigObj.TAX_TOKENS for tkn in ['tknx_addr', 'tkny_addr'])
                ]
            except SolidlyV2StablePoolsNotSupported as e:
                self.ConfigObj.logger.debug(
                    f"[bot.get_curves] Solidly V2 stable pools not supported: {e}\n"
                )
            except NotImplementedError as e:
                self.ConfigObj.logger.error(
                    f"[bot.get_curves] Not supported: {e}\n"
                )
            except ZeroDivisionError as e:
                self.ConfigObj.logger.error(
                    f"[bot.get_curves] MUST FIX INVALID CURVE {p} [{e}]\n"
                )
            except CPC.CPCValidationError as e:
                self.ConfigObj.logger.error(
                    f"[bot.get_curves] MUST FIX INVALID CURVE {p} [{e}]\n"
                )
            except TypeError as e:
                self.ConfigObj.logger.error(
                    f"[bot.get_curves] MUST FIX DECIMAL ERROR CURVE {p} [{e}]\n"
                )
            except p.DoubleInvalidCurveError as e:
                self.ConfigObj.logger.error(
                    f"[bot.get_curves] MUST FIX DOUBLE INVALID CURVE {p} [{e}]\n"
                )
            except Univ3Calculator.DecimalsMissingError as e:
                self.ConfigObj.logger.error(
                    f"[bot.get_curves] MUST FIX DECIMALS MISSING [{e}]\n"
                )
            except Exception as e:
                # TODO: unexpected exception should possibly be raised
                self.ConfigObj.logger.error(
                    f"[bot.get_curves] MUST FIX UNEXPECTED ERROR converting pool to curve {p}\n[ERR={e}]\n\n"
                )

        return CPCContainer(curves)

    def _simple_ordering_by_src_token(
        self, best_trade_instructions_dic, best_src_token
    ):
        """
        Reorders a trade_instructions_dct so that all items where the best_src_token is the tknin are before others
        """
        src_token_instr = [
            x for x in best_trade_instructions_dic if x["tknin"] == best_src_token
        ]
        non_src_token_instr = [
            x
            for x in best_trade_instructions_dic
            if (x["tknin"] != best_src_token and x["tknout"] != best_src_token)
        ]
        src_token_end = [
            x for x in best_trade_instructions_dic if x["tknout"] == best_src_token
        ]
        ordered_trade_instructions_dct = (
            src_token_instr + non_src_token_instr + src_token_end
        )

        return ordered_trade_instructions_dct

    def _basic_scaling(self, best_trade_instructions_dic, best_src_token):
        """
        For items in the trade_instruction_dic scale the amtin by 0.999 if its the src_token
        """
        scaled_best_trade_instructions_dic = [
            dict(x.items()) for x in best_trade_instructions_dic
        ]
        for item in scaled_best_trade_instructions_dic:
            if item["tknin"] == best_src_token:
                item["amtin"] *= self.SCALING_FACTOR

        return scaled_best_trade_instructions_dic

    def _convert_trade_instructions(
        self, trade_instructions_dic: List[Dict[str, Any]]
    ) -> List[TradeInstruction]:
        """
        Converts the trade instructions dictionaries into `TradeInstruction` objects.

        Parameters
        ----------
        trade_instructions_dic: List[Dict[str, Any]]
            The trade instructions dictionaries.

        Returns
        -------
        List[Dict[str, Any]]
            The trade instructions.
        """
        return [
            TradeInstruction(**{
                **{k: v for k, v in ti.items() if k != "error"},
                "raw_txs": "[]",
                "pair_sorting": "",
                "ConfigObj": self.ConfigObj,
                "db": self.db,
                "strategy_id": self.db.get_pool(cid=ti["cid"].split('-')[0]).strategy_id
            })
            for ti in trade_instructions_dic if ti["error"] is None
        ]

    def _get_deadline(self, block_number) -> int:
        """
        Gets the deadline for a transaction.

        Returns
        -------
        int
            The deadline (as UNIX epoch).
        """
        if block_number is None:
            block_number = self.ConfigObj.w3.eth.block_number
        return self.ConfigObj.w3.eth.get_block(block_number).timestamp + self.ConfigObj.DEFAULT_BLOCKTIME_DEVIATION

    def get_arb_finder(self, arb_mode: str, flashloan_tokens, CCm) -> ArbitrageFinderBase:
        return {
            "multi_triangle": ArbitrageFinderTriangleMulti,
            "b3_two_hop": ArbitrageFinderTriangleBancor3TwoHop,
            "multi_pairwise_pol": ArbitrageFinderMultiPairwisePol,
            "multi_pairwise_all": ArbitrageFinderMultiPairwiseAll,
            "multi_triangle_complete": ArbitrageFinderTriangleMultiComplete,
        }[arb_mode](flashloan_tokens=flashloan_tokens, CCm=CCm, ConfigObj=self.ConfigObj)

    def run(
        self,
        *,
        flashloan_tokens: List[str] = None,
        CCm: CPCContainer = None,
        arb_mode: str = None,
        randomizer: int = 1,
        logging_path: str = None,
        replay_from_block: int = None,
    ):
        """
        Runs the bot.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens
        CCm: CPCContainer
            The complete market data container
        arb_mode: str
            The arbitrage mode
        randomizer: int
            The number of top arbitrage opportunities to randomly choose from
        logging_path: str
            The logging path
        replay_from_block: int
            The block number to start replaying from
        """

        if flashloan_tokens is None:
            flashloan_tokens = self.RUN_FLASHLOAN_TOKENS
        if CCm is None:
            CCm = self.get_curves()

        arb_finder = self.get_arb_finder(arb_mode, flashloan_tokens, CCm)
        arb_opps = arb_finder.find_arb_opps()

        if len(arb_opps) == 0:
            self.ConfigObj.logger.info("[bot.run] No eligible arb opportunities.")
            return

        self.ConfigObj.logger.info(f"[bot.run] Found {len(arb_opps)} eligible arb opportunities.")

        arb_opp = rand_item(list_of_items=arb_opps, num_of_items=randomizer)

        tx_hash, tx_receipt = self._handle_trade_instructions(CCm, arb_mode, arb_opp, replay_from_block)

        if tx_hash:
            tx_status = ["failed", "succeeded"][tx_receipt["status"]] if tx_receipt else "pending"
            tx_details = json.dumps(tx_receipt, indent=4) if tx_receipt else "no receipt"
            self.ConfigObj.logger.info(f"Arbitrage transaction {tx_hash} {tx_status}")

            if logging_path:
                filename = f"tx_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
                with open(os.path.join(logging_path, filename), "w") as f:
                    f.write(f"{tx_hash} {tx_status}: {tx_details}")

    def calculate_profit(
        self,
        CCm: CPCContainer,
        best_profit: Decimal,
        fl_token: str,
        flashloan_fee_amt: int = 0,
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate the actual profit in USD.

        Parameters
        ----------
        CCm: CPCContainer
            The container.
        best_profit: Decimal
            The best profit.
        fl_token: str
            The flashloan token.
        flashloan_fee_amt: int
            The flashloan fee amount.

        Returns
        -------
        Tuple[Decimal, Decimal]
            best_profit_gastkn, best_profit_usd.
        """
        self.ConfigObj.logger.debug(f"[bot.calculate_profit] best_profit, fl_token, flashloan_fee_amt: {best_profit, fl_token, flashloan_fee_amt}")
        sort_sequence = ['bancor_v2','bancor_v3'] + self.ConfigObj.UNI_V2_FORKS + self.ConfigObj.UNI_V3_FORKS

        flashloan_fee_amt_fl_token = Decimal(str(flashloan_fee_amt))
        if fl_token not in [self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS]:
            price_curves = get_prices_simple(CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, fl_token)
            sorted_price_curves = custom_sort(price_curves, sort_sequence, self.ConfigObj.CARBON_V1_FORKS)
            self.ConfigObj.logger.debug(f"[bot.calculate_profit sort_sequence] {sort_sequence}")
            self.ConfigObj.logger.debug(f"[bot.calculate_profit price_curves] {price_curves}")
            self.ConfigObj.logger.debug(f"[bot.calculate_profit sorted_price_curves] {sorted_price_curves}")
            if len(sorted_price_curves)>0:
                fltkn_gastkn_conversion_rate = sorted_price_curves[0][-1]
                flashloan_fee_amt_gastkn = Decimal(str(flashloan_fee_amt_fl_token)) / Decimal(str(fltkn_gastkn_conversion_rate))
                best_profit_gastkn = Decimal(str(best_profit)) / Decimal(str(fltkn_gastkn_conversion_rate)) - flashloan_fee_amt_gastkn
                self.ConfigObj.logger.debug(f"[bot.calculate_profit] GASTOKEN: {fltkn_gastkn_conversion_rate, best_profit_gastkn}")
            else:
                self.ConfigObj.logger.error(
                    f"[bot.calculate_profit] Failed to get conversion rate for {fl_token} and {self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS}. Raise"
                )
                raise
        else:
            best_profit_gastkn = best_profit - flashloan_fee_amt_fl_token

        try:
            price_curves_usd = get_prices_simple(CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, self.ConfigObj.STABLECOIN_ADDRESS)
            sorted_price_curves_usd = custom_sort(price_curves_usd, sort_sequence, self.ConfigObj.CARBON_V1_FORKS)
            self.ConfigObj.logger.debug(f"[bot.calculate_profit price_curves_usd] {price_curves_usd}")
            self.ConfigObj.logger.debug(f"[bot.calculate_profit sorted_price_curves_usd] {sorted_price_curves_usd}")
            usd_gastkn_conversion_rate = Decimal(str(sorted_price_curves_usd[0][-1]))
        except Exception:
            usd_gastkn_conversion_rate = Decimal("NaN")

        best_profit_usd = best_profit_gastkn * usd_gastkn_conversion_rate
        self.ConfigObj.logger.debug(f"[bot.calculate_profit] {'GASTOKEN', best_profit_gastkn, usd_gastkn_conversion_rate, best_profit_usd, 'USD'}")
        return best_profit_gastkn, best_profit_usd

    def _handle_trade_instructions(
        self,
        CCm: CPCContainer,
        arb_mode: str,
        arb_opp: dict,
        replay_from_block: int = None
    ) -> Tuple[Optional[str], Optional[dict]]:
        """
        Creates and executes the trade instructions
        
        This is the workhorse function that chains all the different actions that
        are necessary to create trade instructions and to ultimately execute them.
        
        Parameters
        ----------
        CCm: CPCContainer
            The container.
        arb_mode: str
            The arbitrage mode.
        arb_opp: dictionary
            The dictionary containing an arbitrage opportunity found by the Optimizer
        replay_from_block: int
            the block number to start replaying from (default: None)

        Returns
        -------
        - The hash of the transaction if submitted, None otherwise.
        - The receipt of the transaction if completed, None otherwise.
        """
        src_token = arb_opp["src_token"]
        trade_instructions_dic = arb_opp["trade_instructions_dic"]

        # Order the trade instructions
        ordered_trade_instructions_dct = self._simple_ordering_by_src_token(
            trade_instructions_dic, src_token
        )

        # Scale the trade instructions
        ordered_scaled_dcts = self._basic_scaling(
            ordered_trade_instructions_dct, src_token
        )

        # Convert the trade instructions
        ordered_trade_instructions_objects = self._convert_trade_instructions(
            ordered_scaled_dcts
        )

        # Create the tx route handler
        tx_route_handler = TxRouteHandler(
            trade_instructions=ordered_trade_instructions_objects
        )

        # Aggregate the carbon trades
        agg_trade_instructions = (
            tx_route_handler.aggregate_carbon_trades(ordered_trade_instructions_objects)
            if any(trade.is_carbon for trade in ordered_trade_instructions_objects)
            else ordered_trade_instructions_objects
        )

        # Calculate the trade instructions
        calculated_trade_instructions = tx_route_handler.calculate_trade_outputs(
            agg_trade_instructions
        )

        # Aggregate multiple Bancor V3 trades into a single trade
        calculated_trade_instructions = tx_route_handler.aggregate_bancor_v3_trades(
            calculated_trade_instructions
        )

        flashloan_struct = tx_route_handler.generate_flashloan_struct(
            trade_instructions_objects=calculated_trade_instructions
        )

        # Get the flashloan token
        fl_token = calculated_trade_instructions[0].tknin_address
        fl_token_symbol = calculated_trade_instructions[0].tknin_symbol
        fl_token_decimals = calculated_trade_instructions[0].tknin_decimals
        flashloan_amount_wei = int(calculated_trade_instructions[0].amtin_wei)
        flashloan_fee = FLASHLOAN_FEE_MAP.get(self.ConfigObj.NETWORK, 0)
        flashloan_fee_amt = flashloan_fee * (flashloan_amount_wei / 10**int(fl_token_decimals))

        flashloan_tkn_profit = tx_route_handler.calculate_trade_profit(
            calculated_trade_instructions
        )

        # Calculate the best profit
        best_profit_gastkn, best_profit_usd = self.calculate_profit(
            CCm, flashloan_tkn_profit, fl_token, flashloan_fee_amt
        )

        # Check if the best profit is greater than the minimum profit
        if best_profit_gastkn < self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN:
            self.ConfigObj.logger.info(
                f"[bot._handle_trade_instructions]:\n"
                f"- Expected profit: {best_profit_gastkn}\n"
                f"- Minimum profit:  {self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN}\n"
            )
            return None, None

        # Log the calculated arbitrage
        arb_info = [
            f"arb mode = {arb_mode}",
            f"gas profit = {num_format(best_profit_gastkn)}",
            f"usd profit = {num_format(best_profit_usd)}",
            f"flashloan token = {fl_token_symbol}",
            f"flashloan amount = {num_format(calculated_trade_instructions[0].amtin)}",
            f"flashloan profit = {num_format(flashloan_tkn_profit)}"
        ]
        arb_ti_info = [
            {
                "exchange": trade.exchange_name,
                "tkn_in": {trade.tknin_symbol: trade.tknin} if trade.tknin_symbol != trade.tknin else trade.tknin,
                "amt_in": num_format(trade.amtin),
                "tkn_out": {trade.tknout_symbol: trade.tknout} if trade.tknout_symbol != trade.tknout else trade.tknout,
                "amt_out": num_format(trade.amtout)
            }
            for trade in calculated_trade_instructions
        ]
        self.ConfigObj.logger.info(
            "\n".join(
                [
                    "[bot._handle_trade_instructions] calculated arbitrage:",
                    *[f"- {line}" for line in arb_info],
                    "- trade instructions:",
                    *[f"  {index + 1}. {line}" for index, line in enumerate(arb_ti_info)]
                ]
            )
        )

        # Split Carbon Orders
        split_calculated_trade_instructions = split_carbon_trades(
            cfg=self.ConfigObj,
            trade_instructions=calculated_trade_instructions
        )

        # Encode the trade instructions
        encoded_trade_instructions = tx_route_handler.custom_data_encoder(
            split_calculated_trade_instructions
        )

        # Get the deadline
        deadline = self._get_deadline(replay_from_block)

        # Get the route struct
        route_struct = [
            asdict(rs)
            for rs in tx_route_handler.get_route_structs(
                trade_instructions=encoded_trade_instructions, deadline=deadline
            )
        ]

        route_struct_processed = add_wrap_or_unwrap_trades_to_route(
            cfg=self.ConfigObj,
            flashloans=flashloan_struct,
            routes=route_struct,
            trade_instructions=split_calculated_trade_instructions,
        )

        maximize_last_trade_per_tkn(route_struct=route_struct_processed)

        # Log the flashloan details
        self.ConfigObj.logger.debug(
            f"[bot._handle_trade_instructions] Flashloan of {fl_token_symbol}, amount: {flashloan_amount_wei}"
        )
        self.ConfigObj.logger.debug(
            f"[bot._handle_trade_instructions] Flashloan token address: {fl_token}"
        )
        self.ConfigObj.logger.debug(
            f"[bot._handle_trade_instructions] Route Struct: \n {route_struct_processed}"
        )
        self.ConfigObj.logger.debug(
            f"[bot._handle_trade_instructions] Trade Instructions: \n {trade_instructions_dic}"
        )

        # Validate and submit the transaction
        return self.tx_helpers.validate_and_submit_transaction(
            route_struct=route_struct_processed,
            src_amt=flashloan_amount_wei,
            src_address=fl_token,
            expected_profit_gastkn=best_profit_gastkn,
            expected_profit_usd=best_profit_usd,
            flashloan_struct=flashloan_struct,
        )
