# coding=utf-8
"""
Main integration point for the bot optimizer and other infrastructure.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT

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
import time
from _decimal import Decimal
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Tuple, Any, Callable
from typing import Optional

from fastlane_bot.config import Config
from fastlane_bot.helpers import (
    TxSubmitHandler,
    TxSubmitHandlerBase,
    TxReceiptHandler,
    TxReceiptHandlerBase,
    TxRouteHandler,
    TxRouteHandlerBase,
    TxHelpers,
    TxHelpersBase,
    TradeInstruction,
    Univ3Calculator,
    RouteStruct,
)
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
from fastlane_bot.tools.optimizer import CPCArbOptimizer
from .events.interface import QueryInterface
from .modes.pairwise_multi import FindArbitrageMultiPairwise
from .modes.pairwise_single import FindArbitrageSinglePairwise
from .modes.triangle_multi import ArbitrageFinderTriangleMulti
from .modes.triangle_single import ArbitrageFinderTriangleSingle
from .modes.triangle_single_bancor3 import ArbitrageFinderTriangleSingleBancor3
from .modes.triangle_bancor_v3_two_hop import ArbitrageFinderTriangleBancor3TwoHop
from .utils import num_format, log_format, num_format_float


@dataclass
class CarbonBotBase:
    """
    Base class for the business logic of the bot.

    Attributes
    ----------
    db: DatabaseManager
        the database manager.
    TxSubmitHandler: class derived from TxSubmitHandlerBase
        the class to be instantiated for the transaction submit handler (default: TxSubmitHandler).
    TxReceiptHandlerClass: class derived from TxReceiptHandlerBase
        ditto (default: TxReceiptHandler).
    TxRouteHandlerClass: class derived from TxRouteHandlerBase
        ditto (default: TxRouteHandler).
    TxHelpersClass: class derived from TxHelpersBase
        ditto (default: TxHelpers).

    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    db: QueryInterface = field(init=False)
    TxSubmitHandler: any = None
    TxReceiptHandlerClass: any = None
    TxRouteHandlerClass: any = None
    TxHelpersClass: any = None
    ConfigObj: Config = None
    usd_gas_limit: int = 150
    min_profit: int = 60
    polling_interval: int = None

    def __post_init__(self):
        """
        The post init method.
        """

        if self.ConfigObj is None:
            self.ConfigObj = Config()

        self.c = self.ConfigObj

        assert (
            self.polling_interval is None
        ), "polling_interval is now a parameter to run"

        if self.TxSubmitHandler is None:
            self.TxSubmitHandler = TxSubmitHandler(ConfigObj=self.ConfigObj)
        assert issubclass(
            self.TxSubmitHandler.__class__, TxSubmitHandlerBase
        ), f"TxSubmitHandler not derived from TxSubmitHandlerBase {self.TxSubmitHandler.__class__}"

        if self.TxReceiptHandlerClass is None:
            self.TxReceiptHandlerClass = TxReceiptHandler
        assert issubclass(
            self.TxReceiptHandlerClass, TxReceiptHandlerBase
        ), f"TxReceiptHandlerClass not derived from TxReceiptHandlerBase {self.TxReceiptHandlerClass}"

        if self.TxRouteHandlerClass is None:
            self.TxRouteHandlerClass = TxRouteHandler
        assert issubclass(
            self.TxRouteHandlerClass, TxRouteHandlerBase
        ), f"TxRouteHandlerClass not derived from TxRouteHandlerBase {self.TxRouteHandlerClass}"

        if self.TxHelpersClass is None:
            self.TxHelpersClass = TxHelpers(ConfigObj=self.ConfigObj)
        assert issubclass(
            self.TxHelpersClass.__class__, TxHelpersBase
        ), f"TxHelpersClass not derived from TxHelpersBase {self.TxHelpersClass}"

        self.db = QueryInterface(ConfigObj=self.ConfigObj)

    @property
    def C(self) -> Any:
        """
        Convenience method self.ConfigObj
        """
        return self.ConfigObj

    @staticmethod
    def versions():
        """
        Returns the versions of the module and its Carbon dependencies.
        """
        s = [f"fastlane_bot v{__VERSION__} ({__DATE__})"]
        s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(CPC)]
        s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer)]
        return s

    UDTYPE_FROM_CONTRACTS = "from_contracts"
    UDTYPE_FROM_EVENTS = "from_events"

    def get_curves(self) -> CPCContainer:
        """
        Gets the curves from the database.

        Returns
        -------
        CPCContainer
            The container of curves.
        """
        pools_and_tokens = self.db.get_pool_data_with_tokens()
        curves = []
        tokens = self.db.get_tokens()
        ADDRDEC = {t.key: (t.address, int(t.decimals)) for t in tokens}
        for p in pools_and_tokens:
            try:
                p.ADDRDEC = ADDRDEC
                curves += p.to_cpc()
            except ZeroDivisionError as e:
                self.ConfigObj.logger.error(
                    f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n"
                )
            except CPC.CPCValidationError as e:
                self.ConfigObj.logger.error(
                    f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n"
                )
            except TypeError as e:
                self.ConfigObj.logger.error(
                    f"[get_curves] MUST FIX DECIMAL ERROR CURVE {p} [{e}]\n"
                )
            except p.DoubleInvalidCurveError as e:
                self.ConfigObj.logger.error(
                    f"[get_curves] MUST FIX DOUBLE INVALID CURVE {p} [{e}]\n"
                )
            except Univ3Calculator.DecimalsMissingError as e:
                self.ConfigObj.logger.error(
                    f"[get_curves] MUST FIX DECIMALS MISSING [{e}]\n"
                )
            except Exception as e:
                self.ConfigObj.logger.error(
                    f"[get_curves] error converting pool to curve {p}\n[ERR={e}]\n\n"
                )

        return CPCContainer(curves)


