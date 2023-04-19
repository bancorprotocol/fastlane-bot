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
import time
from typing import Any, Union, Optional

import pandas as pd
from _decimal import Decimal

from carbon.config import *
from carbon.helpers import (
    TxSubmitHandler,
    TradeInstruction,
    TxRouteHandler,
    TxReceiptHandler,
)
from carbon.manager import DatabaseManager
from carbon.models import Pool, session
from carbon.tools import tokenscale as ts
from carbon.tools.arbgraphs import ArbGraph, plt  # convenience imports
from carbon.tools.cpc import ConstantProductCurve as CPC, CPCContainer
from carbon.tools.optimizer import CPCArbOptimizer

plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ArbGraph))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ts.TokenScale))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))

from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class CarbonBot:
    """
    A class that handles the business logic of the bot.

    Attributes
    ----------
    tx_submitter_handler: TxSubmitHandler
        The transaction submitter handler.
    tx_receipt_handler: TxReceiptHandler
        The transaction receipt handler.
    mode: str
        The mode of the bot. (continuous or single)
    genesis_data: pd.DataFrame
        The genesis data. (token pairs)

    """

    mode: str = "single"
    db: DatabaseManager = None
    genesis_data = pd.read_csv("carbon/data/seed_token_pairs.csv")
    drop_tables: bool = False
    seed_pools: bool = False
    update_pools: bool = False
    polling_interval: int = 60

    tx_submitter_handler: TxSubmitHandler = None
    tx_receipt_handler: TxReceiptHandler = None
    tx_route_handler: TxRouteHandler = None

    def __post_init__(self):
        """
        The post init method.
        """
        self._check_mode()
        if self.db is None:
            self.db = DatabaseManager(
                data=self.genesis_data, drop_tables=self.drop_tables
            )
        if self.seed_pools:
            self.db.seed_pools()
        if self.update_pools:
            self.db.update_pools()

    @staticmethod
    def get_curves() -> CPCContainer:
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
            except:
                pass
        return CPCContainer(curves)

    def _check_mode(self):
        """
        Checks if the mode is valid.
        """
        if self.mode not in ["single", "continuous"]:
            raise Exception("Invalid mode.")

    def _convert_trade_instructions(
        self, trade_instructions_dic: List[Dict[str, Any]]
    ) -> list[TradeInstruction]:
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
            TradeInstruction(
                cid=trade_instruction["cid"],
                tknin=trade_instruction["tknin"],
                amtin=trade_instruction["amtin"],
                tknout=trade_instruction["tknout"],
                amtout=trade_instruction["amtout"],
            )
            for trade_instruction in trade_instructions_dic
        ]

    def _find_arbitrage_opportunities(
        self, flashloan_tokens: List[str], CCm: CPCContainer, mode: str = "bothin"
    ) -> tuple[Union[int, Any], Optional[Any], Optional[Any]]:
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
        best_profit = 0
        best_trade_instructions_df = None
        best_trade_instructions_dic = None
        for idx, tkn in enumerate(flashloan_tokens):
            tkn0 = flashloan_tokens[idx - 1]
            tkn1 = flashloan_tokens[idx]
            CC = CCm.bypairs(CCm.filter_pairs(bothin=f"{tkn0},{tkn1}"))
            O = CPCArbOptimizer(CC)
            r = O.margp_optimizer(tkn)
            trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
            trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
            if (
                r.result < best_profit
                and len(TxRouteHandler._get_carbon_indexes(trade_instructions_dic)) > 0
            ):
                best_profit = r.result
                best_trade_instructions_df = trade_instructions_df
                best_trade_instructions_dic = trade_instructions_dic
        return best_profit, best_trade_instructions_df, best_trade_instructions_dic

    def _execute_strategy(self, flashloan_tokens: List[str], CCm: CPCContainer) -> str:
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
        ) = self._find_arbitrage_opportunities(flashloan_tokens, CCm)
        trade_instructions = self._convert_trade_instructions(trade_instructions_dic)

        tx_route_handler = TxRouteHandler(trade_instructions)
        if not tx_route_handler.contains_carbon:
            logger.info("No arb opportunities found on Carbon.")
            return None

        new_route = tx_route_handler._determine_trade_route(trade_instructions)
        trade_instructions = tx_route_handler._reorder_trade_instructions(
            trade_instructions, new_route
        )
        trade_instructions = tx_route_handler._calculate_trade_outputs(
            trade_instructions
        )

        tx_submit_handler = TxSubmitHandler(trade_instructions)
        deadline = tx_submit_handler._get_deadline()

        route_struct, src_address, src_amount = tx_route_handler.get_route_structs(
            trade_instructions, deadline
        )
        tx_details = tx_submit_handler._get_tx_details()
        tx_submit_handler.token_contract.functions.approve(
            w3.toChecksumAddress(FASTLANE_CONTRACT_ADDRESS), src_amount
        ).transact(tx_details)

        tx = tx_submit_handler._submit_transaction_tenderly(
            route_struct, src_address, src_amount
        )
        w3.eth.wait_for_transaction_receipt(tx)
        return tx.hex()

    def run(
        self,
        flashloan_tokens: List[str],
        CCm: CPCContainer = None,
        update_pools: bool = False,
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
        if not flashloan_tokens:
            flashloan_tokens = ["USDC", "DAI", "USDT", "BNT", "WETH"]
        if CCm is None:
            CCm = self.get_curves()
        if update_pools:
            self.db.update_pools()
        if self.mode == "continuous":
            while True:
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
        else:
            tx_hash = self._execute_strategy(flashloan_tokens, CCm)
            if tx_hash:
                logger.info(
                    f"Flashloan arbitrage executed with transaction hash: {tx_hash}"
                )
