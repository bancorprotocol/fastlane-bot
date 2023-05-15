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
    @@@@@@@@@@@@@@BANCOR@(2023)@@@@@/,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

"""
__VERSION__ = "3-b2.1"
__DATE__ = "03/May/2023"

import itertools
import time
from dataclasses import dataclass, InitVar, asdict, field
from typing import Any, Union, Optional
from typing import List, Dict, Tuple
from _decimal import Decimal

from fastlane_bot.db.manager import DatabaseManager
# from fastlane_bot.db.models import Pool, Token
from fastlane_bot.helpers import (
    TxSubmitHandler, TxSubmitHandlerBase,
    TxReceiptHandler, TxReceiptHandlerBase,
    TxRouteHandler, TxRouteHandlerBase,
    TxHelpers, TxHelpersBase,
    TradeInstruction, Univ3Calculator
)
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
from fastlane_bot.tools.optimizer import CPCArbOptimizer
import fastlane_bot.db.models as models
from fastlane_bot.config import Config
from .db.mock_model_managers import MockDatabaseManager
from .helpers.txhelpers import TxHelper
from .utils import num_format


# errorlogger = self.ConfigObj.logger.error
# errorlogger = self.ConfigObj.logger.debug # TODO: REMOVE THIS

@dataclass
class CarbonBotBase():
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

    db: DatabaseManager = field(init=False)
    TxSubmitHandler: any = None
    TxReceiptHandlerClass: any = None
    TxRouteHandlerClass: any = None
    TxHelpersClass: any = None
    ConfigObj: Config = None

    genesis_data: InitVar = None  # DEPRECATED; WILL BE REMOVED SOON
    drop_tables: InitVar = False  # STAYS
    seed_pools: InitVar = False  # anything else WILL raise
    update_pools: InitVar = False  # anything else WILL raise

    usd_gas_limit: int = 150
    min_profit: int = 60
    polling_interval: int = None

    def __post_init__(self, genesis_data=None, drop_tables=None, seed_pools=None, update_pools=None):
        """
        The post init method.
        """

        if genesis_data is not None:
            self.ConfigObj.logger.warning(
                "WARNING: genesis_data is deprecated. This argument will be removed soon"
            )
        if self.ConfigObj is None:
            self.ConfigObj = Config()

        self.c = self.ConfigObj

        assert self.polling_interval is None, "polling_interval is now a parameter to run"

        if self.TxSubmitHandler is None:
            self.TxSubmitHandler = TxSubmitHandler(ConfigObj=self.ConfigObj)
        assert issubclass(self.TxSubmitHandler.__class__,
                          TxSubmitHandlerBase), f"TxSubmitHandler not derived from TxSubmitHandlerBase {self.TxSubmitHandler.__class__}"

        if self.TxReceiptHandlerClass is None:
            self.TxReceiptHandlerClass = TxReceiptHandler
        assert issubclass(self.TxReceiptHandlerClass,
                          TxReceiptHandlerBase), f"TxReceiptHandlerClass not derived from TxReceiptHandlerBase {self.TxReceiptHandlerClass}"

        if self.TxRouteHandlerClass is None:
            self.TxRouteHandlerClass = TxRouteHandler  # (ConfigObj=self.ConfigObj)
        assert issubclass(self.TxRouteHandlerClass,
                          TxRouteHandlerBase), f"TxRouteHandlerClass not derived from TxRouteHandlerBase {self.TxRouteHandlerClass}"

        if self.TxHelpersClass is None:
            self.TxHelpersClass = TxHelpers(ConfigObj=self.ConfigObj)
        assert issubclass(self.TxHelpersClass.__class__,
                          TxHelpersBase), f"TxHelpersClass not derived from TxHelpersBase {self.TxHelpersClass}"

        if self.ConfigObj.DATABASE == self.ConfigObj.DATABASE_UNITTEST:
            self.db = MockDatabaseManager(ConfigObj=self.ConfigObj)
        else:
            self.db = DatabaseManager(ConfigObj=self.ConfigObj)
        # if self.db is None:
        #     self.db = DatabaseManager(
        #         data=self.genesis_data, ConfigObj=self.ConfigObj
        #     )

    @property
    def C(self) -> Any:
        """
        Convenience method self.ConfigObj
        """
        return self.ConfigObj

    def versions(self):
        """
        Returns the versions of the module and its Carbon dependencies.
        """
        s = [f"fastlane_bot v{__VERSION__} ({__DATE__})"]
        s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(CPC)]
        s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer)]
        return s

    # def update_pools(self, drop_tables: bool = False):
    #     """convenience method for db.update_pools()"""
    #     self.db.update_pools(drop_tables=drop_tables)

    UDTYPE_FROM_CONTRACTS = "from_contracts"
    UDTYPE_FROM_EVENTS = "from_events"

    def update(self, udtype=None, *, drop_tables=False, top_n: int = None, only_carbon: bool = True, bypairs: List[str] = None):
        """
        convenience access to the db.update methods

        :udtype:            UDTYPE_FROM_CONTRACTS or UDTYPE_FROM_EVENTS
        :drop_tables:       if True, drops all tables before updating
        :top_n:             if not None, only updates the top n pools
        :only_carbon:       if True, only updates carbon pools and other exchanges that are carbon-pool compatible pairs
        """
        raise NotImplementedError("update() is deprecated. Use `python run_db_update_w_heartbeat.py` instead")
        # self.c.logger.info(f"starting update(udtype={udtype}, "
        #                    f"drop_tables={drop_tables}, "
        #                    f"top_n={top_n}, "
        #                    f"only_carbon={only_carbon}"
        #                    f"bypairs={bypairs})")

        # if udtype is None:
        #     udtype = self.UDTYPE_FROM_CONTRACTS
        #
        # if drop_tables:
        #     self.db.drop_all_tables()
        #
        # if udtype == self.UDTYPE_FROM_CONTRACTS:
        #     # return self.db.update_pools_from_contracts(bypairs=bypairs)
        #     pass
        # elif udtype == self.UDTYPE_FROM_EVENTS:
        #     return self.db.update_pools_from_events()
        # else:
        #     raise ValueError(f"Invalid udtype {udtype}")

    def drop_all_tables(self):
        """convenience method for db.drop_all_tables()"""
        self.db.drop_all_tables()

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
        #self.ConfigObj.logger.debug(f"ADDRDEC {ADDRDEC}")
        for p in pools_and_tokens:
            try:
                p.ADDRDEC = ADDRDEC
                curves += p.to_cpc()
                # time.sleep(0.00000001)  # to avoid unstable results
            except ZeroDivisionError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n")
                #raise
            except CPC.CPCValidationError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n")
                #raise
            except TypeError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX DECIMAL ERROR CURVE {p} [{e}]\n")
                # if not str(e).startswith("1unsupported operand type(s) for"):
                    # raise
            except p.DoubleInvalidCurveError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX DOUBLE INVALID CURVE {p} [{e}]\n")
                #raise
            except Univ3Calculator.DecimalsMissingError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX DECIMALS MISSING [{e}]\n")
                #raise
            except Exception as e:
                self.ConfigObj.logger.error(f"[get_curves] error converting pool to curve {p}\n[ERR={e}]\n\n")
                #raise

        return CPCContainer(curves)


@dataclass
class CarbonBot(CarbonBotBase):
    """
    A class that handles the business logic of the bot.

    MAIN ENTRY POINTS
    :run:               Runs the bot.
    """

    def __post_init__(self, genesis_data=None, drop_tables=None, seed_pools=None, update_pools=None):
        super().__post_init__(genesis_data=genesis_data, drop_tables=drop_tables, seed_pools=seed_pools,
                              update_pools=update_pools)

    class NoArbAvailable(Exception): pass
    def _simple_ordering_by_src_token(self, best_trade_instructions_dic, best_src_token):
        '''
        Reorders a trade_instructions_dct so that all items where the best_src_token is the tknin are before others
        '''
        if best_trade_instructions_dic is None:
            raise self.NoArbAvailable(f"[_simple_ordering_by_src_token] {best_trade_instructions_dic}")
        src_token_instr = [x for x in best_trade_instructions_dic if x['tknin'] == best_src_token]
        non_src_token_instr = [x for x in best_trade_instructions_dic if x['tknin'] != best_src_token]
        ordered_trade_instructions_dct = src_token_instr + non_src_token_instr

        tx_in_count = len(src_token_instr)
        return ordered_trade_instructions_dct, tx_in_count

    def _basic_scaling(self, best_trade_instructions_dic, best_src_token):
        '''
        For items in the trade_instruction_dic scale the amtin by 0.999 if its the src_token
        '''
        scaled_best_trade_instructions_dic = []
        for x in best_trade_instructions_dic:
            scaled_best_trade_instructions_dic += [{k: v for k, v in x.items()}]

        for i in range(len(scaled_best_trade_instructions_dic)):
            if scaled_best_trade_instructions_dic[i]["tknin"] == best_src_token:
                scaled_best_trade_instructions_dic[i]["amtin"] *= 0.999
#             else:
#                 scaled_best_trade_instructions_dic[i]["amtin"] *= 0.99

        return scaled_best_trade_instructions_dic

    def _drop_error(self, trade_instructions_dct):
        new_dict = []
        for i in range(len(trade_instructions_dct)):
            new_dict += [{k: v for k, v in trade_instructions_dct[i].items() if k != 'error'}]
        return new_dict

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
        result = ({**ti, "raw_txs": "[]", "pair_sorting": "", "ConfigObj": self.ConfigObj, "db": self.db} for ti in
                  errorless_trade_instructions_dic if ti is not None)
        result = [TradeInstruction(**ti) for ti in result]
        return result

    def _check_if_carbon(self, cid: str):  # -> tuple[bool, str, str]:
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

    def _check_if_not_carbon(self, cid: str):  # -> tuple[bool, str, str]:
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

    AO_TOKENS = "tokens"
    AO_CANDIDATES = "candidates"

    def _find_arbitrage_opportunities(
            self, flashloan_tokens: List[str], CCm: CPCContainer, *, mode: str = "bothin", result=None,
    ):  # -> Union[tuple[Any, list[tuple[Any, Any]]], list[Any], tuple[
        # Union[int, Decimal, Decimal], Optional[Any], Optional[Any], Optional[Any], Optional[Any]]]:
        """
        Finds the arbitrage opportunities.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: CPCContainer
            The CPCContainer object.
        result: AO_XXX or None
            What (intermediate) result to return.
            mode: str
            The mode.

        Returns
        -------
        Tuple[Decimal, List[Dict[str, Any]]]
            The best profit and the trade instructions.
        """
        assert mode == "bothin", "parameter not used"
        # c.logger.debug("[_find_arbitrage_opportunities] Number of curves:", len(CCm))
        best_profit = 0
        best_src_token = None
        best_trade_instructions = None
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        # flashloan_tokens_intersect = [T.BNT, ]
        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect)
            # tkn1 is always the token being flash loaned
            # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
            if tkn0 != tkn1
        ]
        if result == self.AO_TOKENS:
            return all_tokens, combos

        ops = (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions
        )

        candidates = []
        for tkn0, tkn1 in combos:
            # try:
            r = None
            #c.logger.debug(f"Checking flashloan token = {tkn1}, other token = {tkn0}")
            CC = CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue
            O = CPCArbOptimizer(CC)
            src_token = tkn1
            try:
                pstart = ({tkn0: CCm.bypairs(f"{tkn0}/{tkn1}")[0].p})
                r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
                assert not r.is_error
            except Exception as e:
                # c.logger.debug(e, r)
                try:
                    r = O.margp_optimizer(src_token)
                    assert not r.is_error
                except Exception as e:
                    # c.logger.info(e)
                    continue
            try:
                profit_src = -r.result
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions = r.trade_instructions()
            except:
                continue

            cids = [ti['cid'] for ti in trade_instructions_dic]
            quote_token = "ETH-EEeE" if src_token == "WETH-6Cc2" else src_token

            try:
                profit = self.db.get_bnt_price_from_tokens(profit_src, src_token)
            except Exception as e:
                self.ConfigObj.logger.error("[TODO CLEAN UP]{e}")
                profit = profit_src

            self.ConfigObj.logger.info(f"Profit in bnt: {profit} {cids}")
            # candidates += [(profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]
            contains_carbon = any(
                self._check_if_carbon(ti['cid'])[0]
                for ti in trade_instructions_dic
            )
            contains_other = any(
                self._check_if_not_carbon(ti['cid'])
                for ti in trade_instructions_dic
            )
            try:
                netchange = trade_instructions_df.iloc[-1]
            except Exception as e:
                netchange = [500] #an arbitrary large number

            bnt_gas_limit = self.db.get_bnt_price_from_tokens(self.usd_gas_limit, 'USDC')
            self.ConfigObj.logger.debug(f"bnt_gas_limit: {bnt_gas_limit}")
            condition_6 = False
            if profit > (self.min_profit + bnt_gas_limit):
                condition_6 = True

            if len(trade_instructions_df) > 0:
                condition_1 = (profit > best_profit)
                self.ConfigObj.logger.debug(f"profit > best_profit: {condition_1}")
                # ordered_scaled_dcts, tx_in_count = self._order_and_scale_trade_instruction_dcts(
                #     trade_instructions_df, trade_instructions_dic, src_token)

                # condition_5 = tx_in_count > 0

                self.ConfigObj.logger.debug(f"profit > best_profit: {condition_1}")
                condition_2 = contains_carbon
                self.ConfigObj.logger.debug(f"contains_carbon: {condition_2}")
                condition_3 = max(netchange) < 1e-4

                self.ConfigObj.logger.debug(f"max(netchange)<1e-4: {condition_3}")
                # self.ConfigObj.logger.debug(f"contains_other: {condition_4}")
                # self.ConfigObj.logger.debug(f"tx_in_count > 0: {condition_5}")
                if condition_3:
                    candidates += [
                        (profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]

                if condition_1 and condition_2 and condition_3 and condition_6:
                    self.ConfigObj.logger.debug("*************")
                    self.ConfigObj.logger.debug(f"New best profit: {profit}")

                    best_profit = profit
                    best_src_token = src_token
                    best_trade_instructions_df = trade_instructions_df
                    best_trade_instructions_dic = trade_instructions_dic
                    best_trade_instructions = trade_instructions

                    self.ConfigObj.logger.debug(f"best_trade_instructions_df: {best_trade_instructions_df}")

                    ops = (
                        best_profit,
                        best_trade_instructions_df,
                        best_trade_instructions_dic,
                        best_src_token,
                        best_trade_instructions
                    )
                    self.ConfigObj.logger.debug("*************")
            # except Exception as e:
            #     self.ConfigObj.logger.debug(f"Error in opt: {e}")
            #     continue

        return candidates if result == self.AO_CANDIDATES else ops

    def _find_arbitrage_opportunities_carbon_multi_pairwise(
            self, flashloan_tokens: List[str], CCm: CPCContainer, *, mode: str = "bothin", result=None,
    ):  # -> Union[tuple[Any, list[tuple[Any, Any]]], list[Any], tuple[
        # Union[int, Decimal, Decimal], Optional[Any], Optional[Any], Optional[Any], Optional[Any]]]:
        """
        Finds the pair-wise arbitrage opportunities for individual carbon orders.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: CPCContainer
            The CPCContainer object.
        result: AO_XXX or None
            What (intermediate) result to return.
            mode: str
            The mode.

        Returns
        -------
        Tuple[Decimal, List[Dict[str, Any]]]
            The best profit and the trade instructions.
        """
        assert mode == "bothin", "parameter not used"
        # c.logger.debug("[_find_arbitrage_opportunities] Number of curves:", len(CCm))
        best_profit = 0
        best_src_token = None
        best_trade_instructions = None
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
        ops = (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions
        )

        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect)
            # tkn1 is always the token being flash loaned
            # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
            if tkn0 != tkn1
        ]
        if result == self.AO_TOKENS:
            return all_tokens, combos

        candidates = []
        for tkn0, tkn1 in combos:
            r = None
            self.C.logger.debug(f"Checking flashloan token = {tkn1}, other token = {tkn0}")
            CC = CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue
            carbon_curves = [x for x in CC.curves if x.params.exchange=='carbon_v1']
            not_carbon_curves = [x for x in CC.curves if x.params.exchange!='carbon_v1']
            #curve_combos = list(itertools.product(not_carbon_curves, carbon_curves)) #combos 1 carbon curve w non_carbon
            curve_combos = [[curve] + carbon_curves for curve in not_carbon_curves]
            # for curve in not_carbon_curves:
            #     combo = [curve] + carbon_curves
            #     curve_combos.append(combo)

            # self.ConfigObj.logger.info(f"\n\ncurve combos: type={type(curve_combos)}, \nprint:{curve_combos}")

            for curve_combo in curve_combos:
                CC_cc = CPCContainer(curve_combo)
                O = CPCArbOptimizer(CC_cc)
                src_token = tkn1
                try:
                    pstart = ({tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p}) #this intentionally selects the non_carbon curve
                    r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
                    profit_src = -r.result
                    trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)

                    """
                    1 Determine correct direction - opposite of non-Carbon pool
                    2 Get cids of wrong-direction Carbon pools
                    3 Create new CPCContainer with correct pools
                    4 Rerun optimizer
                    5 Resume normal flow
                    """

                    curve0 = curve_combo[0]
                    self.ConfigObj.logger.info(f"\ntrade_instructions_df: {trade_instructions_df.to_string()}")
                    # with trade_instructions_df.option_context('display.max_rows', None, 'display.max_columns',
                    #                        None):  # more options can be specified also
                    #     print(trade_instructions_df)

                    cids = [curve.cid for curve in curve_combo]


                    non_carbon_cids = [curve.cid for curve in curve_combo if curve.params.get('exchange') != "carbon_v1"]

                    tkn0_in: bool
                    #self.ConfigObj.logger.info(f"\nnon_carbon_cid: {non_carbon_cids[0]} - index {trade_instructions_df.loc[non_carbon_cids[0]]}")

                    non_carbon_row = trade_instructions_df.loc[non_carbon_cids[0]]
                    # self.ConfigObj.logger.info(
                    #     f"analysis of row: type: {type(non_carbon_row)}, length:{len(non_carbon_row)}, row0:{non_carbon_row[0]}, row1:{non_carbon_row[1]}")

                    tkn0_into_carbon = True if non_carbon_row[0] < 0 else False
                    wrong_direction_cids = []

                    for idx, row in trade_instructions_df.iterrows():
                        if "-0" in idx or "-1" in idx:
                            if (tkn0_into_carbon and row[0] < 0) or (not tkn0_into_carbon and row[0] > 0):
                                wrong_direction_cids.append(idx)

                        # self.ConfigObj.logger.info(
                        #     f"analysis in iterrows: idx: {idx}, length:{len(row)}, row0:{row[0]}, row1:{row[1]}")
                    self.ConfigObj.logger.info(f"wrong direction cids: {wrong_direction_cids}")
                    # self.ConfigObj.logger.info(
                    #     f"index of non carbon: {trade_instructions_df.loc[non_carbon_cids[0]]}")

                    if len(non_carbon_cids) > 0 and len(wrong_direction_cids) > 0:
                        self.ConfigObj.logger.info(f"Removing wrong direction pools & rerunning optimizer")

                        new_curves = [curve for curve in curve_combo if curve.cid not in wrong_direction_cids]

                        CC_cc = CPCContainer(new_curves)
                        O = CPCArbOptimizer(CC_cc)
                        pstart = ({tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p}) #this intentionally selects the non_carbon curve
                        r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
                        profit_src = -r.result
                        trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)


                    # self.ConfigObj.logger.info(f"Non Carbon cids: {non_carbon_cids}")



                    # for idx, row in trade_instructions_df.iterrows():




                    # self.ConfigObj.logger.info(f"dataframe cids: {trade_instructions_df}")


                    # tkn0_into_carbon: bool =

                    ## If 1+ Carbon curve in wrong direction, need to drop it and resolve /w optimizer##



                    trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                    trade_instructions = r.trade_instructions()

                    self.ConfigObj.logger.debug(f"\n\ntrade_instructions_df={trade_instructions_df}\ntrade_instructions_dic={trade_instructions_dic}\ntrade_instructions={trade_instructions}\n\n")


                except:
                    continue

                cids = [ti['cid'] for ti in trade_instructions_dic]
                quote_token = "ETH-EEeE" if src_token == "WETH-6Cc2" else src_token

                try:
                    profit = self.db.get_bnt_price_from_tokens(profit_src, src_token)
                except Exception as e:
                    self.ConfigObj.logger.error(f"[TODO CLEAN UP]{e}")
                    profit = profit_src

                self.ConfigObj.logger.debug(f"Profit in bnt: {num_format(profit)} {cids}")
                try:
                    netchange = trade_instructions_df.iloc[-1]
                except Exception as e:
                    netchange = [500] #an arbitrary large number

                # bnt_gas_limit = self.db.get_bnt_price_from_tokens(self.usd_gas_limit, 'USDC')
                # self.ConfigObj.logger.debug(f"bnt_gas_limit: {bnt_gas_limit}")
                # condition_profit = False
                # if profit > (self.min_profit + bnt_gas_limit):
                #     condition_profit = True

                if len(trade_instructions_df) > 0:
                    condition_better_profit = (profit > best_profit)
                    self.ConfigObj.logger.debug(f"profit > best_profit: {condition_better_profit}")
                    condition_zeros_one_token = max(netchange) < 1e-4
                    self.ConfigObj.logger.debug(f"max(netchange)<1e-4: {condition_zeros_one_token}")

                    if condition_zeros_one_token: #candidate regardless if profitable
                        candidates += [
                            (profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]

                    if condition_better_profit and condition_zeros_one_token:
                        self.ConfigObj.logger.debug("*************")
                        self.ConfigObj.logger.debug(f"New best profit: {profit}")

                        best_profit = profit
                        best_src_token = src_token
                        best_trade_instructions_df = trade_instructions_df
                        best_trade_instructions_dic = trade_instructions_dic
                        best_trade_instructions = trade_instructions

                        self.ConfigObj.logger.debug(f"best_trade_instructions_df: {best_trade_instructions_df}")

                        ops = (
                            best_profit,
                            best_trade_instructions_df,
                            best_trade_instructions_dic,
                            best_src_token,
                            best_trade_instructions
                        )
                        self.ConfigObj.logger.debug("*************")
                # except Exception as e:
                #     self.ConfigObj.logger.debug(f"Error in opt: {e}")
                #     continue
        self.ConfigObj.logger.info(
            f"\n\n***BEST Multi***\ntrade_instructions_df={best_trade_instructions_df}\ntrade_instructions_dic={best_trade_instructions_dic}\ntrade_instructions={best_trade_instructions}\nsrc={best_src_token}\n")
        return candidates if result == self.AO_CANDIDATES else ops
    def _find_arbitrage_opportunities_carbon_single_pairwise(
            self, flashloan_tokens: List[str], CCm: CPCContainer, *, mode: str = "bothin", result=None,
    ):  # -> Union[tuple[Any, list[tuple[Any, Any]]], list[Any], tuple[
        # Union[int, Decimal, Decimal], Optional[Any], Optional[Any], Optional[Any], Optional[Any]]]:
        """
        Finds the pair-wise arbitrage opportunities for individual carbon orders.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: CPCContainer
            The CPCContainer object.
        result: AO_XXX or None
            What (intermediate) result to return.
            mode: str
            The mode.

        Returns
        -------
        Tuple[Decimal, List[Dict[str, Any]]]
            The best profit and the trade instructions.
        """
        assert mode == "bothin", "parameter not used"
        # c.logger.debug("[_find_arbitrage_opportunities] Number of curves:", len(CCm))
        best_profit = 0
        best_src_token = None
        best_trade_instructions = None
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
        ops = (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions
        )

        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect)
            # tkn1 is always the token being flash loaned
            # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
            if tkn0 != tkn1
        ]
        if result == self.AO_TOKENS:
            return all_tokens, combos

        candidates = []
        for tkn0, tkn1 in combos:
            r = None
            self.C.logger.debug(f"Checking flashloan token = {tkn1}, other token = {tkn0}")
            CC = CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue
            carbon_curves = [x for x in CC.curves if x.params.exchange=='carbon_v1']
            not_carbon_curves = [x for x in CC.curves if x.params.exchange!='carbon_v1']
            curve_combos = list(itertools.product(not_carbon_curves, carbon_curves)) #combos 1 carbon curve w non_carbon

            for curve_combo in curve_combos:
                CC_cc = CPCContainer(curve_combo)
                O = CPCArbOptimizer(CC_cc)
                src_token = tkn1
                try:
                    pstart = ({tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p}) #this intentially selects the non_carbon curve
                    r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
                    profit_src = -r.result
                    trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                    trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                    trade_instructions = r.trade_instructions()
                    self.ConfigObj.logger.info(
                        f"\n\ntrade_instructions_df={trade_instructions_df}\ntrade_instructions_dic={trade_instructions_dic}\ntrade_instructions={trade_instructions}\n\n")
                except:
                    continue

                cids = [ti['cid'] for ti in trade_instructions_dic]
                quote_token = "ETH-EEeE" if src_token == "WETH-6Cc2" else src_token

                try:
                    profit = self.db.get_bnt_price_from_tokens(profit_src, src_token)
                except Exception as e:
                    self.ConfigObj.logger.error(f"[TODO CLEAN UP]{e}")
                    profit = profit_src

                self.ConfigObj.logger.debug(f"Profit in bnt: {num_format(profit)} {cids}")
                try:
                    netchange = trade_instructions_df.iloc[-1]
                except Exception as e:
                    netchange = [500] #an arbitrary large number

                # bnt_gas_limit = self.db.get_bnt_price_from_tokens(self.usd_gas_limit, 'USDC')
                # self.ConfigObj.logger.debug(f"bnt_gas_limit: {bnt_gas_limit}")
                # condition_profit = False
                # if profit > (self.min_profit + bnt_gas_limit):
                #     condition_profit = True

                if len(trade_instructions_df) > 0:
                    condition_better_profit = (profit > best_profit)
                    self.ConfigObj.logger.debug(f"profit > best_profit: {condition_better_profit}")
                    condition_zeros_one_token = max(netchange) < 1e-4
                    self.ConfigObj.logger.debug(f"max(netchange)<1e-4: {condition_zeros_one_token}")

                    if condition_zeros_one_token: #candidate regardless if profitable
                        candidates += [
                            (profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]

                    if condition_better_profit and condition_zeros_one_token:
                        self.ConfigObj.logger.debug("*************")
                        self.ConfigObj.logger.debug(f"New best profit: {profit}")

                        best_profit = profit
                        best_src_token = src_token
                        best_trade_instructions_df = trade_instructions_df
                        best_trade_instructions_dic = trade_instructions_dic
                        best_trade_instructions = trade_instructions

                        self.ConfigObj.logger.debug(f"best_trade_instructions_df: {best_trade_instructions_df}")

                        ops = (
                            best_profit,
                            best_trade_instructions_df,
                            best_trade_instructions_dic,
                            best_src_token,
                            best_trade_instructions
                        )
                        self.ConfigObj.logger.debug("*************")
                # except Exception as e:
                #     self.ConfigObj.logger.debug(f"Error in opt: {e}")
                #     continue
        self.ConfigObj.logger.info(
            f"\n\ntrade_instructions_df={best_trade_instructions_df}\ntrade_instructions_dic={best_trade_instructions_dic}\ntrade_instructions={best_trade_instructions}\nsrc={best_src_token}\n")
        return candidates if result == self.AO_CANDIDATES else ops


    def _find_arbitrage_opportunities_carbon_single_triangle(
            self, flashloan_tokens: List[str], CCm: CPCContainer, *, mode: str = "bothin", result=None,
    ):  # -> Union[tuple[Any, list[tuple[Any, Any]]], list[Any], tuple[
        # Union[int, Decimal, Decimal], Optional[Any], Optional[Any], Optional[Any], Optional[Any]]]:
        """
        Finds the triangle arbitrage opportunities for individual carbon orders.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: CPCContainer
            The CPCContainer object.
        result: AO_XXX or None
            What (intermediate) result to return.
            mode: str
            The mode.

        Returns
        -------
        Tuple[Decimal, List[Dict[str, Any]]]
            The best profit and the trade instructions.
        """
        assert mode == "bothin", "parameter not used"
        # c.logger.debug("[_find_arbitrage_opportunities] Number of curves:", len(CCm))

        best_profit = 0
        best_src_token = None
        best_trade_instructions = None
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
        ops = (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions
        )
        candidates = []
        all_miniverses = []
        all_carbon_curves = CCm.byparams(exchange='carbon_v1').curves

        for flt in flashloan_tokens: # may wish to run this for one flt at a time
            non_flt_carbon_curves = [x for x in all_carbon_curves if flt not in x.pair]
            for i in range(len(non_flt_carbon_curves)):
                target_tkny = non_flt_carbon_curves[i].tkny
                target_tknx = non_flt_carbon_curves[i].tknx
                carbon_curves = CCm.bypairs(f"{target_tknx}/{target_tkny}").byparams(exchange='carbon_v1').curves
                y_match_curves = CCm.bypairs(set(CCm.filter_pairs(onein=target_tknx)) & set(CCm.filter_pairs(onein=flt)))
                x_match_curves = CCm.bypairs(set(CCm.filter_pairs(onein=target_tkny)) & set(CCm.filter_pairs(onein=flt)))
                y_match_curves_not_carbon = [x for x in y_match_curves if x.params.exchange!='carbon_v1']
                x_match_curves_not_carbon = [x for x in x_match_curves if x.params.exchange!='carbon_v1']
                miniverses = list(itertools.product(y_match_curves_not_carbon, carbon_curves, x_match_curves_not_carbon))
                if len(miniverses) > 0:
                    all_miniverses += list(zip([flt] * len(miniverses), miniverses))
                    # print(flt, target_tkny, target_tknx, len(miniverses))
                    
        for src_token, miniverse in all_miniverses:
            r = None
            self.C.logger.debug(f"Checking flashloan token = {src_token}, miniverse = {miniverse}")
            CC_cc = CPCContainer(miniverse)
            O = CPCArbOptimizer(CC_cc)
            try:
                r = O.margp_optimizer(src_token)
                profit_src = -r.result
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions = r.trade_instructions()
            except:
                continue

            cids = [ti['cid'] for ti in trade_instructions_dic]
            quote_token = "ETH-EEeE" if src_token == "WETH-6Cc2" else src_token

            try:
                profit = self.db.get_bnt_price_from_tokens(profit_src, src_token)
            except Exception as e:
                self.ConfigObj.logger.error(f"[TODO CLEAN UP]{e}")
                profit = profit_src

            self.ConfigObj.logger.debug(f"Profit in bnt: {profit} {cids}")
            try:
                netchange = trade_instructions_df.iloc[-1]
            except Exception as e:
                netchange = [500] #an arbitrary large number

            if len(trade_instructions_df) > 0:
                condition_better_profit = (profit > best_profit)
                self.ConfigObj.logger.debug(f"profit > best_profit: {condition_better_profit}")
                condition_zeros_one_token = max(netchange) < 1e-4
                self.ConfigObj.logger.debug(f"max(netchange)<1e-4: {condition_zeros_one_token}")

                if condition_zeros_one_token: #candidate regardless if profitable
                    candidates += [
                        (profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]

                if condition_better_profit and condition_zeros_one_token:
                    self.ConfigObj.logger.debug("*************")
                    self.ConfigObj.logger.debug(f"New best profit: {profit}")

                    best_profit = profit
                    best_src_token = src_token
                    best_trade_instructions_df = trade_instructions_df
                    best_trade_instructions_dic = trade_instructions_dic
                    best_trade_instructions = trade_instructions

                    self.ConfigObj.logger.debug(f"best_trade_instructions_df: {best_trade_instructions_df}")

                    ops = (
                        best_profit,
                        best_trade_instructions_df,
                        best_trade_instructions_dic,
                        best_src_token,
                        best_trade_instructions
                    )
                    self.ConfigObj.logger.debug("*************")
            # except Exception as e:
            #     self.ConfigObj.logger.debug(f"Error in opt: {e}")
            #     continue

        return candidates if result == self.AO_CANDIDATES else ops


    def _get_deadline(self) -> int:
        """
        Gets the deadline for a transaction.

        Returns
        -------
        int
            The deadline (as UNIX epoch).
        """
        return (
                self.ConfigObj.w3.eth.getBlock(
                    self.ConfigObj.w3.eth.block_number).timestamp + self.ConfigObj.DEFAULT_BLOCKTIME_DEVIATION
        )

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
    def _run(
            self, flashloan_tokens: List[str], CCm: CPCContainer, *, result=None, arb_mode:str = None
    ) -> Optional[Tuple[str, List[Any]]]:
        """
        Working-level entry point for run(), performing the actual execution.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens, ie all tokens that can be borrowed.
        CCm: CPCContainer
            The CPCContainer object containing all market curves.
        result: XS_XXX or None
            What intermediate result to return (default: None)
        arb_mode: AM_REGULAR or AM_SINGLE
            What way to search arbs, 'single' is carbon single pair-wise
        Returns
        -------
        str
            The transaction hash.
        """
        ## Find arbitrage opportunities
        #arb_mode = self.AM_SINGLE if arb_mode is None else arb_mode
        arb_mode = self.AM_MULTI if arb_mode is None else arb_mode
        if arb_mode == self.AM_REGULAR:
            r = self._find_arbitrage_opportunities(flashloan_tokens, CCm)
        elif arb_mode == self.AM_SINGLE:
            r = self._find_arbitrage_opportunities_carbon_single_pairwise(flashloan_tokens, CCm)
        elif arb_mode == self.AM_TRIANGLE:
            r = self._find_arbitrage_opportunities_carbon_single_triangle(flashloan_tokens, CCm)
        elif arb_mode == self.AM_MULTI:
            r = self._find_arbitrage_opportunities_carbon_multi_pairwise(flashloan_tokens, CCm)
        else:
            raise ValueError(f"arb_mode not recognised {arb_mode}") 
        
        if result == self.XS_ARBOPPS:
            return r
        (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        ) = r

        # Order the trades instructions suitable for routing and scale the amounts
        ordered_trade_instructions_dct, tx_in_count = self._simple_ordering_by_src_token(best_trade_instructions_dic,
                                                                                         best_src_token)
        ordered_scaled_dcts = self._basic_scaling(ordered_trade_instructions_dct, best_src_token)
        if result == self.XS_ORDSCAL:
            return ordered_scaled_dcts

        ## Convert opportunities to trade instructions
        ordered_trade_instructions_objects = self._convert_trade_instructions(ordered_scaled_dcts)
        if result == self.XS_TI:
            return ordered_trade_instructions_objects

        ## Aggregate trade instructions
        tx_route_handler = self.TxRouteHandlerClass(trade_instructions=ordered_trade_instructions_objects)

        calculated_trade_instructions = tx_route_handler.calculate_trade_outputs(ordered_trade_instructions_objects)

        if result == self.XS_EXACT:
            return calculated_trade_instructions

        fl_token = calculated_trade_instructions[0].tknin_key
        if (fl_token == 'WETH-6Cc2'):
            fl_token = "ETH-EEeE"
        try:
            best_profit = calculated_trade_instructions[-1].amtout - calculated_trade_instructions[0].amtin
            best_profit = self.db.get_bnt_price_from_tokens(best_profit, tkn=fl_token)
            self.ConfigObj.logger.debug(f"updated best_profit after calculating exact trade numbers: {num_format(best_profit)}")
        except Exception as e:
            self.ConfigObj.logger.error(f"[Failed to update profit in BNT for price of token: {fl_token}] error:{e}")

        if best_profit < self.ConfigObj.DEFAULT_MIN_PROFIT:
            self.ConfigObj.logger.info(f"Opportunity with profit: {num_format(best_profit)} does not meet minimum profit: {self.ConfigObj.DEFAULT_MIN_PROFIT}, discarding.")
            return (None, None)

        agg_trade_instructions = tx_route_handler._aggregate_carbon_trades(
            trade_instructions_objects=calculated_trade_instructions
        )
        del ordered_trade_instructions_objects  # TODO: REMOVE THIS
        if result == self.XS_AGGTI:
            return agg_trade_instructions

        # Get the flashloan amount
        flashloan_amount = int(sum(agg_trade_instructions[i].amtin_wei for i in range(tx_in_count)))

        # Get the flashloan token and verify
        # fl_token = agg_trade_instructions[0].tknin_key
        is_carbon = True if agg_trade_instructions[0].raw_txs != [] else False
        # print(fl_token, agg_trade_instructions[0].raw_txs, is_carbon)

        # elif (fl_token == 'WETH-6Cc2') and not is_carbon:
        # else:
        #     raise ValueError("Flashloan WETH not yet supported")
        flashloan_token_address = self.ConfigObj.w3.toChecksumAddress(
            self.db.get_token(key=fl_token).address
        )

        self.ConfigObj.logger.debug(f"flashloan_amount: {flashloan_amount}")
        if result == self.XS_ORDINFO:
            return agg_trade_instructions, flashloan_amount, flashloan_token_address

        ## Encode trade instructions
        encoded_trade_instructions = tx_route_handler.custom_data_encoder(agg_trade_instructions)
        if result == self.XS_ENCTI:
            return encoded_trade_instructions

        ## Determine route
        deadline = self._get_deadline()

        # Get the route struct
        route_struct = [
            asdict(rs) for rs in tx_route_handler.get_route_structs(
                encoded_trade_instructions, deadline
            )
        ]
        if result == self.XS_ROUTE:
            return route_struct, flashloan_amount, flashloan_token_address

        ## Submit transaction and obtain transaction receipt
        assert result is None, f"Unknown result requested {result}"

        # Get the cids of the trade instructions
        cids = list({ti['cid'].split('-')[0] for ti in best_trade_instructions_dic})

        if self.ConfigObj.NETWORK == self.ConfigObj.NETWORK_TENDERLY:
            return (self._validate_and_submit_transaction_tenderly(
                        ConfigObj = self.ConfigObj,
                        route_struct = route_struct,
                        src_amount = flashloan_amount,
                        src_address = flashloan_token_address,
                            ), cids)

        # log the flashloan arbitrage tx info
        self.ConfigObj.logger.debug(f"Flashloan amount: {flashloan_amount}")
        self.ConfigObj.logger.debug(f"Flashloan token address: {flashloan_token_address}")
        self.ConfigObj.logger.debug(f"Route Struct: \n {route_struct}")
        self.ConfigObj.logger.debug(f"Trade Instructions: \n {best_trade_instructions_dic}")
        # self.ConfigObj.logger.debug(f"Trade Instructions Objects: \n {ordered_trade_instructions_objects}")
        # self.ConfigObj.logger.debug(f"Aggregated Trade Instructions: \n {agg_trade_instructions}")





        pool = (
            self.db.get_pool(exchange_name=self.ConfigObj.BANCOR_V3_NAME, pair_name='BNT-FF1C/ETH-EEeE')
        )
        bnt_eth = (int(pool.tkn0_balance), int(pool.tkn1_balance))

        # Init TxHelpers
        tx_helpers = TxHelpers(ConfigObj=self.ConfigObj)
        # Submit tx
        return (tx_helpers.validate_and_submit_transaction(route_struct=route_struct, src_amt=flashloan_amount,
                                                          src_address=flashloan_token_address, bnt_eth=bnt_eth,
                                                          expected_profit=best_profit, safety_override=False, verbose=True), cids)


        # # Initialize tx helper
        # tx_helper = TxHelper(
        #     usd_gas_limit=self.usd_gas_limit,
        #     w3=self.ConfigObj.w3,
        #     gas_price_multiplier=self.gas_price_multiplier,
        #     arb_contract=self.ConfigObj.BANCOR_ARBITRAGE_CONTRACT
        # )
        # # Submit the transaction
        # return tx_helper.submit_flashloan_arb_tx(
        #     arb_data=route_struct,
        #     flashloan_token_address=flashloan_token_address,
        #     flashloan_amount=flashloan_amount,
        #     verbose=True,
        # ), cids

    def _validate_and_submit_transaction_tenderly(self, ConfigObj, route_struct, src_address, src_amount):
        tx_submit_handler = TxSubmitHandler(
            ConfigObj=ConfigObj,
            route_struct=route_struct,
            src_address=src_address,
            src_amount=src_amount,
        )
        self.ConfigObj.logger.debug(f"route_struct: {route_struct}")
        tx_details = tx_submit_handler._get_tx_details()
        # tx_submit_handler.token_contract.functions.approve(
        #     self.ConfigObj.w3.toChecksumAddress(self.ConfigObj.FASTLANE_CONTRACT_ADDRESS), 0
        # ).transact(tx_details)
        # tx_submit_handler.token_contract.functions.approve(
        #     self.ConfigObj.w3.toChecksumAddress(self.ConfigObj.FASTLANE_CONTRACT_ADDRESS), src_amount
        # ).transact(tx_details)
        self.ConfigObj.logger.debug("src_address", src_address)
        tx = tx_submit_handler._submit_transaction_tenderly(
            route_struct=route_struct,
            src_address=src_address,
            src_amount=src_amount
        )
        return self.ConfigObj.w3.eth.wait_for_transaction_receipt(tx)

    RUN_FLASHLOAN_TOKENS = [T.WETH, T.DAI, T.USDC, T.USDT, T.WBTC, T.BNT]
    RUN_SINGLE = "single"
    RUN_CONTINUOUS = "continuous"
    RUN_POLLING_INTERVAL = 60  # default polling interval in seconds

    def run(
            self,
            *,
            flashloan_tokens: List[str] = None,
            CCm: CPCContainer = None,
            polling_interval: int = None,
            mode: str = None,
    ) -> str:
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

        Returns
        -------
        str
            The transaction hash.
        """
        if mode is None:
            mode = self.RUN_CONTINUOUS
        assert mode in [self.RUN_SINGLE,
                        self.RUN_CONTINUOUS], f"Unknown mode {mode} [possible values: {self.RUN_SINGLE}, {self.RUN_CONTINUOUS}]"
        if self.polling_interval is None:
            self.polling_interval = polling_interval if polling_interval is not None else self.RUN_POLLING_INTERVAL

        if flashloan_tokens is None:
            flashloan_tokens = self.RUN_FLASHLOAN_TOKENS
        if CCm is None:
            CCm = self.get_curves()

        if mode == "continuous":
            while True:
                try:
                    CCm = self.get_curves()
                    tx_hash, cids = self._run(flashloan_tokens, CCm)
                    if tx_hash:
                        self.ConfigObj.logger.info(f"Arbitrage executed [hash={tx_hash}]")
                        self.db.update_recently_traded_pools(cids)

                    time.sleep(self.polling_interval)
                except self.NoArbAvailable as e:
                    self.ConfigObj.logger.debug(f"[bot:run:single] {e}")
                except Exception as e:
                    self.ConfigObj.logger.error(f"[bot:run:continuous] {e}")
                    time.sleep(self.polling_interval)
        else:
            try:
                tx_hash = self._run(flashloan_tokens=flashloan_tokens, CCm=CCm)
                self.ConfigObj.logger.info(f"Arbitrage executed [hash={tx_hash}]")
            except self.NoArbAvailable as e:
                self.ConfigObj.logger.warning(f"[NoArbAvailable] {e}")
            except Exception as e:
                self.ConfigObj.logger.error(f"[bot:run:single] {e}")
                raise
