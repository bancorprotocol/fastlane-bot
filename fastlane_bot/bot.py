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

import itertools
import time
from dataclasses import dataclass, InitVar, asdict
from typing import Any, Union, Optional
from typing import List, Dict, Tuple
from _decimal import Decimal

#from fastlane_bot import config as cfg
from fastlane_bot.db.manager import DatabaseManager
from fastlane_bot.db.models import Pool, Token
from fastlane_bot.helpers import (
    TxSubmitHandler, TxSubmitHandlerBase,
    TxReceiptHandler, TxReceiptHandlerBase,
    TxRouteHandler, TxRouteHandlerBase,
    TxHelpers, TxHelpersBase,
    TradeInstruction
)
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
from fastlane_bot.tools.optimizer import CPCArbOptimizer
import fastlane_bot.db.models as models
from fastlane_bot.config import Config
from . import __VERSION__, __DATE__
from .helpers.txhelpers import TxHelper

# errorlogger = c.logger.error
# errorlogger = c.logger.debug # TODO: REMOVE THIS

@dataclass
class CarbonBotBase():
    """
    Base class for the business logic of the bot.
    
    Attributes
    ----------
    db: DatabaseManager
        the database manager.
    TxSubmitHandlerClass: class derived from TxSubmitHandlerBase
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
    
    db: DatabaseManager = None
    TxSubmitHandlerClass: any = None
    TxReceiptHandlerClass: any = None
    TxRouteHandlerClass: any = None
    TxHelpersClass: any = None
    ConfigObj: Config = None
    
    genesis_data: InitVar = None # DEPRECATED; WILL BE REMOVED SOON
    drop_tables: InitVar = False # STAYS
    seed_pools: InitVar = False # anything else WILL raise
    update_pools: InitVar = False # anything else WILL raise
    
    usd_gas_limit: int = 150
    min_profit: int = 60
    polling_interval: int = None
    
    def __post_init__(self, genesis_data=None, drop_tables=None, seed_pools=None, update_pools=None):
        """
        The post init method.
        """
        if genesis_data is not None:
            print(
                "WARNING: genesis_data is deprecated. This argument will be removed soon"
            )
            
        assert self.polling_interval is None, "polling_interval is now a parameter to run"

        if self.TxSubmitHandlerClass is None:
            self.TxSubmitHandlerClass = TxSubmitHandler
        assert issubclass(self.TxSubmitHandlerClass, TxSubmitHandlerBase), f"TxSubmitHandlerClass not derived from TxSubmitHandlerBase {self.TxSubmitHandlerClass}"

        if self.TxReceiptHandlerClass is None:
            self.TxReceiptHandlerClass = TxReceiptHandler
        assert issubclass(self.TxReceiptHandlerClass, TxReceiptHandlerBase), f"TxReceiptHandlerClass not derived from TxReceiptHandlerBase {self.TxReceiptHandlerClass}"

        if self.TxRouteHandlerClass is None:
            self.TxRouteHandlerClass = TxRouteHandler
        assert issubclass(self.TxRouteHandlerClass, TxRouteHandlerBase), f"TxRouteHandlerClass not derived from TxRouteHandlerBase {self.TxRouteHandlerClass}"

        if self.TxHelpersClass is None:
            self.TxHelpersClass = TxHelpers
        assert issubclass(self.TxHelpersClass, TxHelpersBase), f"TxHelpersClass not derived from TxHelpersBase {self.TxHelpersClass}"

        if self.db is None:
            self.db = DatabaseManager(
                data=self.genesis_data
            )
            
        if self.ConfigObj is None:
            self.ConfigObj = Config()
    
    @property
    def C(self, key: str) -> Any:
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
        
    def update_pools(self, drop_tables: bool = False):
        """convenience method for db.update_pools()"""
        self.db.update_pools(drop_tables=drop_tables)

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
        pools_and_tokens = self.db.get_nonzero_liquidity_pools_and_tokens()
        curves = []
        for p in pools_and_tokens:
            try:
                curves += p.to_cpc()
                #time.sleep(0.00000001)  # to avoid unstable results
            except ZeroDivisionError as e:
                errorlogger(f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n")
                #raise
            except CPC.CPCValidationError as e:
                errorlogger(f"[get_curves] MUST FIX INVALID CURVE {p} [{e}]\n")
                #raise   
            except TypeError as e:
                errorlogger(f"[get_curves] MUST FIX DECIMAL ERROR CURVE {p} [{e}]\n")
                if not str(e).startswith("1unsupported operand type(s) for"):
                    raise    
            except p.DoubleInvalidCurveError as e:
                errorlogger(f"[get_curves] MUST FIX DOUBLE INVALID CURVE {p} [{e}]\n")
                #raise   
            except Exception as e:
                errorlogger(f"[get_curves] error converting pool to curve {p} [{e}]\n")
                raise
        return CPCContainer(curves)


@dataclass
class CarbonBot(CarbonBotBase):
    """
    A class that handles the business logic of the bot.

    MAIN ENTRY POINTS
    :run:               Runs the bot.
    """

    def __post_init__(self, genesis_data=None, drop_tables=None, seed_pools=None, update_pools=None):
        super().__post_init__(genesis_data=genesis_data, drop_tables=drop_tables, seed_pools=seed_pools, update_pools=update_pools)

    def _order_and_scale_trade_instruction_dcts(self,
                                                trade_instruction_df,
                                                trade_instruction_dcts,
                                                best_src_token
                                                ):
        # print("[_order_and_scale_trade_instruction_dcts] r", r)
        # note the dictionary values are changed in place
        # trade_instruction_df, trade_instruction_dcts, best_src_token = r
        df = trade_instruction_df.iloc[:-3]
        assert len(df.columns) == 2, "Can only route pairs"
        dfp = df[df[best_src_token] > 0]
        dfm = df[df[best_src_token] < 0]
        order = list(dfp.index.values) + list(dfm.index.values)
        # order here
        trade_dicts = {d['cid']: d for d in trade_instruction_dcts}
        ordered_trade_instructions = [trade_dicts[cid] for cid in order]
        # scale here
        data = ordered_trade_instructions
        for i in range(len(data)):
            if data[i]["tknin"] == best_src_token:
                #     data[i]["amtin"] *= 0.999
                # else:
                data[i]["amtin"] *= 0.99
        return data, len(dfp)  # ordered_scaled_dcts, tx_in_count

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
        result = ({**ti, "raw_txs": "[]", "pair_sorting": ""} for ti in trade_instructions_dic if ti is not None)
        result = [TradeInstruction(**ti) for ti in result]
        return result

    def _check_if_carbon(self, cid: str) -> tuple[bool, str, str]:
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
    ) -> Tuple[
        Union[Union[int, Decimal, Decimal], Any], Optional[Any], Optional[Any], str
    ]:
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
        c.logger.debug("[_find_arbitrage_opportunities] Number of curves:", len(CCm))
        best_profit = 0
        best_src_token = None
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
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
            try:
                c.logger.debug(f"Checking flashloan token = {tkn1}, other token = {tkn0}")
                CC = CCm.bypairs(f"{tkn0}/{tkn1}")
                if len(CC) < 2:
                    continue
                pstart = (
                    {
                        tkn0: CCm.bypairs(f"{tkn0}/{tkn1}")[0].p,
                    }
                    if len(CC) != 0
                    else None
                )
                O = CPCArbOptimizer(CC)
                src_token = tkn1
                try:
                    r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
                    assert not r.is_error
                except Exception as e:
                    c.logger.debug(e, r)
                    try:
                        r = O.margp_optimizer(src_token)
                        assert not r.is_error
                    except Exception as e:
                        c.logger.info(e)
                        continue

                profit_src = -r.result
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions = r.trade_instructions()

                cids = [ti['cid'] for ti in trade_instructions_dic]
                profit = self.db._get_bnt_price_from_tokens(profit_src, src_token)

                candidates += [(profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]
                contains_carbon = sum(
                    int(self._check_if_carbon(ti['cid'])[0])
                    for ti in trade_instructions_dic
                )
                contains_other = sum(
                    int(self._check_if_not_carbon(ti['cid']))
                    for ti in trade_instructions_dic
                )
                try:
                    netchange = trade_instructions_df[trade_instructions_df.index == 'TOTAL NET'].values[0]
                except Exception as e:
                    netchange = [0]

                ops = (
                    best_profit,
                    best_trade_instructions_df,
                    best_trade_instructions_dic,
                    best_src_token,
                    best_trade_instructions
                )

                if len(trade_instructions_df) > 0 and profit < 1500:
                    ordered_scaled_dcts, tx_in_count = self._order_and_scale_trade_instruction_dcts(
                        trade_instructions_df, trade_instructions_dic, src_token)

                    condition_1 = (profit > best_profit)
                    condition_3 = tx_in_count > 0
                    condition_4 = False
                    bnt_gas_limit = self.db._get_bnt_price_from_tokens(self.usd_gas_limit, 'USDC')
                    if profit > (self.min_profit + bnt_gas_limit):
                        condition_4 = True

                    condition_5 = 2 <= contains_carbon + contains_other <= 3
                    contains_other_ct = contains_other
                    contains_carbon_ct = contains_carbon
                    contains_other = contains_other > 0
                    contains_carbon = contains_carbon > 0
                    condition_2 = True

                    # print all conditions (profit > best_profit) and (contains_carbon > 0) and (tx_in_count > 0) and (profit > (self.min_profit + bnt_gas_limit)) and (2 <= contains_carbon + contains_other <= 3)
                    c.logger.info('\n')
                    c.logger.info("[_find_arbitrage_opportunities] *************")
                    c.logger.info(f"profit = {round(profit, 4)}, tkn0 = {tkn0}, tkn1 = {tkn1}, cids = {cids}")
                    c.logger.info(f"(self.min_profit + bnt_gas_limit) = {(self.min_profit + bnt_gas_limit)} {bnt_gas_limit}")
                    c.logger.info(f"(profit > best_profit): {(profit > best_profit)}")
                    c.logger.info(f"(contains_carbon > 0): {contains_carbon_ct} {contains_carbon}")
                    c.logger.info(f"(contains_other > 0): {contains_other_ct} {contains_other}")
                    c.logger.info(f"(tx_in_count > 0): {(tx_in_count > 0)}")
                    c.logger.info(f"(profit > (self.min_profit + bnt_gas_limit)): {(profit > (self.min_profit + bnt_gas_limit))}")
                    c.logger.info(f"(2 <= contains_carbon + contains_other <= 3): {condition_5}")
                    c.logger.info('\n')

                    if (profit > best_profit) and (contains_carbon > 0) and (tx_in_count > 0) and (profit > (self.min_profit + bnt_gas_limit)) and (2 <= contains_carbon + contains_other <= 3) and (max(netchange) < 1e-4):
                        best_profit = profit
                        best_src_token = src_token
                        best_trade_instructions_df = trade_instructions_df
                        best_trade_instructions_dic = trade_instructions_dic
                        best_trade_instructions = trade_instructions

                        c.logger.info('\n')
                        c.logger.info("[_find_arbitrage_opportunities] *************")
                        c.logger.info(f"New best profit: {profit}")
                        c.logger.info(f"Profit in bnt: {profit} {cids}")
                        c.logger.info(f"bnt_gas_limit: {bnt_gas_limit}")
                        c.logger.info(f"tx_in_count > 0: {condition_3}")
                        c.logger.info(f"2 <= contains_carbon + contains_other <= 3: {condition_5}")
                        c.logger.info(f"contains_carbon: {contains_carbon}")
                        c.logger.info(f"contains_other: {contains_other}")
                        c.logger.info(f"profit > best_profit: {condition_1}")
                        c.logger.info(f"best_trade_instructions_df: {best_trade_instructions_df}")
                        c.logger.info("*************")
                        c.logger.info('\n')
            
            except Exception as e:
                raise
            
            cids = [ti['cid'] for ti in trade_instructions_dic]
            if src_token == "WETH-6Cc2":
                query_token = "ETH-EEeE"
            else:
                query_token = src_token
            profit_usd = self.db._get_usd_price_from_key(profit_src, query_token, tkn0)
            profit = profit_usd*2
            #print(f"Profit in usd: {profit_usd} {cids}")
            #print(f"Profit in bnt: {profit} {cids}")
            contains_carbon = any(
                self._check_if_carbon(ti['cid'])[0]
                for ti in trade_instructions_dic
            )
            #print('contains_carbon', profit, contains_carbon, [self._check_if_carbon(ti['cid'])[0] for ti in trade_instructions_dic])
            candidates += [self.ArbCandidate(r, contains_carbon, profit_usd)]
            try:
                netchange = trade_instructions_df.iloc[-1]
            except Exception as e:
                c.logger.error(f"[_find_arbitrage_opportunities] {e}")

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
            c.w3.eth.getBlock(c.w3.eth.block_number).timestamp + c.DEFAULT_BLOCKTIME_DEVIATION
        )

    XS_ARBOPPS = "arbopps"
    XS_TI = "ti"
    XS_ORDSCAL = "ordscal"
    XS_AGGTI = "aggti"
    XS_ORDTI = "ordti"
    XS_ENCTI = "encti"
    XS_ROUTE = "route"
    # TODO: RENAME TO _RUN
    def _run(
        self, flashloan_tokens: List[str], CCm: CPCContainer, *, result=None, network: str = "mainnet"
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

        Returns
        -------
        str
            The transaction hash.
        """
        assert network == "mainnet", "Only mainnet"
        # TODO: REMOVE THIS PARAMETER; THE NETWORK MUST BE SET IN THE BOT ITSELF
        
        ## Find arbitrage opportunities
        r = self._find_arbitrage_opportunities(flashloan_tokens, CCm)
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
        ordered_scaled_dcts, tx_in_count = self._order_and_scale_trade_instruction_dcts(r)
        if result == self.XS_ORDSCAL:
            return ordered_scaled_dcts
        
        ## Convert opportunities to trade instructions
        ordered_trade_instructions_objects = self._convert_trade_instructions(ordered_scaled_dcts)
        if result == self.XS_TI:
            return ordered_trade_instructions_objects
        
        ## Aggregate trade instructions
        tx_route_handler = self.TxRouteHandlerClass(ordered_trade_instructions_objects)
        agg_trade_instructions = tx_route_handler._aggregate_carbon_trades(
            trade_instructions=ordered_trade_instructions_objects
        )
        del ordered_trade_instructions_objects # TODO: REMOVE THIS
        if result == self.XS_AGGTI:
            return agg_trade_instructions

        # Get the flashloan amount
        flashloan_amount = int(agg_trade_instructions[0].amtin_wei) * self.flashloan_multiplier

        # Get the flashloan token address
        flashloan_token_address = c.w3.toChecksumAddress(
            self.db.get_token_address_from_token_key(agg_trade_instructions[0].tknin_key)
        )

        c.logger.debug(f"flashloan_amount: {flashloan_amount}")
        if result == self.XS_ORDTI:
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
            return route_struct
        
        ## Submit transaction and obtain transaction receipt
        assert result is None, f"Unknown result requested {result}"
        if network != "mainnet":
            return self._validate_and_submit_transaction_tenderly(
                encoded_trade_instructions, flashloan_token_address, route_struct, flashloan_amount
            )

        # log the flashloan arbitrage tx info
        c.logger.info(f"Flashloan amount: {flashloan_amount}")
        c.logger.info(f"Flashloan token address: {flashloan_token_address}")
        c.logger.info(f"Route Struct: \n {route_struct}")
        c.logger.info(f"Trade Instructions: \n {best_trade_instructions_dic}")
        c.logger.info(f"Trade Instructions Objects: \n {ordered_trade_instructions_objects}")
        c.logger.info(f"Aggregated Trade Instructions: \n {agg_trade_instructions}")

        # Initialize tx helper
        tx_helper = TxHelper(
            usd_gas_limit=self.usd_gas_limit,
            w3=c.w3,
            gas_price_multiplier=self.gas_price_multiplier,
            arb_contract=c.BANCOR_ARBITRAGE_CONTRACT
        )

        # Get the cids of the trade instructions
        cids = list({ti['cid'].split('-')[0] for ti in best_trade_instructions_dic})

        # Submit the transaction
        return tx_helper.submit_flashloan_arb_tx(
            arb_data=route_struct,
            flashloan_token_address=flashloan_token_address,
            flashloan_amount=flashloan_amount,
            verbose=True,
        ), cids



    def _validate_and_submit_transaction_tenderly(self, trade_instructions, src_address, route_struct, src_amount):
        tx_submit_handler = self.TxSubmitHandlerClass(
            trade_instructions,
            src_address=src_address,
            src_amount=trade_instructions[0].amtin_wei,
        )
        c.logger.debug(f"route_struct: {route_struct}")
        tx_details = tx_submit_handler._get_tx_details()
        tx_submit_handler.token_contract.functions.approve(
            c.w3.toChecksumAddress(c.FASTLANE_CONTRACT_ADDRESS), 0
        ).transact(tx_details)
        tx_submit_handler.token_contract.functions.approve(
            c.w3.toChecksumAddress(c.FASTLANE_CONTRACT_ADDRESS), src_amount
        ).transact(tx_details)
        c.logger.debug("src_address", src_address)
        tx = tx_submit_handler._submit_transaction_tenderly(
            route_struct, src_address, src_amount
        )
        return  c.w3.eth.wait_for_transaction_receipt(tx)

    # def _handle_ordering(
    #     self, agg_trade_instructions, best_src_token, tx_route_handler
    # ):
    #     """
    #     Handles the ordering of the aggregated trade instructions.

    #     Parameters
    #     ----------
    #     agg_trade_instructions:
    #         aggregate trade instructions as returned by _agg_carbon_independentIDs
        
    #     best_src_token: 
    #         the best source (=flashloan) token as returned by _find_arbitrage_opportunities
            
    #     tx_route_handler: TxRouteHandlerBase
    #         the transaction route handler object

    #     Returns
    #     -------
    #         ordered trade instructions
    #     """
    #     new_trade_instructions = []
    #     if len(agg_trade_instructions) == 2:
    #         for inst in agg_trade_instructions:
    #             if inst.tknin == best_src_token:
    #                 new_trade_instructions += [inst]
    #         missing = [
    #             inst
    #             for inst in agg_trade_instructions
    #             if inst not in new_trade_instructions
    #         ]
    #         new_trade_instructions.append(missing[0])
    #     else:
    #         new_trade_instructions = tx_route_handler._find_tradematches(
    #             agg_trade_instructions
    #         )
    #     return new_trade_instructions

    RUN_FLASHLOAN_TOKENS = [T.WETH, T.DAI, T.USDC, T.USDT, T.WBTC, T.BNT]
    RUN_SINGLE = "single"
    RUN_CONTINUOUS = "continuous"
    RUN_POLLING_INTERVAL = 60 # default polling interval in seconds
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
        assert mode in [self.RUN_SINGLE, self.RUN_CONTINUOUS], f"Unknown mode {mode} [possible values: {self.RUN_SINGLE}, {self.RUN_CONTINUOUS}]"
        if polling_interval is None:
            polling_interval = self.RUN_POLLING_INTERVAL
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
                        c.logger.info(f"Arbitrage executed [hash={tx_hash}]")
                        self.db.update_recently_traded_pools(cids)

                    time.sleep(self.polling_interval)
                except Exception as e:
                    c.logger.error(f"[bot:run:continuous] {e}")
                    time.sleep(self.polling_interval)
        else:
            try:
                tx_hash = self._run(flashloan_tokens, CCm)
                c.logger.info(f"Arbitrage executed [hash={tx_hash}]")
            except Exception as e:
                c.logger.error(f"[bot:run:single] {e}")

                
