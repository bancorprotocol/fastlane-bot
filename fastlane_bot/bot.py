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
    MB@RICHARDSON@BANCOR@(2023)@@@@@/,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

"""
__VERSION__ = "3-b2.2"
__DATE__ = "20/June/2023"

import random
import time
from _decimal import Decimal
from dataclasses import dataclass, InitVar, asdict, field
from typing import List, Dict, Tuple, Any, Callable
from typing import Optional

import fastlane_bot.config as c
from fastlane_bot.helpers import (
    TxSubmitHandler, TxSubmitHandlerBase,
    TxReceiptHandler, TxReceiptHandlerBase,
    TxRouteHandler, TxRouteHandlerBase,
    TxHelpers, TxHelpersBase, TradeInstruction, Univ3Calculator
)
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
from fastlane_bot.tools.optimizer import CPCArbOptimizer
from fastlane_bot.config import Config
from .data_fetcher.interface import QueryInterface
from .modes.pairwise_multi import FindArbitrageMultiPairwise
from .modes.pairwise_single import FindArbitrageSinglePairwise
from .modes.triangle_multi import ArbitrageFinderTriangleMulti
from .modes.triangle_single import ArbitrageFinderTriangleSingle
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

        self.db = QueryInterface(ConfigObj=self.ConfigObj)

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

    UDTYPE_FROM_CONTRACTS = "from_contracts"
    UDTYPE_FROM_EVENTS = "from_events"

    def update(self, udtype=None, *, drop_tables=False, top_n: int = None, only_carbon: bool = True,
               bypairs: List[str] = None):
        """
        convenience access to the db.update methods

        :udtype:            UDTYPE_FROM_CONTRACTS or UDTYPE_FROM_EVENTS
        :drop_tables:       if True, drops all tables before updating
        :top_n:             if not None, only updates the top n pools
        :only_carbon:       if True, only updates carbon pools and other exchanges that are carbon-pool compatible pairs
        """
        raise NotImplementedError("update() is deprecated. Use `python run_db_update_w_heartbeat.py` instead")

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
        for p in pools_and_tokens:
            try:
                p.ADDRDEC = ADDRDEC
                curves += p.to_cpc()
            except ZeroDivisionError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n")
            except CPC.CPCValidationError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n")
            except TypeError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX DECIMAL ERROR CURVE {p} [{e}]\n")
            except p.DoubleInvalidCurveError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX DOUBLE INVALID CURVE {p} [{e}]\n")
            except Univ3Calculator.DecimalsMissingError as e:
                self.ConfigObj.logger.error(f"[get_curves] MUST FIX DECIMALS MISSING [{e}]\n")
            except Exception as e:
                self.ConfigObj.logger.error(f"[get_curves] error converting pool to curve {p}\n[ERR={e}]\n\n")

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

    class NoArbAvailable(Exception):
        pass

    def _simple_ordering_by_src_token(self, best_trade_instructions_dic, best_src_token):
        """
        Reorders a trade_instructions_dct so that all items where the best_src_token is the tknin are before others
        """
        if best_trade_instructions_dic is None:
            raise self.NoArbAvailable(f"[_simple_ordering_by_src_token] {best_trade_instructions_dic}")
        src_token_instr = [x for x in best_trade_instructions_dic if x['tknin'] == best_src_token]
        non_src_token_instr = [x for x in best_trade_instructions_dic if x['tknin'] != best_src_token]
        ordered_trade_instructions_dct = src_token_instr + non_src_token_instr

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
                item["amtin"] *= 0.999
        #             else:
        #                 scaled_best_trade_instructions_dic[i]["amtin"] *= 0.99

        return scaled_best_trade_instructions_dic

    def _drop_error(self, trade_instructions_dct):
        return [
            {k: v for k, v in trade_instructions_dct[i].items() if k != 'error'}
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
    AM_MULTI_TRIANGLE = "multi_triangle"
    AM_BANCOR_V3 = "bancor_v3"

    @staticmethod
    def _get_arb_finder(arb_mode: str) -> Callable:
        if arb_mode in {'single', 'pairwise_single'}:
            return FindArbitrageSinglePairwise
        elif arb_mode in {'multi', 'pairwise_multi'}:
            return FindArbitrageMultiPairwise
        elif arb_mode in {'triangle', 'triangle_single'}:
            return ArbitrageFinderTriangleSingle
        elif arb_mode in {'multi_triangle', 'triangle_multi'}:
            return ArbitrageFinderTriangleMulti

    def _run(
            self, flashloan_tokens: List[str], CCm: CPCContainer, *, result=None, arb_mode: str = None, randomizer=True
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

        Returns
        -------
        Optional[Tuple[str, List[Any]]]
            The result.

        """

        random_mode = self.AO_CANDIDATES if randomizer else None
        arb_mode = self.AM_SINGLE if arb_mode is None else arb_mode
        arb_finder = self._get_arb_finder(arb_mode)
        finder = arb_finder(flashloan_tokens=flashloan_tokens, CCm=CCm, mode='bothin', result=random_mode, ConfigObj=self.ConfigObj)
        r = finder.find_arbitrage()

        if result == self.XS_ARBOPPS:
            return r

        if r is None or len(r) == 0:
            self.ConfigObj.logger.info("No eligible arb opportunities.")
            return None

        self.ConfigObj.logger.info(f"Found {len(r)} eligible arb opportunities.")
        r = random.choice(r) if randomizer else r

        return self._handle_trade_instructions(CCm, arb_mode, r, result)

    # TODO: This is still a mess. Refactor. [_handle_trade_instructions]
    def _handle_trade_instructions(self, CCm, arb_mode, r, result):
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
        agg_trade_instructions = tx_route_handler._aggregate_carbon_trades(
            trade_instructions_objects=ordered_trade_instructions_objects
        )
        del ordered_trade_instructions_objects  # TODO: REMOVE THIS
        if result == self.XS_AGGTI:
            return agg_trade_instructions
        calculated_trade_instructions = tx_route_handler.calculate_trade_outputs(agg_trade_instructions)
        if result == self.XS_EXACT:
            return calculated_trade_instructions
        fl_token = calculated_trade_instructions[0].tknin_key
        fl_token_with_weth = fl_token
        if (fl_token == 'WETH-6Cc2'):
            fl_token = "ETH-EEeE"
        # try:
        best_profit = calculated_trade_instructions[-1].amtout - calculated_trade_instructions[0].amtin
        flashloan_tkn_profit = best_profit
        if fl_token_with_weth != 'BNT-FF1C':
            bnt_flt_curves = CCm.bypair(pair=f"BNT-FF1C/{fl_token_with_weth}")
            bnt_flt = [x for x in bnt_flt_curves if x.params["exchange"] == "bancor_v3"][0]
            flt_per_bnt = Decimal(str(bnt_flt.x_act / bnt_flt.y_act))
            best_profit = Decimal(str(flt_per_bnt * best_profit))
        bnt_usdc_curve = CCm.bycid("0xc4771395e1389e2e3a12ec22efbb7aff5b1c04e5ce9c7596a82e9dc8fdec725b")
        usd_bnt = bnt_usdc_curve.y / bnt_usdc_curve.x
        profit_usd = best_profit * Decimal(str(usd_bnt))
        self.ConfigObj.logger.debug(
            f"updated best_profit after calculating exact trade numbers: {num_format(best_profit)}")
        flashloans = [{"token": fl_token, "amount": num_format_float(calculated_trade_instructions[0].amtin),
                       "profit": num_format_float(flashloan_tkn_profit)}]
        log_dict = {"type": arb_mode, "profit_bnt": num_format_float(best_profit),
                    "profit_usd": num_format_float(profit_usd), "flashloan": flashloans, "trades": []}
        for idx, trade in enumerate(calculated_trade_instructions):
            log_dict["trades"].append({"trade_index": idx, "exchange": trade.exchange_name, "tkn_in": trade.tknin,
                                       "amount_in": num_format_float(trade.amtin), "tkn_out": trade.tknout,
                                       "amt_out": num_format_float(trade.amtout), "cid0": trade.cid[-10:]})
        self.ConfigObj.logger.info(f"{log_format(log_data=log_dict, log_name='calculated_arb')}")
        if best_profit < self.ConfigObj.DEFAULT_MIN_PROFIT:
            self.ConfigObj.logger.info(
                f"Opportunity with profit: {num_format(best_profit)} does not meet minimum profit: {self.ConfigObj.DEFAULT_MIN_PROFIT}, discarding.")
            return (None, None)
        # Get the flashloan amount
        flashloan_amount = int(calculated_trade_instructions[0].amtin_wei)
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
                ConfigObj=self.ConfigObj,
                route_struct=route_struct,
                src_amount=flashloan_amount,
                src_address=flashloan_token_address,
            ), cids)
        # log the flashloan arbitrage tx info
        self.ConfigObj.logger.debug(f"Flashloan amount: {flashloan_amount}")
        self.ConfigObj.logger.debug(f"Flashloan token address: {flashloan_token_address}")
        self.ConfigObj.logger.debug(f"Route Struct: \n {route_struct}")
        self.ConfigObj.logger.debug(f"Trade Instructions: \n {best_trade_instructions_dic}")
        pool = (
            self.db.get_pool(exchange_name=self.ConfigObj.BANCOR_V3_NAME, pair_name='BNT-FF1C/ETH-EEeE')
        )
        bnt_eth = (int(pool.tkn0_balance), int(pool.tkn1_balance))
        # Init TxHelpers
        tx_helpers = TxHelpers(ConfigObj=self.ConfigObj)
        # Submit tx
        return (tx_helpers.validate_and_submit_transaction(route_struct=route_struct, src_amt=flashloan_amount,
                                                           src_address=flashloan_token_address, bnt_eth=bnt_eth,
                                                           expected_profit=best_profit, safety_override=False,
                                                           verbose=True, log_object=log_dict), cids)


    def _validate_and_submit_transaction_tenderly(self, ConfigObj, route_struct, src_address, src_amount):
        tx_submit_handler = TxSubmitHandler(
            ConfigObj=ConfigObj,
            route_struct=route_struct,
            src_address=src_address,
            src_amount=src_amount,
        )
        self.ConfigObj.logger.debug(f"route_struct: {route_struct}")
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

    def validate_mode(self, mode: str):
        """
        Validate the mode. If the mode is None, set it to RUN_CONTINUOUS.
        """
        if mode is None:
            mode = self.RUN_CONTINUOUS
        assert mode in [self.RUN_SINGLE, self.RUN_CONTINUOUS], f"Unknown mode {mode} [possible values: {self.RUN_SINGLE}, {self.RUN_CONTINUOUS}]"
        return mode

    def setup_polling_interval(self, polling_interval: int):
        """
        Setup the polling interval. If the polling interval is None, set it to RUN_POLLING_INTERVAL.
        """
        if self.polling_interval is None:
            self.polling_interval = polling_interval if polling_interval is not None else self.RUN_POLLING_INTERVAL

    def setup_flashloan_tokens(self, flashloan_tokens):
        """
        Setup the flashloan tokens. If flashloan_tokens is None, set it to RUN_FLASHLOAN_TOKENS.
        """
        return flashloan_tokens if flashloan_tokens is not None else self.RUN_FLASHLOAN_TOKENS

    def setup_CCm(self, CCm):
        """
        Setup the CCm. If CCm is None, retrieve and filter curves.
        """
        if CCm is None:
            CCm = self.get_curves()
            filter_out_weth = [x for x in CCm if (x.params.exchange == 'carbon_v1') & ((x.params.tkny_addr == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2') or (x.params.tknx_addr == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'))]
            CCm = CPCContainer([x for x in CCm if x not in filter_out_weth])
        return CCm

    def run_continuous_mode(self, flashloan_tokens, CCm, arb_mode):
        """
        Run the bot in continuous mode.
        """
        while True:
            try:
                CCm = self.get_curves()
                filter_out_weth = [x for x in CCm if (x.params.exchange == 'carbon_v1') & ((x.params.tkny_addr == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2') or (x.params.tknx_addr == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'))]
                CCm = CPCContainer([x for x in CCm if x not in filter_out_weth])
                tx_hash, cids = self._run(flashloan_tokens, CCm, arb_mode=arb_mode)
                if tx_hash and tx_hash[0]:
                    self.ConfigObj.logger.info(f"Arbitrage executed [hash={tx_hash}]")

                time.sleep(self.polling_interval)
            except self.NoArbAvailable as e:
                self.ConfigObj.logger.debug(f"[bot:run:single] {e}")
            except Exception as e:
                self.ConfigObj.logger.error(f"[bot:run:continuous] {e}")
                time.sleep(self.polling_interval)

    def run_single_mode(self, flashloan_tokens, CCm, arb_mode):
        """
        Run the bot in single mode.
        """
        try:
            tx_hash = self._run(flashloan_tokens=flashloan_tokens, CCm=CCm, arb_mode=arb_mode)
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
            self.run_continuous_mode(flashloan_tokens, CCm, arb_mode)
        else:
            self.run_single_mode(flashloan_tokens, CCm, arb_mode)

