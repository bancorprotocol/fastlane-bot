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
from typing import Any, Union, Optional, Tuple, List, Dict

#import math
import pandas as pd
from _decimal import Decimal
#from pandas import DataFrame, Series

from fastlane_bot import config as cfg
from fastlane_bot.helpers import (
    TxSubmitHandler, TxSubmitHandlerBase,
    TxReceiptHandler, TxReceiptHandlerBase,
    TxRouteHandler, TxRouteHandlerBase,
    TxHelpers, TxHelpersBase,
    TradeInstruction
)
from fastlane_bot.db import DatabaseManager
from fastlane_bot.models import Pool, session, Token
from fastlane_bot.tools import tokenscale as ts
from fastlane_bot.tools.arbgraphs import ArbGraph, plt  # convenience imports
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
from fastlane_bot.tools.optimizer import CPCArbOptimizer

from dataclasses import dataclass, asdict, InitVar, field
from typing import List, Dict, Tuple

from . import __VERSION__, __DATE__

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
    
    genesis_data: InitVar = None # DEPRECATED; WILL BE REMOVED SOON
    drop_tables: InitVar = False # STAYS
    seed_pools: InitVar = False # anything else WILL raise
    update_pools: InitVar = False # anything else WILL raise
    
    polling_interval: int = 60
    
    def __post_init__(self, genesis_data=None, drop_tables=None, seed_pools=None, update_pools=None):
        """
        The post init method.
        """
        if not genesis_data is None:
            print(f"WARNING: genesis_data is deprecated. This argument will be removed soon")
            
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
                data=self.genesis_data, drop_tables=drop_tables
            )
                    
    def versions(self):
        """
        Returns the versions of the module and its Carbon dependencies.
        """
        s = [f"fastlane_bot v{__VERSION__} ({__DATE__})"]
        s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(CPC)]
        #s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(ArbGraph)]
        #s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(ts.TokenScale)]
        s += ["carbon v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer)]
        return s
        
    def seed_pools(self, drop_tables: bool = False):
        """convenience method for db.seed_pools()"""
        self.db.seed_pools(drop_tables=drop_tables)
        
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
        pools = (
            # TODO: CLEANUP THE SESSION / EVENTMANAGER / DATABASEMANAGER ISSUE
            session.query(Pool)
            .filter(
                (Pool.tkn0_balance > 0)
                | (Pool.tkn1_balance > 0)
                | (Pool.liquidity > 0)
                | (Pool.y_0 > 0)
            )
            .all()
        )
        curves = []
        for p in pools:
            try:
                curves += p.to_cpc("float")
                time.sleep(0.00000001)  # to avoid unstable results
            except:
                pass
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

    def _order_and_scale_trade_instruction_dcts(self, r):
        print("[_order_and_scale_trade_instruction_dcts] r", r)
        # note the dictionary values are changed in place
        _, trade_instruction_df, trade_instruction_dcts, best_src_token = r
        df = trade_instruction_df.iloc[:-3]
        assert len(df.columns)==2, "Can only route pairs"
        dfp = df[df[best_src_token]>0]
        dfm = df[df[best_src_token]<0]
        order = list(dfp.index.values) + list(dfm.index.values)
        # order here
        trade_dicts = {d['cid'] :d for d in trade_instruction_dcts}
        ordered_trade_instructions = [trade_dicts[cid] for cid in order]
        #scale here
        data = trade_instruction_dcts
        for i in range(len(data)):
            if data[i]["tknin"] == 'WETH-6Cc2':
                data[i]["amtin"] *= 0.9999
            else:
                data[i]["amtin"] *= 0.99
        return data, len(dfp) #ordered_scaled_dcts, tx_in_count

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
        cfg.logger.debug("[_find_arbitrage_opportunities] Number of curves:", len(CCm))
        best_profit = 0
        best_src_token = None
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
        # pools = (
        #     # TODO: CLEANUP THE SESSION / EVENTMANAGER / DATABASEMANAGER ISSUE
        #     session.query(Pool)
        #     .filter(
        #         (Pool.tkn0_balance > 0)
        #         | (Pool.tkn1_balance > 0)
        #         | (Pool.liquidity > 0)
        #         | (Pool.y_0 > 0)
        #     )
        #     .all()
        # )
        # cfg.logger.debug(f"Number of pools: {len(pools)}")
        # all_tokens = [p.pair_name.split("/")[0] for p in pools] + [
        #     p.pair_name.split("/")[1] for p in pools
        # ]
        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect)
            if tkn0 != tkn1
        ]
        if result == self.AO_TOKENS:
            return all_tokens, combos
        
        candidates = []
        for tkn0, tkn1 in combos:
            try:
                cfg.logger.debug(f"Checking {tkn0} -> {tkn1}")
                CC = CCm.bypairs(f"{tkn0}/{tkn1}")
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
                    r = O.margp_optimizer(tkn1, params=dict(pstart=pstart))
                    assert not r.is_error
                except Exception as e:
                    cfg.logger.debug(e, r)
                    try:
                        r = O.margp_optimizer(tkn1)
                    except Exception as e:
                        cfg.logger.error(e)
                        
                profit_src = -r.result

                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)

                profit = self._get_profit_in_bnt(profit_src, src_token)
                    # TODO: THIS MAY OR MAY NOT GET A PROFIT NUMBER
                    # WE NEED TO DEAL WITH THIS IF IT DOES NOT
                cfg.logger.debug(f"Profit in {src_token}: {profit_src}")
                cfg.logger.debug(f"Profit in BNT: {profit}")
                candidates += [(profit, trade_instructions_df, trade_instructions_dic, src_token)]
                if profit > best_profit:
                    best_profit = profit
                    best_src_token = src_token
                    best_trade_instructions_df = trade_instructions_df
                    best_trade_instructions_dic = trade_instructions_dic
            except Exception as e:
                cfg.logger.error(e)
        
        if result == self.AO_CANDIDATES:
            return candidates
        return (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
        )

    def _get_profit_in_bnt(self, profit_src, src_token):
        """
        Gets the profit in BNT.

        Parameters
        ----------
        profit_src: Decimal
            The profit in the source token.
        src_token: str
            The source token.
        """
        # print("BNT HARDCODEDD TODO FIX")
        # return profit_src
    
        if src_token == "BNT-FF1C":
            return profit_src
        # TODO: THIS SHOULD NOT BE IN THE BOT BUT IN THE MODEL
        pool = (
            # TODO: CLEANUP THE SESSION / EVENTMANAGER / DATABASEMANAGER ISSUE
            session.query(Pool)
            .filter(Pool.exchange_name == cfg.BANCOR_V3_NAME, Pool.tkn1_key == src_token)
            .first()
        )
        bnt = Decimal(pool.tkn0_balance) / 10**18
        src = Decimal(src_token) / 10**pool.tkn1_decimals
        bnt_per_src = bnt / src
        return profit_src * bnt_per_src

    def _get_deadline(self) -> int:
        """
        Gets the deadline for a transaction.

        Returns
        -------
        int
            The deadline (as UNIX epoch).
        """
        return (
            cfg.w3.eth.getBlock(cfg.w3.eth.block_number).timestamp + cfg.DEFAULT_BLOCKTIME_DEVIATION
        )

    XS_ARBOPPS = "arbopps"
    XS_TI = "ti"
    XS_ORDSCAL = "ordscal"
    XS_AGGTI = "aggti"
    XS_ORDTI = "ordti"
    XS_ENCTI = "encti"
    XS_ROUTE = "route"
    def _execute_strategy(
        self, flashloan_tokens: List[str], CCm: CPCContainer, *, result=None, network: str = "mainnet"
    ) -> Optional[Dict[str, Any]]:
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
            trade_instructions_dic,
            best_src_token,
        ) = r

        # Order the trades instructions suitable for routing and scale the amounts
        ordered_scaled_dcts, tx_in_count = self._order_and_scale_trade_instruction_dcts(r)
        if result == self.XS_ORDSCAL:
            return ordered_scaled_dcts
        
        ## Convert opportunities to trade instructions
        trade_instructions = self._convert_trade_instructions(ordered_scaled_dcts)
        if result == self.XS_TI:
            return trade_instructions
        
        ## Aggregate trade instructions
        tx_route_handler = self.TxRouteHandlerClass(trade_instructions)
        agg_trade_instructions = tx_route_handler._agg_carbon_independentIDs(
            trade_instructions=trade_instructions
        )
        del trade_instructions # TODO: REMOVE THIS
        if result == self.XS_AGGTI:
            return agg_trade_instructions

        # ## Order trade instructions
        # ordered_trade_instructions = self._handle_ordering(
        #     agg_trade_instructions, best_src_token, tx_route_handler
        # )
        src_amount = sum(agg_trade_instructions[i].amtin_wei for i in range(tx_in_count))
        cfg.logger.debug(f"src_amount: {src_amount}")
        src_address = (
            # TODO: CLEANUP THE SESSION / EVENTMANAGER / DATABASEMANAGER ISSUE
            session.query(Token).filter(Token.key == best_src_token).first().address
        )
        src_address = cfg.w3.toChecksumAddress(src_address)
        if result == self.XS_ORDTI:
            return agg_trade_instructions, src_amount, src_address
        
        ## Encode trade instructions
        encoded_trade_instructions = tx_route_handler.custom_data_encoder(agg_trade_instructions)
        if result == self.XS_ENCTI:
            return encoded_trade_instructions
        
        ## Determine route
        deadline = self._get_deadline()
        route_struct = tx_route_handler.get_arb_contract_args(
            encoded_trade_instructions, deadline
        )
        if result == self.XS_ROUTE:
            return route_struct
        
        ## Submit transaction and obtain transaction receipt
        assert result is None, f"Unknown result requested {result}"
        if network != "mainnet":
            return self._validate_and_submit_transaction_tenderly(
                encoded_trade_instructions, src_address, route_struct, src_amount
            )
        tx_helper = self.TxHelpersClass()
        return tx_helper.validate_and_submit_transaction(
            encoded_trade_instructions, src_address, route_struct, src_amount
        )

    def _validate_and_submit_transaction_tenderly(self, trade_instructions, src_address, route_struct, src_amount):
        tx_submit_handler = self.TxSubmitHandlerClass(
            trade_instructions,
            src_address=src_address,
            src_amount=trade_instructions[0].amtin_wei,
        )
        cfg.logger.debug(f"route_struct: {route_struct}")
        tx_details = tx_submit_handler._get_tx_details()
        tx_submit_handler.token_contract.functions.approve(
            cfg.w3.toChecksumAddress(cfg.FASTLANE_CONTRACT_ADDRESS), 0
        ).transact(tx_details)
        tx_submit_handler.token_contract.functions.approve(
            cfg.w3.toChecksumAddress(cfg.FASTLANE_CONTRACT_ADDRESS), src_amount
        ).transact(tx_details)
        cfg.logger.debug("src_address", src_address)
        tx = tx_submit_handler._submit_transaction_tenderly(
            route_struct, src_address, src_amount
        )
        return cfg.w3.eth.wait_for_transaction_receipt(tx)

    def _handle_ordering(
        self, agg_trade_instructions, best_src_token, tx_route_handler
    ):
        """
        Handles the ordering of the aggregated trade instructions.

        Parameters
        ----------
        agg_trade_instructions:
            aggregate trade instructions as returned by _agg_carbon_independentIDs
        
        best_src_token: 
            the best source (=flashloan) token as returned by _find_arbitrage_opportunities
            
        tx_route_handler: TxRouteHandlerBase
            the transaction route handler object

        Returns
        -------
            ordered trade instructions
        """
        new_trade_instructions = []
        if len(agg_trade_instructions) == 2:
            for inst in agg_trade_instructions:
                if inst.tknin == best_src_token:
                    new_trade_instructions += [inst]
            missing = [
                inst
                for inst in agg_trade_instructions
                if inst not in new_trade_instructions
            ]
            new_trade_instructions.append(missing[0])
        else:
            new_trade_instructions = tx_route_handler._find_tradematches(
                agg_trade_instructions
            )
        return new_trade_instructions

    RUN_FLASHLOAN_TOKENS = [T.WETH, T.DAI, T.USDC, T.USDT, T.WBTC, T.BNT]
    RM_SINGLE = "single"
    RM_CONTINUOUS = "continuous"
    def run(
        self,
        flashloan_tokens: List[str],
        CCm: CPCContainer = None,
        #update_pools: bool = False,
        *,
        mode: str = None,
    ) -> str:
        """
        Runs the bot.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: CPCContainer
            The CPCContainer object.

        Returns
        -------
        str
            The transaction hash.
        """
        if mode is None:
            mode = self.RM_CONTINUOUS
        assert mode in [self.RM_SINGLE, self.RM_CONTINUOUS], f"Unknown mode {mode}"
        if not flashloan_tokens:
            flashloan_tokens = self.RUN_FLASHLOAN_TOKENS
        if CCm is None:
            CCm = self.get_curves()
        if mode == "continuous":
            while True:
                try:
                    tx_hash = self._execute_strategy(flashloan_tokens, CCm)
                    if tx_hash:
                        cfg.logger.info(
                            f"Flashloan arbitrage executed with transaction hash: {tx_hash}"
                        )
                    time.sleep(
                        self.polling_interval
                    )  # Sleep for 60 seconds before searching for opportunities again
                except Exception as e:
                    cfg.logger.debug(e)
                    time.sleep(self.polling_interval)
        else:
            try:
                tx_hash = self._execute_strategy(flashloan_tokens, CCm)
            except Exception as e:
                cfg.logger.warning(e)
                tx_hash = None
            if tx_hash:
                cfg.logger.info(
                    f"Flashloan arbitrage executed with transaction hash: {tx_hash}"
                )
