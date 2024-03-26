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

import random
import json
import os
from _decimal import Decimal
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Generator, List, Dict, Tuple, Any, Callable
from typing import Optional

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
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
from .config.constants import FLASHLOAN_FEE_MAP
from .events.interface import QueryInterface
from .modes.pairwise_multi import FindArbitrageMultiPairwise
from .modes.pairwise_multi_all import FindArbitrageMultiPairwiseAll
from .modes.pairwise_multi_pol import FindArbitrageMultiPairwisePol
from .modes.pairwise_single import FindArbitrageSinglePairwise
from .modes.triangle_multi import ArbitrageFinderTriangleMulti
from .modes.triangle_single import ArbitrageFinderTriangleSingle
from .modes.triangle_bancor_v3_two_hop import ArbitrageFinderTriangleBancor3TwoHop
from .utils import num_format


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

    ARB_FINDER = {
        "single": FindArbitrageSinglePairwise,
        "multi": FindArbitrageMultiPairwise,
        "triangle": ArbitrageFinderTriangleSingle,
        "multi_triangle": ArbitrageFinderTriangleMulti,
        "b3_two_hop": ArbitrageFinderTriangleBancor3TwoHop,
        "multi_pairwise_pol": FindArbitrageMultiPairwisePol,
        "multi_pairwise_all": FindArbitrageMultiPairwiseAll,
    }

    class NoArbAvailable(Exception):
        pass

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
        if best_trade_instructions_dic is None:
            raise self.NoArbAvailable(f"No arb available for token {best_src_token}")
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

        tx_in_count = len(src_token_instr)
        return ordered_trade_instructions_dct, tx_in_count

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
        block_number = (
            self.ConfigObj.w3.eth.block_number if block_number is None else block_number
        )
        return (
            self.ConfigObj.w3.eth.get_block(block_number).timestamp
            + self.ConfigObj.DEFAULT_BLOCKTIME_DEVIATION
        )

    @classmethod
    def _get_arb_finder(cls, arb_mode: str) -> Callable:
        return cls.ARB_FINDER[arb_mode]

    def _find_arbitrage(
        self,
        flashloan_tokens: List[str],
        CCm: CPCContainer,
        arb_mode: str,
        randomizer: int
    ) -> dict:
        arb_finder = self._get_arb_finder(arb_mode)
        random_mode = arb_finder.AO_CANDIDATES if randomizer else None
        finder = arb_finder(
            flashloan_tokens=flashloan_tokens,
            CCm=CCm,
            mode="bothin",
            result=random_mode,
            ConfigObj=self.ConfigObj,
        )
        return {"finder": finder, "r": finder.find_arbitrage()}

    def _run(
        self,
        flashloan_tokens: List[str],
        CCm: CPCContainer,
        *,
        arb_mode: str,
        randomizer: int,
        data_validator=False,
        logging_path: str = None,
        replay_mode: bool = False,
        replay_from_block: int = None,
    ):
        """
        Runs the bot.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The tokens to flashloan.
        CCm: CPCContainer
            The container.
        arb_mode: str
            The arbitrage mode.
        randomizer: int
            randomizer (int): The number of arb opportunities to randomly pick from, sorted by expected profit.
        data_validator: bool
            If extra data validation should be performed
        logging_path: str
            the logging path (default: None)
        replay_mode: bool
            whether to run in replay mode (default: False)
        replay_from_block: int
            the block number to start replaying from (default: None)

        """
        arbitrage = self._find_arbitrage(flashloan_tokens=flashloan_tokens, CCm=CCm, arb_mode=arb_mode, randomizer=randomizer)
        finder, r = [arbitrage[key] for key in ["finder", "r"]]

        if r is None or len(r) == 0:
            self.ConfigObj.logger.info("[bot._run] No eligible arb opportunities.")
            return

        self.ConfigObj.logger.info(
            f"[bot._run] Found {len(r)} eligible arb opportunities."
        )
        r = self.randomize(arb_opps=r, randomizer=randomizer)

        if data_validator:
            r = self.validate_optimizer_trades(arb_opp=r, arb_finder=finder)
            if r is None:
                self.ConfigObj.logger.warning(
                    "[bot._run] Math validation eliminated arb opportunity, restarting."
                )
                return
            if replay_mode:
                pass
            elif self.validate_pool_data(arb_opp=r):
                self.ConfigObj.logger.debug(
                    "[bot._run] All data checks passed! Pools in sync!"
                )
            else:
                self.ConfigObj.logger.warning(
                    "[bot._run] Data validation failed. Updating pools and restarting."
                )
                return

        tx_hash, tx_receipt = self._handle_trade_instructions(CCm, arb_mode, r, replay_from_block)

        if tx_hash:
            tx_status = ["failed", "succeeded"][tx_receipt["status"]] if tx_receipt else "pending"
            tx_details = json.dumps(tx_receipt, indent=4) if tx_receipt else "no receipt"
            self.ConfigObj.logger.info(f"Arbitrage transaction {tx_hash} {tx_status}")

            if logging_path:
                filename = f"tx_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
                with open(os.path.join(logging_path, filename), "w") as f:
                    f.write(f"{tx_hash} {tx_status}: {tx_details}")

    def validate_optimizer_trades(self, arb_opp, arb_finder):
        """
        Validates arbitrage trade input using equations that account for fees.
        This has limited coverage, but is very effective for the instances it covers.

        Parameters
        ----------
        arb_opp: tuple
            The tuple containing an arbitrage opportunity found by the Optimizer
        arb_finder: Any
            The Arb mode class that handles the differences required for each arb route.

        Returns
        -------
        tuple or None
        """

        (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = arb_opp

        (
            ordered_trade_instructions_dct,
            tx_in_count,
        ) = self._simple_ordering_by_src_token(
            best_trade_instructions_dic, best_src_token
        )
        cids = []
        for pool in ordered_trade_instructions_dct:
            pool_cid = pool["cid"]
            if "-0" in pool_cid or "-1" in pool_cid:
                self.ConfigObj.logger.debug(
                    f"[bot.validate_optimizer_trades] Math arb validation not currently supported for arbs with "
                    f"Carbon, returning to main flow."
                )
                return arb_opp
            cids.append(pool_cid)
        if len(cids) > 3:
            self.ConfigObj.logger.warning(
                f"[bot.validate_optimizer_trades] Math validation not supported for more than 3 pools, returning "
                f"to main flow."
            )
            return arb_opp
        max_trade_in = arb_finder.get_optimal_arb_trade_amts(
            cids=cids, flt=best_src_token
        )
        if max_trade_in is None:
            return None
        if type(max_trade_in) != float and type(max_trade_in) != int:
            return None
        if max_trade_in < 0.0:
            return None
        self.ConfigObj.logger.debug(
            f"[bot.validate_optimizer_trades] max_trade_in equation = {max_trade_in}, optimizer trade in = {ordered_trade_instructions_dct[0]['amtin']}"
        )
        ordered_trade_instructions_dct[0]["amtin"] = max_trade_in

        best_trade_instructions_dic = ordered_trade_instructions_dct

        return (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        )

    def validate_pool_data(self, arb_opp):
        """
        Validates that the data for each pool in the arbitrage opportunity is fresh.

        Parameters
        ----------
        arb_opp: tuple
            The tuple containing an arbitrage opportunity found by the Optimizer

        Returns
        -------
        bool
        """
        self.ConfigObj.logger.info("[bot.validate_pool_data] Validating pool data...")
        (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = arb_opp
        for pool in best_trade_instructions_dic:
            pool_cid = pool["cid"].split("-")[0]
            strategy_id = pool["strategy_id"]
            current_pool = self.db.get_pool(cid=pool_cid)
            pool_info = {
                "cid": pool_cid,
                "strategy_id": strategy_id,
                "id": current_pool.id,
                "address": current_pool.address,
                "pair_name": current_pool.pair_name,
                "exchange_name": current_pool.exchange_name,
                "tkn0_address": current_pool.tkn0_address,
                "tkn1_address": current_pool.tkn1_address,
                "tkn0_symbol": current_pool.tkn0_symbol,
                "tkn1_symbol": current_pool.tkn1_symbol,
                "tkn0_decimals" : current_pool.tkn0_decimals,
                "tkn1_decimals": current_pool.tkn1_decimals,
            }

            self.db.mgr.update_from_pool_info(pool_info=pool_info)
            self.ConfigObj.logger.debug(f"[bot.validate_pool_data] pool_cid: {pool_cid}")
            self.ConfigObj.logger.debug(f"[bot.validate_pool_data] pool_info: {pool_info}")

            if current_pool.exchange_name in self.ConfigObj.CARBON_V1_FORKS:
                if (
                    current_pool.y_0 != pool_info["y_0"]
                    or current_pool.y_1 != pool_info["y_1"]
                ):
                    self.ConfigObj.logger.debug(
                        "[bot.validate_pool_data] Carbon pool not up to date, updating and restarting."
                    )
                    return False
            elif current_pool.exchange_name in [
                "balancer",
            ]:
                for idx, balance in enumerate(current_pool.token_balances):
                    if balance != pool_info[f"tkn{idx}_balance"]:
                        self.ConfigObj.logger.debug(
                            "[bot.validate_pool_data] Balancer pool not up to date, updating and restarting."
                        )
                        return False
            elif current_pool.exchange_name in self.ConfigObj.UNI_V3_FORKS:
                if (
                    current_pool.liquidity != pool_info["liquidity"]
                    or current_pool.sqrt_price_q96 != pool_info["sqrt_price_q96"]
                    or current_pool.tick != pool_info["tick"]
                ):
                    self.ConfigObj.logger.debug(
                        "[bot.validate_pool_data] UniV3 pool not up to date, updating and restarting."
                    )
                    return False

            elif (
                current_pool.tkn0_balance != pool_info["tkn0_balance"]
                or current_pool.tkn1_balance != pool_info["tkn1_balance"]
            ):
                self.ConfigObj.logger.debug(
                    f"[bot.validate_pool_data] {pool_info['exchange_name']} pool not up to date, updating and restarting."
                )
                return False

        return True

    @staticmethod
    def randomize(arb_opps, randomizer: int = 1):
        """
        Sorts arb opportunities by profit, then returns a random element from the top N arbs, with N being the value input in randomizer.
        :param arb_opps: Arb opportunities
        :param randomizer: the number of arb ops to choose from after sorting by profit. For example, a value of 3 would be the top 3 arbs by profitability.
        returns:
            A randomly selected arb opportunity.

        """
        arb_opps.sort(key=lambda x: x[0], reverse=True)
        randomizer = min(max(randomizer, 1), len(arb_opps))
        top_n_arbs = arb_opps[:randomizer]
        return random.choice(top_n_arbs)

    @staticmethod
    def _carbon_in_trade_route(trade_instructions: List[TradeInstruction]) -> bool:
        """
        Returns True if the exchange route includes Carbon
        """
        return any(trade.is_carbon for trade in trade_instructions)
    
    def get_prices_simple(self, CCm, tkn0, tkn1):
        curve_prices = [(x.params['exchange'],x.descr,x.cid,x.p) for x in CCm.bytknx(tkn0).bytkny(tkn1)]
        curve_prices += [(x.params['exchange'],x.descr,x.cid,1/x.p) for x in CCm.bytknx(tkn1).bytkny(tkn0)]
        return curve_prices
    
    # Global constant for Carbon Forks ordering
    CARBON_SORTING_ORDER = float('inf')

    # Create a sort order mapping function
    def create_sort_order(self, sort_sequence):
        # Create a dictionary mapping from sort sequence to indices, except for Carbon Forks
        return {key: index for index, key in enumerate(sort_sequence) if key not in self.ConfigObj.CARBON_V1_FORKS}

    # Define the sort key function separately
    def sort_key(self, item, sort_order):
        # Check if the item is Carbon Forks
        if item[0] in self.ConfigObj.CARBON_V1_FORKS:
            return self.CARBON_SORTING_ORDER
        # Otherwise, use the sort order from the dictionary, or a default high value
        return sort_order.get(item[0], self.CARBON_SORTING_ORDER - 1)

    # Define the custom sort function
    def custom_sort(self, data, sort_sequence):
        sort_order = self.create_sort_order(sort_sequence)
        return sorted(data, key=lambda item: self.sort_key(item, sort_order))

    def calculate_profit(
        self,
        CCm: CPCContainer,
        best_profit: Decimal,
        fl_token: str,
        flashloan_fee_amt: int = 0,
    ) -> Tuple[Decimal, Decimal, Decimal]:
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
        Tuple[Decimal, Decimal, Decimal]
            The updated best_profit, flt_per_bnt, and profit_usd.
        """
        self.ConfigObj.logger.debug(f"[bot.calculate_profit] best_profit, fl_token, flashloan_fee_amt: {best_profit, fl_token, flashloan_fee_amt}")
        sort_sequence = ['bancor_v2','bancor_v3'] + self.ConfigObj.UNI_V2_FORKS + self.ConfigObj.UNI_V3_FORKS

        best_profit_fl_token = best_profit
        flashloan_fee_amt_fl_token = Decimal(str(flashloan_fee_amt))
        if fl_token not in [self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS]:
            price_curves = self.get_prices_simple(CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, fl_token)
            sorted_price_curves = self.custom_sort(price_curves, sort_sequence)
            self.ConfigObj.logger.debug(f"[bot.calculate_profit sort_sequence] {sort_sequence}")
            self.ConfigObj.logger.debug(f"[bot.calculate_profit price_curves] {price_curves}")
            self.ConfigObj.logger.debug(f"[bot.calculate_profit sorted_price_curves] {sorted_price_curves}")
            if len(sorted_price_curves)>0:
                fltkn_gastkn_conversion_rate = sorted_price_curves[0][-1]
                flashloan_fee_amt_gastkn = Decimal(str(flashloan_fee_amt_fl_token)) / Decimal(str(fltkn_gastkn_conversion_rate))
                best_profit_gastkn = Decimal(str(best_profit_fl_token)) / Decimal(str(fltkn_gastkn_conversion_rate)) - flashloan_fee_amt_gastkn
                self.ConfigObj.logger.debug(f"[bot.calculate_profit] {fl_token, best_profit_fl_token, fltkn_gastkn_conversion_rate, best_profit_gastkn, 'GASTOKEN'}")
            else:
                self.ConfigObj.logger.error(
                    f"[bot.calculate_profit] Failed to get conversion rate for {fl_token} and {self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS}. Raise"
                )
                raise
        else:
            best_profit_gastkn = best_profit_fl_token - flashloan_fee_amt_fl_token

        try:
            price_curves_usd = self.get_prices_simple(CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, self.ConfigObj.STABLECOIN_ADDRESS)
            sorted_price_curves_usd = self.custom_sort(price_curves_usd, sort_sequence)
            self.ConfigObj.logger.debug(f"[bot.calculate_profit price_curves_usd] {price_curves_usd}")
            self.ConfigObj.logger.debug(f"[bot.calculate_profit sorted_price_curves_usd] {sorted_price_curves_usd}")
            usd_gastkn_conversion_rate = Decimal(str(sorted_price_curves_usd[0][-1]))
        except Exception:
            usd_gastkn_conversion_rate = Decimal("NaN")

        best_profit_usd = best_profit_gastkn * usd_gastkn_conversion_rate
        self.ConfigObj.logger.debug(f"[bot.calculate_profit] {'GASTOKEN', best_profit_gastkn, usd_gastkn_conversion_rate, best_profit_usd, 'USD'}")
        return best_profit_fl_token, best_profit_gastkn, best_profit_usd

    @staticmethod
    def calculate_arb(
        arb_mode: str,
        best_profit_gastkn: Decimal,
        best_profit_usd: Decimal,
        flashloan_tkn_profit: Decimal,
        calculated_trade_instructions: List[Any],
        fl_token: str,
    ) -> dict:
        """
        Calculate the arbitrage.

        Parameters
        ----------
        arb_mode: str
            The arbitrage mode.
        best_profit: Decimal
            The best profit.
        best_profit_usd: Decimal
            The profit in USD.
        flashloan_tkn_profit: Decimal
            The profit from flashloan token.
        calculated_trade_instructions: List[Any]
            The calculated trade instructions.
        fl_token: str
            The flashloan token.

        Returns
        -------
        dict
            The arbitrage.
        """

        return {
            "type": arb_mode,
            "profit_gas_token": num_format(best_profit_gastkn),
            "profit_usd": num_format(best_profit_usd),
            "flashloan": [
                {
                    "token": fl_token,
                    "amount": num_format(calculated_trade_instructions[0].amtin),
                    "profit": num_format(flashloan_tkn_profit)
                }
            ],
            "trades": [
                {
                    "trade_index": idx,
                    "exchange": trade.exchange_name,
                    "tkn_in": {trade.tknin_symbol: trade.tknin} if trade.tknin_symbol != trade.tknin else trade.tknin,
                    "amount_in": num_format(trade.amtin),
                    "tkn_out": {trade.tknout_symbol: trade.tknout} if trade.tknout_symbol != trade.tknout else trade.tknout,
                    "amt_out": num_format(trade.amtout),
                    "cid0": trade.cid[-10:]
                }
                for idx, trade in enumerate(calculated_trade_instructions)
            ]
        }

    def _handle_trade_instructions(
        self,
        CCm: CPCContainer,
        arb_mode: str,
        r: Any,
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
        r: Any
            The result.
        replay_from_block: int
            the block number to start replaying from (default: None)

        Returns
        -------
        - The hash of the transaction if submitted, None otherwise.
        - The receipt of the transaction if completed, None otherwise.
        """
        (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = r

        # Order the trade instructions
        (
            ordered_trade_instructions_dct,
            tx_in_count,
        ) = self._simple_ordering_by_src_token(
            best_trade_instructions_dic, best_src_token
        )

        # Scale the trade instructions
        ordered_scaled_dcts = self._basic_scaling(
            ordered_trade_instructions_dct, best_src_token
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
            if self._carbon_in_trade_route(ordered_trade_instructions_objects)
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

        best_profit = flashloan_tkn_profit = tx_route_handler.calculate_trade_profit(
            calculated_trade_instructions
        )

        # Calculate the best profit
        best_profit_fl_token, best_profit_gastkn, best_profit_usd = self.calculate_profit(
            CCm, best_profit, fl_token, flashloan_fee_amt
        )

        # Log the best profit
        self.ConfigObj.logger.debug(
            f"[bot._handle_trade_instructions] Updated best_profit after calculating exact trade numbers: {num_format(best_profit_gastkn)}"
        )

        # Calculate the arbitrage
        arb = self.calculate_arb(
            arb_mode,
            best_profit_gastkn,
            best_profit_usd,
            flashloan_tkn_profit,
            calculated_trade_instructions,
            fl_token_symbol,
        )

        # Log the arbitrage
        self.ConfigObj.logger.info(
            f"[bot._handle_trade_instructions] calculated arb: {arb}"
        )

        # Check if the best profit is greater than the minimum profit
        if best_profit_gastkn < self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN:
            self.ConfigObj.logger.info(
                f"[bot._handle_trade_instructions] Opportunity with profit: {num_format(best_profit_gastkn)} does not meet minimum profit: {self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN}, discarding."
            )
            return None, None

        # Log the flashloan amount
        self.ConfigObj.logger.debug(
            f"[bot._handle_trade_instructions] Flashloan amount: {flashloan_amount_wei}"
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

        # Get the cids
        cids = [(ti.cid,ti.strategy_id) for ti in ordered_trade_instructions_objects]

        # Check if the network is tenderly and submit the transaction accordingly
        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            return (
                self._validate_and_submit_transaction_tenderly(
                    ConfigObj=self.ConfigObj,
                    flashloan_struct=flashloan_struct,
                    route_struct=route_struct_maximized,
                    src_amount=flashloan_amount_wei,
                    src_address=flashloan_token_address,
                ),
                cids,
                route_struct_maximized,
                log_dict,
            )

        # Log the route_struct
        self.handle_logging_for_trade_instructions(
            4,  # The log id
            flashloan_amount=flashloan_amount_wei,
            flashloan_token_symbol=fl_token_symbol,
            flashloan_token_address=flashloan_token_address,
            route_struct=route_struct_maximized,
            best_trade_instructions_dic=best_trade_instructions_dic,
        )

        # Get the tx helpers class
        tx_helpers = TxHelpers(ConfigObj=self.ConfigObj)

        # Return the validate and submit transaction
        return (
            tx_helpers.validate_and_submit_transaction(
                route_struct=route_struct_maximized,
                src_amt=flashloan_amount_wei,
                src_address=flashloan_token_address,
                expected_profit_gastkn=best_profit_gastkn,
                expected_profit_usd=best_profit_usd,
                safety_override=False,
                verbose=True,
                log_object=log_dict,
                flashloan_struct=flashloan_struct,
            ),
            cids,
            route_struct,
            log_dict,
        )

    def handle_logging_for_trade_instructions(self, log_id: int, **kwargs):
        """
        Handles logging for trade instructions based on log_id.

        Parameters
        ----------
        log_id : int
            The ID for log type.
        **kwargs : dict
            Additional parameters required for logging.

        Returns
        -------
        None
        """
        log_actions = {
            1: self.log_best_profit,
            2: self.log_calculated_arb,
            3: self.log_flashloan_amount,
            4: self.log_flashloan_details,
        }
        log_action = log_actions.get(log_id)
        if log_action:
            log_action(**kwargs)

    def log_best_profit(self, best_profit: Optional[float] = None):
        """
        Logs the best profit.

        Parameters
        ----------
        best_profit : Optional[float], optional
            The best profit, by default None
        """
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
            f"[bot._handle_trade_instructions] Trade Instructions: \n {best_trade_instructions_dic}"
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

    def get_tokens_in_exchange(
        self,
        exchange_name: str,
    ) -> List[str]:
        """
        Gets all tokens that exist in pools on the specified exchange.
        :param exchange_name: the exchange name
        """
        return self.db.get_tokens_from_exchange(exchange_name=exchange_name)

    def run(
        self,
        *,
        flashloan_tokens: List[str] = None,
        CCm: CPCContainer = None,
        arb_mode: str = None,
        run_data_validator: bool = False,
        randomizer: int = 0,
        logging_path: str = None,
        replay_mode: bool = False,
        replay_from_block: int = None,
    ):
        """
        Runs the bot.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens (optional; default: RUN_FLASHLOAN_TOKENS)
        CCm: CPCContainer
            The complete market data container (optional; default: database via get_curves())
        arb_mode: str
            the arbitrage mode (default: None; can be set depending on arbmode)
        run_data_validator: bool
            whether to run the data validator (default: False)
        randomizer: int
            the randomizer (default: 0)
        logging_path: str
            the logging path (default: None)
        replay_mode: bool
            whether to run in replay mode (default: False)
        replay_from_block: int
            the block number to start replaying from (default: None)
        """

        if flashloan_tokens is None:
            flashloan_tokens = self.RUN_FLASHLOAN_TOKENS
        if CCm is None:
            CCm = self.get_curves()

        try:
            self._run(
                flashloan_tokens=flashloan_tokens,
                CCm=CCm,
                arb_mode=arb_mode,
                data_validator=run_data_validator,
                randomizer=randomizer,
                logging_path=logging_path,
                replay_mode=replay_mode,
                replay_from_block=replay_from_block,
            )
        except self.NoArbAvailable as e:
            self.ConfigObj.logger.info(e)
