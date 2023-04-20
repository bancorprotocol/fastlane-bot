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
from . import __VERSION__, __DATE__
import time
from typing import Any, Union, Optional, Tuple, List, Dict

import pandas as pd
from _decimal import Decimal
from pandas import DataFrame, Series

from fastlane_bot.config import *
from fastlane_bot.helpers import (
    TxSubmitHandler, TxSubmitHandlerBase,
    TradeInstruction, TxReceiptHandlerBase,
    TxRouteHandler, TxRouteHandlerBase,
    TxReceiptHandler, TransactionHelpers,
)
from fastlane_bot.db import DatabaseManager
from fastlane_bot.models import Pool, session, Token
#from carbon.tools import tokenscale as ts
#from carbon.tools.arbgraphs import ArbGraph
from carbon.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
from carbon.tools.optimizer import CPCArbOptimizer

from dataclasses import dataclass, asdict, InitVar, field
from typing import List, Dict, Tuple


@dataclass
class CarbonBot:
    """
    A class that handles the business logic of the bot.

    Attributes
    ----------
    TxSubmitHandlerClass: class derived from TxSubmitHandlerBase
        the class to be instantiated for the transaction submit handler (default: TxSubmitHandler).
    TxReceiptHandlerClass: class derived from TxReceiptHandlerBase
        ditto (default: TxReceiptHandler).
    TxRouteHandlerClass: class derived from TxRouteHandlerBase
        ditto (default: TxRouteHandler).


    
    MAIN ENTRY POINTS
    :run:               Runs the bot.
    :seed_pools:        Seeds the pools.
    :update_pools:      Updates the pools.
    :get_curves:        Gets the curves.
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    db: DatabaseManager = None
    genesis_data = pd.read_csv(DATABASE_SEED_FILE) # TODO this and drop tables
    drop_tables: InitVar = False
    polling_interval: int = 60

    TxSubmitHandlerClass: any = None
    TxReceiptHandlerClass: any = None
    TxRouteHandlerClass: any = None

    def __post_init__(self, drop_tables: bool = False):
        """
        The post init method.
        """
        if self.TxSubmitHandlerClass is None:
            self.TxSubmitHandlerClass = TxSubmitHandler
        assert issubclass(self.TxSubmitHandlerClass, TxSubmitHandlerBase), f"TxSubmitHandlerClass not derived from TxSubmitHandlerBase {self.TxSubmitHandlerClass}"
        
        if self.TxReceiptHandlerClass is None:
            self.TxReceiptHandlerClass = TxReceiptHandler
        assert issubclass(self.TxReceiptHandlerClass, TxReceiptHandlerBase), f"TxReceiptHandlerClass not derived from TxReceiptHandlerBase {self.TxReceiptHandlerClass}"
        
        if self.TxRouteHandlerClass is None:
            self.TxRouteHandlerClass = TxRouteHandler
        assert issubclass(self.TxRouteHandlerClass, TxRouteHandlerBase), f"TxRouteHandlerClass not derived from TxRouteHandlerBase {self.TxRouteHandlerClass}"
        
        if self.db is None:
            self.db = DatabaseManager(
                data=self.genesis_data, drop_tables=self.drop_tables
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

    def get_curves(self) -> CPCContainer:
        """
        Gets the curves from the database.

        Returns
        -------
        CPCContainer
            The container of curves.
        """
        pools = (
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
        trade_instructions = []
        if trade_instructions_dic is not None:
            for trade_instruction in trade_instructions_dic:
                if trade_instruction is not None:
                    if "raw_txs" not in trade_instruction.keys():
                        trade_instruction["raw_txs"] = "[]"
                    if "pair_sorting" not in trade_instruction.keys():
                        trade_instruction["pair_sorting"] = ""
                    trade_instructions += [
                        TradeInstruction(
                            cid=trade_instruction["cid"],
                            tknin=trade_instruction["tknin"],
                            amtin=trade_instruction["amtin"],
                            tknout=trade_instruction["tknout"],
                            amtout=trade_instruction["amtout"],
                            raw_txs=trade_instruction["raw_txs"],
                            pair_sorting=trade_instruction["pair_sorting"],
                        )
                    ]
        return trade_instructions

    def _find_arbitrage_opportunities(
        self, flashloan_tokens: List[str], CCm: CPCContainer, mode: str = "bothin"
    ) -> Tuple[Union[Union[int, Decimal, Decimal], Any], Optional[Any], Optional[Any], str]:
        """
        Finds the arbitrage opportunities.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: CPCContainer
            The CPCContainer object.
        mode: str
            The mode.

        Returns
        -------
        Tuple[Decimal, List[Dict[str, Any]]]
            The best profit and the trade instructions.
        """
        logger.debug("[_find_arbitrage_opportunities] Number of curves:", len(CCm))
        best_profit = 0
        best_src_token = None
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
        for idx, tkn in enumerate(flashloan_tokens):
            tkn0 = flashloan_tokens[idx - 1]
            tkn1 = flashloan_tokens[idx]
            assert tkn == tkn1

            CC = CCm.bypairs(CCm.filter_pairs(bothin=f"{tkn0},{tkn1}"))
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
            except Exception as e:
                logger.debug(e)
                r = O.margp_optimizer(tkn1)  # TODO: catch again
            profit_src = -r.result
            trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
            trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)

            profit = self._get_profit_in_bnt(profit_src, src_token)

            if profit > best_profit:
                best_src_token = src_token
                best_profit = profit
                best_trade_instructions_df = trade_instructions_df
                best_trade_instructions_dic = trade_instructions_dic
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
        if src_token == "BNT-FF1C":
            return profit_src
        pool = (
            session.query(Pool)
            .filter(Pool.exchange_name == BANCOR_V3_NAME, Pool.tkn1_key == src_token)
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
            The deadline.
        """
        return (
                w3.eth.getBlock(w3.eth.block_number).timestamp
                + DEFAULT_BLOCKTIME_DEVIATION
        )

    def _execute_strategy(self, flashloan_tokens: List[str], CCm: CPCContainer, network: str = 'mainnet') -> Optional[
        Dict[str, Any]]:
        """
        Refactored execute strategy.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: float
            The CCm.

        Returns
        -------
        str
            The transaction hash.
        """
        (
            best_profit,
            best_trade_instructions_df,
            trade_instructions_dic,
            best_src_token,
        ) = self._find_arbitrage_opportunities(flashloan_tokens, CCm)

        trade_instructions = self._convert_trade_instructions(trade_instructions_dic)
        tx_route_handler = TxRouteHandler(trade_instructions)
        agg_trade_instructions = tx_route_handler._agg_carbon_independentIDs(
            trade_instructions=trade_instructions
        )

        trade_instructions = self._handle_ordering(agg_trade_instructions, best_src_token, tx_route_handler)
        src_amount = trade_instructions[0].amtin_wei
        logger.debug(f"src_amount: {src_amount}")
        src_address = (
            session.query(Token).filter(Token.key == best_src_token).first().address
        )
        src_address = w3.toChecksumAddress(src_address)
        trade_instructions = tx_route_handler.custom_data_encoder(trade_instructions)

        deadline = self._get_deadline()

        route_struct = tx_route_handler.get_arb_contract_args(
            trade_instructions, deadline
        )

        if network != 'mainnet':
            return self._validate_and_submit_transaction_tenderly(
                trade_instructions, src_address, route_struct, src_amount
            )
        tx_submit_handler = TransactionHelpers()
        return tx_submit_handler.validate_and_submit_transaction(
            route_struct, src_address, src_amount
        )

    def _validate_and_submit_transaction_tenderly(self, trade_instructions, src_address, route_struct, src_amount):
        tx_submit_handler = TxSubmitHandler(
            trade_instructions,
            src_amount=trade_instructions[0].amtin_wei,
            src_address=src_address,
        )
        logger.debug(f"route_struct: {route_struct}")
        tx_details = tx_submit_handler._get_tx_details()
        tx_submit_handler.token_contract.functions.approve(
            w3.toChecksumAddress(FASTLANE_CONTRACT_ADDRESS), 0
        ).transact(tx_details)
        tx_submit_handler.token_contract.functions.approve(
            w3.toChecksumAddress(FASTLANE_CONTRACT_ADDRESS), src_amount
        ).transact(tx_details)
        logger.debug("src_address", src_address)
        tx = tx_submit_handler._submit_transaction_tenderly(
            route_struct, src_address, src_amount
        )
        return w3.eth.wait_for_transaction_receipt(tx)

    def _handle_ordering(self, agg_trade_instructions, best_src_token, tx_route_handler):
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

    MODE_SINGLE = "single"
    MODE_CONTINUOUS = "continuous"
    MODE_CONT = MODE_CONTINUOUS
    def run(
        self,
        flashloan_tokens: List[str],
        CCm: CPCContainer = None,
        update_pools: bool = False,
        mode: str = None,
    ) -> str:
        """
        Runs the bot once.

        Parameters
        ----------
        flashloan_tokens: List[str]
            The flashloan tokens.
        CCm: CPCContainer
            The container object containing all curves to be arbitraged.
        mode: MODE_SINGLE or MODE_CONTINUOUS
            Whether to run the bot once or continuously (default: cont).

        Returns
        -------
        str
            The transaction hash.
        """
        if isinstance(flashloan_tokens, str):
            flashloan_tokens = [t.strip() for t in flashloan_tokens.split(",")]
        if not flashloan_tokens:
            flashloan_tokens = [T.WETH, T.DAI, T.USDC, T.USDT, T.WBTC, T.BNT]
        if mode is None:
            mode = self.MODE_CONTINUOUS
        if CCm is None:
            CCm = self.get_curves()
        if mode == self.MODE_CONTINUOUS:
            while True:
                try:
                    tx_hash = self._execute_strategy(flashloan_tokens, CCm)
                    if tx_hash:
                        logger.info(
                            f"Flashloan arbitrage executed with transaction hash: {tx_hash}"
                        )
                        if update_pools:
                            self.db.update_pools()
                    time.sleep(
                        self.polling_interval
                    )  # Sleep for 60 seconds before searching for opportunities again
                except Exception as e:
                    logger.debug(e)
                    time.sleep(
                        self.polling_interval
                    )
        elif mode == self.MODE_SINGLE:
            try:
                tx_hash = self._execute_strategy(flashloan_tokens, CCm)
            except Exception as e:
                logger.warning(e)
                tx_hash = None
            if tx_hash:
                logger.info(
                    f"Flashloan arbitrage executed with transaction hash: {tx_hash}"
                )
        else:
            raise ValueError(f"Unknown mode: {mode}")