@dataclass
class CarbonBot(CarbonBotBase):
    """
    A class that handles the business logic of the bot.

    MAIN ENTRY POINTS
    :run:               Runs the bot.
    """

    XS_ARBOPPS = "arbopps"
    XS_TI = "ti"
    XS_EXACT = "exact"
    XS_ORDSCAL = "ordscal"
    XS_AGGTI = "aggti"
    XS_ORDINFO = "ordinfo"
    XS_ENCTI = "encti"
    XS_ROUTE = "route"
    AM_REGULAR = "regular"
    AM_SINGLE = "single"
    AM_TRIANGLE = "triangle"
    AM_MULTI = "multi"
    AM_MULTI_TRIANGLE = "multi_triangle"
    AM_BANCOR_V3 = "bancor_v3"
    RUN_FLASHLOAN_TOKENS = [T.WETH, T.DAI, T.USDC, T.USDT, T.WBTC, T.BNT, T.NATIVE_ETH]
    RUN_SINGLE = "single"
    RUN_CONTINUOUS = "continuous"
    RUN_POLLING_INTERVAL = 60  # default polling interval in seconds
    SCALING_FACTOR = 0.999
    AO_TOKENS = "tokens"
    AO_CANDIDATES = "candidates"
    BNT_ETH_CID = "0xc4771395e1389e2e3a12ec22efbb7aff5b1c04e5ce9c7596a82e9dc8fdec725b"

    def __post_init__(self):
        super().__post_init__()

    class NoArbAvailable(Exception):
        pass

    def _simple_ordering_by_src_token(
        self, best_trade_instructions_dic, best_src_token
    ):
        """
        Reorders a trade_instructions_dct so that all items where the best_src_token is the tknin are before others
        """
        if best_trade_instructions_dic is None:
            raise self.NoArbAvailable(
                f"[_simple_ordering_by_src_token] {best_trade_instructions_dic}"
            )
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

    def _simple_ordering_by_src_token_v2(
        self, best_trade_instructions_dic, best_src_token
    ):
        """
        Reorders a trade_instructions_dct so that all items where the best_src_token is the tknin are before others
        """
        if best_trade_instructions_dic is None:
            raise self.NoArbAvailable(
                f"[_simple_ordering_by_src_token] {best_trade_instructions_dic}"
            )
        trades = [
            x for x in best_trade_instructions_dic if x["tknin"] == best_src_token
        ]
        tx_in_count = len(trades)
        while len(trades) < len(best_trade_instructions_dic):
            next_tkn = trades[-1]["tknout"]
            trades += [x for x in best_trade_instructions_dic if x["tknin"] == next_tkn]

        return trades, tx_in_count

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

    @staticmethod
    def _drop_error(trade_instructions_dct):
        return [
            {k: v for k, v in trade_instructions_dct[i].items() if k != "error"}
            for i in range(len(trade_instructions_dct))
        ]

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
        errorless_trade_instructions_dic = self._drop_error(trade_instructions_dic)
        result = (
            {
                **ti,
                "raw_txs": "[]",
                "pair_sorting": "",
                "ConfigObj": self.ConfigObj,
                "db": self.db,
            }
            for ti in errorless_trade_instructions_dic
            if ti is not None
        )
        result = [TradeInstruction(**ti) for ti in result]
        return result

    @staticmethod
    def _check_if_carbon(cid: str):
        """
        Checks if the curve is a Carbon curve.

        Returns
        -------
        bool
            Whether the curve is a Carbon curve.
        """
        if "-" in cid:
            _cid_tkn = cid.split("-")[1]
            cid = cid.split("-")[0]
            return True, _cid_tkn, cid
        return False, "", cid

    @staticmethod
    def _check_if_not_carbon(cid: str):
        """
        Checks if the curve is a Carbon curve.
        Returns
        -------
        bool
            Whether the curve is a Carbon curve.
        """
        return "-" not in cid

    @dataclass
    class ArbCandidate:
        """
        The arbitrage candidates.
        """

        result: any
        constains_carbon: bool = None
        profit_usd: float = None

        @property
        def r(self):
            return self.result

    def _get_deadline(self) -> int:
        """
        Gets the deadline for a transaction.

        Returns
        -------
        int
            The deadline (as UNIX epoch).
        """
        return (
            self.ConfigObj.w3.eth.getBlock(self.ConfigObj.w3.eth.block_number).timestamp
            + self.ConfigObj.DEFAULT_BLOCKTIME_DEVIATION
        )

    @staticmethod
    def _get_arb_finder(arb_mode: str) -> Callable:
        if arb_mode in {"single", "pairwise_single"}:
            return FindArbitrageSinglePairwise
        elif arb_mode in {"multi", "pairwise_multi"}:
            return FindArbitrageMultiPairwise
        elif arb_mode in {"triangle", "triangle_single"}:
            return ArbitrageFinderTriangleSingle
        elif arb_mode in {"multi_triangle", "triangle_multi"}:
            return ArbitrageFinderTriangleMulti
        elif arb_mode in {"bancor_v3", "single_triangle_bancor3"}:
            return ArbitrageFinderTriangleSingleBancor3
        elif arb_mode in {"b3_two_hop"}:
            return ArbitrageFinderTriangleBancor3TwoHop

    def _run(
        self,
        flashloan_tokens: List[str],
        CCm: CPCContainer,
        *,
        result=None,
        arb_mode: str = None,
        randomizer=True,
        data_validator=True,
    ) -> Optional[Tuple[str, List[Any]]]:
        """
        Runs the bot.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The tokens to flashloan.
        CCm: CPCContainer
            The container.
        result: str
            The result type.
        arb_mode: str
            The arbitrage mode.
        randomizer: bool
            Whether to randomize the arbitrage opportunities.
        data_validator: bool
            If extra data validation should be performed

        Returns
        -------
        Optional[Tuple[str, List[Any]]]
            The result.

        """
        random_mode = self.AO_CANDIDATES if randomizer else None
        arb_mode = self.AM_SINGLE if arb_mode is None else arb_mode
        arb_finder = self._get_arb_finder(arb_mode)
        finder = arb_finder(
            flashloan_tokens=flashloan_tokens,
            CCm=CCm,
            mode="bothin",
            result=random_mode,
            ConfigObj=self.ConfigObj,
        )
        r = finder.find_arbitrage()

        if result == self.XS_ARBOPPS:
            return r

        if r is None or len(r) == 0:
            self.ConfigObj.logger.info("No eligible arb opportunities.")
            return None

        self.ConfigObj.logger.info(f"Found {len(r)} eligible arb opportunities.")
        r = random.choice(r) if randomizer else r
        if data_validator or arb_mode == "bancor_v3":
            # Add random chance if we should check or not
            r = self.validate_optimizer_trades(arb_opp=r, arb_mode=arb_mode, arb_finder=finder)
            if r is None:
                self.ConfigObj.logger.info("Math validation eliminated arb opportunity, restarting.")
                return None
            if self.validate_pool_data(arb_opp=r):
                self.ConfigObj.logger.info("All data checks passed! Pools in sync!")
            else:
                self.ConfigObj.logger.info("Data validation failed. Updating pools and restarting.")
                return None
            
        return self._handle_trade_instructions(CCm, arb_mode, r, result)

    def validate_optimizer_trades(self, arb_opp, arb_mode, arb_finder):
        """
        Validates arbitrage trade input using equations that account for fees.
        This has limited coverage, but is very effective for the instances it covers.

        Parameters
        ----------
        arb_opp: tuple
            The tuple containing an arbitrage opportunity found by the Optimizer
        arb_mode: str
            The arbitrage mode.
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
        if arb_mode == "bancor_v3" or arb_mode == "b3_two_hop":

            cids = []
            for pool in ordered_trade_instructions_dct:
                pool_cid = pool["cid"]
                if "-0" in pool_cid or "-1" in pool_cid:
                    self.ConfigObj.logger.debug(f"Math arb validation not currently supported for arbs with Carbon, returning to main flow.")
                    return arb_opp
                    # pool_cid = pool_cid.split("-")[0]
                cids.append(pool_cid)
            if len(cids) > 3:
                self.ConfigObj.logger.info(f"Math validation not supported for more than 3 pools, returning to main flow.")
                return arb_opp
            max_trade_in = arb_finder.get_optimal_arb_trade_amts(cids=cids, flt=best_src_token)
            if max_trade_in is None:
                return None
            if max_trade_in < 0.0:
                return None
            self.ConfigObj.logger.debug(f"max_trade_in equation = {max_trade_in}, optimizer trade in = {ordered_trade_instructions_dct[0]['amtin']}")
            ordered_trade_instructions_dct[0]["amtin"] = max_trade_in

            best_trade_instructions_dic = ordered_trade_instructions_dct
        else:
            return arb_opp

        arb_opp = (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        )
        return arb_opp

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
        self.ConfigObj.logger.info("Validating pool data.")
        (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = arb_opp
        for pool in best_trade_instructions_dic:
            pool_cid = pool["cid"]

            if "-0" in pool_cid or "-1" in pool_cid:
                pool_cid = pool_cid.split("-")[0]
            current_pool = self.db.get_pool(cid=pool_cid)
            pool_info = {"cid": pool_cid, "id": current_pool.id, "address": current_pool.address, "pair_name": current_pool.pair_name,
                         "exchange_name": current_pool.exchange_name, "tkn0_address": current_pool.tkn0_address, "tkn1_address": current_pool.tkn1_address, "tkn0_key": current_pool.tkn0_key, "tkn1_key": current_pool.tkn1_key, "args": {"id": current_pool.cid}}

            fetched_pool = self.db.mgr.update_from_pool_info(pool_info=pool_info)
            if fetched_pool is None:
                self.ConfigObj.logger.error(f"Could not fetch pool data for {pool_cid}")

            ex_name = fetched_pool['exchange_name']
            self._validate_pool_data_logging(pool_cid, fetched_pool)

            if ex_name == "bancor_v3":
                self._validate_pool_data_logging(pool_cid, fetched_pool)

            if current_pool.exchange_name == "carbon_v1":
                if current_pool.y_0 != fetched_pool["y_0"] or current_pool.y_1 != fetched_pool["y_1"]:
                    self.ConfigObj.logger.debug(
                        "Carbon pool not up to date, updating and restarting."
                    )
                    return False

            elif current_pool.exchange_name in ["uniswap_v3", "sushiswap_v3"]:
                if current_pool.liquidity != fetched_pool["liquidity"] or current_pool.sqrt_price_q96 != fetched_pool["sqrt_price_q96"] or current_pool.tick != fetched_pool["tick"]:
                    self.ConfigObj.logger.debug(
                        "UniV3 pool not up to date, updating and restarting."
                    )
                    return False

            elif current_pool.tkn0_balance != fetched_pool["tkn0_balance"] or current_pool.tkn1_balance != fetched_pool["tkn1_balance"]:
                self.ConfigObj.logger.debug(f"{ex_name} pool not up to date, updating and restarting.")
                return False
            
        return True

    def _validate_pool_data_logging(self, pool_cid: str, fetched_pool: Dict[str, Any]) -> None:
        """
        Logs the pool data validation.

        Parameters
        ----------
        pool_cid: str
            The pool CID.
        fetched_pool: dict
            The fetched pool data.

        """
        self.ConfigObj.logger.debug(f"[bot.py validate] pool_cid: {pool_cid}")
        self.ConfigObj.logger.debug(f"[bot.py validate] fetched_pool: {fetched_pool['exchange_name']}")
        self.ConfigObj.logger.debug(f"[bot.py validate] fetched_pool: {fetched_pool}")

    @staticmethod
    def _carbon_in_trade_route(trade_instructions: List[TradeInstruction]) -> bool:
        """
        Returns True if the exchange route includes Carbon
        """
        return any(trade.is_carbon for trade in trade_instructions)

    def calculate_profit(
        self,
        CCm: CPCContainer,
        best_profit: Decimal,
        fl_token: str,
        fl_token_with_weth: str,
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
        fl_token_with_weth: str
            The flashloan token with weth.

        Returns
        -------
        Tuple[Decimal, Decimal, Decimal]
            The updated best_profit, flt_per_bnt, and profit_usd.
        """
        flt_per_bnt = Decimal(1)
        if fl_token_with_weth != T.BNT:
            bnt_flt_curves = CCm.bypair(pair=f"{T.BNT}/{fl_token_with_weth}")
            bnt_flt = [
                x for x in bnt_flt_curves if x.params["exchange"] == "bancor_v3"
            ][0]
            flt_per_bnt = Decimal(str(bnt_flt.x_act / bnt_flt.y_act))
            best_profit = Decimal(str(flt_per_bnt * best_profit))

        bnt_usdc_curve = CCm.bycid(self.BNT_ETH_CID)
        usd_bnt = bnt_usdc_curve.y / bnt_usdc_curve.x
        profit_usd = best_profit * Decimal(str(usd_bnt))

        return best_profit, flt_per_bnt, profit_usd

    @staticmethod
    def update_log_dict(
        arb_mode: str,
        best_profit: Decimal,
        profit_usd: Decimal,
        flashloan_tkn_profit: Decimal,
        calculated_trade_instructions: List[Any],
        fl_token: str,
    ) -> Dict[str, Any]:
        """
        Update the log dictionary.

        Parameters
        ----------
        arb_mode: str
            The arbitrage mode.
        best_profit: Decimal
            The best profit.
        profit_usd: Decimal
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
            The updated log dictionary.
        """
        flashloans = [
            {
                "token": fl_token,
                "amount": num_format_float(calculated_trade_instructions[0].amtin),
                "profit": num_format_float(flashloan_tkn_profit),
            }
        ]
        log_dict = {
            "type": arb_mode,
            "profit_bnt": num_format_float(best_profit),
            "profit_usd": num_format_float(profit_usd),
            "flashloan": flashloans,
            "trades": [],
        }

        for idx, trade in enumerate(calculated_trade_instructions):
            log_dict["trades"].append(
                {
                    "trade_index": idx,
                    "exchange": trade.exchange_name,
                    "tkn_in": trade.tknin,
                    "amount_in": num_format_float(trade.amtin),
                    "tkn_out": trade.tknout,
                    "amt_out": num_format_float(trade.amtout),
                    "cid0": trade.cid[-10:],
                }
            )

        return log_dict

    def _handle_trade_instructions(
        self, CCm: CPCContainer, arb_mode: str, r: Any, result: str
    ) -> Any:
        """
        Handles the trade instructions.

        Parameters
        ----------
        CCm: CPCContainer
            The container.
        arb_mode: str
            The arbitrage mode.
        r: Any
            The result.
        result: str
            The result type.

        Returns
        -------
        Any
            The result.
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
        tx_route_handler = self.TxRouteHandlerClass(
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

        # Get the flashloan token
        fl_token = fl_token_with_weth = calculated_trade_instructions[0].tknin_key

        # If the flashloan token is WETH, then use ETH
        if fl_token == T.WETH:
            fl_token = T.NATIVE_ETH

        # Calculate the profit
        # best_profit_old = flashloan_tkn_profit = (
        #     calculated_trade_instructions[-1].amtout
        #     - calculated_trade_instructions[0].amtin
        # )

        best_profit = flashloan_tkn_profit = tx_route_handler.calculate_trade_profit(calculated_trade_instructions)

        # self.ConfigObj.logger.info(
        #     f"Opportunity with profit: {num_format(best_profit)} vs old profit {best_profit_old}."
        # )
        # Use helper function to calculate profit
        best_profit, flt_per_bnt, profit_usd = self.calculate_profit(
            CCm, best_profit, fl_token, fl_token_with_weth
        )

        # Log the best trade instructions
        self.handle_logging_for_trade_instructions(
            1, # The log id
            best_profit=best_profit
        )

        # Use helper function to update the log dict
        log_dict = self.update_log_dict(
            arb_mode,
            best_profit,
            profit_usd,
            flashloan_tkn_profit,
            calculated_trade_instructions,
            fl_token,
        )

        # Log the log dict
        self.handle_logging_for_trade_instructions(
            2, # The log id
            log_dict=log_dict
        )

        # Check if the best profit is greater than the minimum profit
        if best_profit < self.ConfigObj.DEFAULT_MIN_PROFIT:
            self.ConfigObj.logger.info(
                f"Opportunity with profit: {num_format(best_profit)} does not meet minimum profit: {self.ConfigObj.DEFAULT_MIN_PROFIT}, discarding."
            )
            return None, None

        # Get the flashloan amount and token address
        flashloan_amount = int(calculated_trade_instructions[0].amtin_wei)
        flashloan_token_address = self.ConfigObj.w3.toChecksumAddress(
            self.db.get_token(key=fl_token).address
        )

        # Log the flashloan amount and token address
        self.handle_logging_for_trade_instructions(
            3, # The log id
            flashloan_amount=flashloan_amount,
        )

        # Encode the trade instructions
        encoded_trade_instructions = tx_route_handler.custom_data_encoder(
            calculated_trade_instructions
        )

        # Get the deadline
        deadline = self._get_deadline()

        # Get the route struct
        route_struct = [
            asdict(rs)
            for rs in tx_route_handler.get_route_structs(
                encoded_trade_instructions, deadline
            )
        ]

        # Check if the result is None
        assert result is None, f"Unknown result requested {result}"

        # Get the cids
        cids = list({ti["cid"].split("-")[0] for ti in best_trade_instructions_dic})

        # Check if the network is tenderly and submit the transaction accordingly
        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            return (
                self._validate_and_submit_transaction_tenderly(
                    ConfigObj=self.ConfigObj,
                    route_struct=route_struct,
                    src_amount=flashloan_amount,
                    src_address=flashloan_token_address,
                ),
                cids,
            )

        # Log the route_struct
        self.handle_logging_for_trade_instructions(
            4, # The log id
            flashloan_amount=flashloan_amount,
            flashloan_token_address=flashloan_token_address,
            route_struct=route_struct,
            best_trade_instructions_dic=best_trade_instructions_dic,
        )

        # Get the bnt_eth pool
        pool = self.db.get_pool(
            exchange_name=self.ConfigObj.BANCOR_V3_NAME,
            pair_name=f"{T.BNT}/{T.NATIVE_ETH}",
        )

        # Get the bnt_eth price
        bnt_eth = (int(pool.tkn0_balance), int(pool.tkn1_balance))

        # Get the tx helpers class
        tx_helpers = TxHelpers(ConfigObj=self.ConfigObj)

        # Return the validate and submit transaction
        return (
            tx_helpers.validate_and_submit_transaction(
                route_struct=route_struct,
                src_amt=flashloan_amount,
                src_address=flashloan_token_address,
                bnt_eth=bnt_eth,
                expected_profit=best_profit,
                safety_override=False,
                verbose=True,
                log_object=log_dict,
            ),
            cids,
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
            f"Updated best_profit after calculating exact trade numbers: {num_format(best_profit)}"
        )

    def log_calculated_arb(self, log_dict: Optional[Dict] = None):
        """
        Logs the calculated arbitrage.

        Parameters
        ----------
        log_dict : Optional[Dict], optional
            The dictionary containing log data, by default None
        """
        self.ConfigObj.logger.info(
            f"{log_format(log_data=log_dict, log_name='calculated_arb')}"
        )

    def log_flashloan_amount(self, flashloan_amount: Optional[float] = None):
        """
        Logs the flashloan amount.

        Parameters
        ----------
        flashloan_amount : Optional[float], optional
            The flashloan amount, by default None
        """
        self.ConfigObj.logger.debug(f"Flashloan amount: {flashloan_amount}")

    def log_flashloan_details(
            self,
            flashloan_amount: Optional[float] = None,
            flashloan_token_address: Optional[str] = None,
            route_struct: Optional[List[Dict]] = None,
            best_trade_instructions_dic: Optional[Dict] = None,
    ):
        """
        Logs the details of flashloan.

        Parameters
        ----------
        flashloan_amount : Optional[float], optional
            The flashloan amount, by default None
        flashloan_token_address : Optional[str], optional
            The flashloan token address, by default None
        route_struct : Optional[List[Dict]], optional
            The route structure, by default None
        best_trade_instructions_dic : Optional[Dict], optional
            The dictionary containing the best trade instructions, by default None
        """
        self.ConfigObj.logger.debug(f"Flashloan amount: {flashloan_amount}")
        self.ConfigObj.logger.debug(
            f"Flashloan token address: {flashloan_token_address}"
        )
        self.ConfigObj.logger.debug(f"Route Struct: \n {route_struct}")
        self.ConfigObj.logger.debug(
            f"Trade Instructions: \n {best_trade_instructions_dic}"
        )

    def _validate_and_submit_transaction_tenderly(
        self,
        ConfigObj: Config,
        route_struct: List[RouteStruct],
        src_address: str,
        src_amount: int,
    ):
        """
        Validate and submit the transaction tenderly

        Parameters
        ----------
        ConfigObj: Config
            The Config object
        route_struct: List[RouteStruct]
            The route struct
        src_address: str
            The source address
        src_amount: int
            The source amount

        Returns
        -------
        Any
            The transaction receipt

        """
        tx_submit_handler = TxSubmitHandler(
            ConfigObj=ConfigObj,
            route_struct=route_struct,
            src_address=src_address,
            src_amount=src_amount,
        )
        self.ConfigObj.logger.debug(f"route_struct: {route_struct}")
        self.ConfigObj.logger.debug("src_address", src_address)
        tx = tx_submit_handler.submit_transaction_tenderly(
            route_struct=route_struct, src_address=src_address, src_amount=src_amount
        )
        return self.ConfigObj.w3.eth.wait_for_transaction_receipt(tx)

    def validate_mode(self, mode: str):
        """
        Validate the mode. If the mode is None, set it to RUN_CONTINUOUS.
        """
        if mode is None:
            mode = self.RUN_CONTINUOUS
        assert mode in [
            self.RUN_SINGLE,
            self.RUN_CONTINUOUS,
        ], f"Unknown mode {mode} [possible values: {self.RUN_SINGLE}, {self.RUN_CONTINUOUS}]"
        return mode

    def setup_polling_interval(self, polling_interval: int):
        """
        Setup the polling interval. If the polling interval is None, set it to RUN_POLLING_INTERVAL.
        """
        if self.polling_interval is None:
            self.polling_interval = (
                polling_interval
                if polling_interval is not None
                else self.RUN_POLLING_INTERVAL
            )

    def setup_flashloan_tokens(self, flashloan_tokens):
        """
        Setup the flashloan tokens. If flashloan_tokens is None, set it to RUN_FLASHLOAN_TOKENS.
        """
        return (
            flashloan_tokens
            if flashloan_tokens is not None
            else self.RUN_FLASHLOAN_TOKENS
        )

    def setup_CCm(self, CCm: CPCContainer) -> CPCContainer:
        """
        Setup the CCm. If CCm is None, retrieve and filter curves.

        Parameters
        ----------
        CCm: CPCContainer
            The CPCContainer object

        Returns
        -------
        CPCContainer
            The filtered CPCContainer object
        """
        if CCm is None:
            CCm = self.get_curves()
            filter_out_weth = [
                x
                for x in CCm
                if (x.params.exchange == "carbon_v1")
                & (
                    (x.params.tkny_addr == self.ConfigObj.WETH_ADDRESS)
                    or (x.params.tknx_addr == self.ConfigObj.WETH_ADDRESS)
                )
            ]
            CCm = CPCContainer([x for x in CCm if x not in filter_out_weth])
        return CCm

    def run_continuous_mode(self, flashloan_tokens: List[str], arb_mode: str, run_data_validator: bool, randomizer: bool):
        """
        Run the bot in continuous mode.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens
        arb_mode: bool
            The arb mode
        """
        print(f"run_continuous_mode run_data_validator={run_data_validator}")
        while True:
            try:
                CCm = self.get_curves()
                filter_out_weth = [
                    x
                    for x in CCm
                    if (x.params.exchange == "carbon_v1")
                    & (
                        (x.params.tkny_addr == self.ConfigObj.WETH_ADDRESS)
                        or (x.params.tknx_addr == self.ConfigObj.WETH_ADDRESS)
                    )
                ]
                CCm = CPCContainer([x for x in CCm if x not in filter_out_weth])
                tx_hash, cids = self._run(flashloan_tokens, CCm, arb_mode=arb_mode, data_validator=run_data_validator, randomizer=randomizer)
                if tx_hash and tx_hash[0]:
                    self.ConfigObj.logger.info(f"Arbitrage executed [hash={tx_hash}]")

                time.sleep(self.polling_interval)
            except self.NoArbAvailable as e:
                self.ConfigObj.logger.debug(f"[bot:run:single] {e}")
            except Exception as e:
                self.ConfigObj.logger.error(f"[bot:run:continuous] {e}")
                time.sleep(self.polling_interval)

    def run_single_mode(
        self, flashloan_tokens: List[str], CCm: CPCContainer, arb_mode: str, run_data_validator: bool, randomizer: bool
    ):
        """
        Run the bot in single mode.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens
        CCm: CPCContainer
            The CPCContainer object
        arb_mode: bool
            The arb mode
        """
        try:
            tx_hash = self._run(
                flashloan_tokens=flashloan_tokens, CCm=CCm, arb_mode=arb_mode, data_validator=run_data_validator, randomizer=randomizer
            )
            if tx_hash and tx_hash[0]:
                self.ConfigObj.logger.info(f"Arbitrage executed [hash={tx_hash}]")
        except self.NoArbAvailable as e:
            self.ConfigObj.logger.warning(f"[NoArbAvailable] {e}")
        except Exception as e:
            self.ConfigObj.logger.error(f"[bot:run:single] {e}")
            raise

    def run(
        self,
        *,
        flashloan_tokens: List[str] = None,
        CCm: CPCContainer = None,
        polling_interval: int = None,
        mode: str = None,
        arb_mode: str = None,
        run_data_validator: bool = False,
        randomizer: bool = False
    ):
        """
        Runs the bot.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens (optional; default: self.RUN_FLASHLOAN_TOKENS)
        CCm: CPCContainer
            The complete market data container (optional; default: database via self.get_curves())
        polling_interval: int
            the polling interval in seconds (default: 60 via self.RUN_POLLING_INTERVAL)
        mode: RN_SINGLE or RUN_CONTINUOUS
            whether to run the bot one-off or continuously (default: RUN_CONTINUOUS)
        arb_mode: str
            the arbitrage mode (default: None)

        Returns
        -------
        str
            The transaction hash.
        """

        mode = self.validate_mode(mode)
        self.setup_polling_interval(polling_interval)
        flashloan_tokens = self.setup_flashloan_tokens(flashloan_tokens)
        CCm = self.setup_CCm(CCm)

        if mode == "continuous":
            self.run_continuous_mode(flashloan_tokens, arb_mode, run_data_validator, randomizer)
        else:
            self.run_single_mode(flashloan_tokens, CCm, arb_mode, run_data_validator, randomizer)
