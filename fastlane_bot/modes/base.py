# coding=utf-8
"""
Base class for all arbitrage finder modes

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import abc
from typing import Any, Tuple, Dict, List, Union

import pandas as pd

from fastlane_bot.tools.cpc import T
from fastlane_bot.utils import num_format


class ArbitrageFinderBase:
    """
    Base class for all arbitrage finder modes
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
    AO_TOKENS = "tokens"
    AO_CANDIDATES = "candidates"

    def __init__(
        self,
        flashloan_tokens,
        CCm,
        mode="bothin",
        result=AO_CANDIDATES,
        ConfigObj: Any = None,
        arb_mode: str = None,
    ):
        self.flashloan_tokens = flashloan_tokens
        self.CCm = CCm
        self.mode = mode
        self.result = result
        self.best_profit = 0
        self.best_src_token = None
        self.best_trade_instructions = None
        self.best_trade_instructions_df = None
        self.best_trade_instructions_dic = None
        self.ConfigObj = ConfigObj
        self.base_exchange = "bancor_v3" if arb_mode == "bancor_v3" else "carbon_v1"

    @abc.abstractmethod
    def find_arbitrage(
        self,
        candidates: List[Any] = None,
        ops: Tuple = None,
        best_profit: float = 0,
        profit_src: float = 0,
    ) -> Union[List, Tuple]:
        """
        See subclasses for details

        Parameters
        ----------
        candidates : List[Any], optional
            List of candidates, by default None
        ops : Tuple, optional
            Tuple of operations, by default None
        best_profit : float, optional
            Best profit so far, by default 0
        profit_src : float, optional
            Profit source, by default 0

        Returns
        -------
        Union[List, Tuple]
            If self.result == self.AO_CANDIDATES, it returns a list of candidates.
        """
        pass

    def _set_best_ops(
        self,
        best_profit: float,
        ops: Tuple,
        profit: float,
        src_token: str,
        trade_instructions: Any,
        trade_instructions_df: pd.DataFrame,
        trade_instructions_dic: Dict[str, Any],
    ) -> Tuple[float, Tuple]:
        """
        Set the best operations.

        Parameters:

        """
        self.ConfigObj.logger.debug("[modes.base._set_best_ops] *************")
        self.ConfigObj.logger.debug(
            f"[modes.base._set_best_ops] New best profit: {profit}"
        )

        # Update the best profit and source token
        best_profit = profit
        best_src_token = src_token

        # Update the best trade instructions
        best_trade_instructions_df = trade_instructions_df
        best_trade_instructions_dic = trade_instructions_dic
        best_trade_instructions = trade_instructions

        self.ConfigObj.logger.debug(
            f"[modes.base._set_best_ops] best_trade_instructions_df: {best_trade_instructions_df}"
        )

        # Update the optimal operations
        ops = (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        )

        self.ConfigObj.logger.debug("[modes.base.calculate_profit] *************")

        return best_profit, ops

    def calculate_profit(
        self,
        src_token: str,
        profit_src: float,
        CCm: Any,
        cids: List[str],
        profit: int = 0,
    ) -> float:
        """
        Calculate profit based on the source token.
        """

        best_profit_fl_token = profit_src
        if src_token not in [
            self.ConfigObj.NATIVE_GAS_TOKEN_KEY,
            self.ConfigObj.WRAPPED_GAS_TOKEN_KEY,
        ]:
            if src_token == self.ConfigObj.NATIVE_GAS_TOKEN_KEY:
                fl_token_with_weth = self.ConfigObj.WRAPPED_GAS_TOKEN_KEY
            else:
                fl_token_with_weth = src_token

            try:
                fltkn_eth_conversion_rate = (
                    CCm.bytknb(f"{self.ConfigObj.WRAPPED_GAS_TOKEN_KEY}")
                    .bytknq(f"{fl_token_with_weth}")[0]
                    .p
                )
                best_profit_eth = best_profit_fl_token * fltkn_eth_conversion_rate
            except:
                try:
                    fltkn_eth_conversion_rate = (
                        1
                        / CCm.bytknb(f"{fl_token_with_weth}")
                        .bytknq(f"{self.ConfigObj.WRAPPED_GAS_TOKEN_KEY}")[0]
                        .p
                    )
                    best_profit_eth = best_profit_fl_token * fltkn_eth_conversion_rate
                except Exception as e:
                    self.ConfigObj.logger.error(
                        f"[modes.base.calculate_profit] Failed to get conversion rate for {fl_token_with_weth} and {self.ConfigObj.WRAPPED_GAS_TOKEN_KEY}. Raise exception: {e}"
                    )
                    raise e
        else:
            best_profit_eth = best_profit_fl_token
        return best_profit_eth

    @staticmethod
    def get_netchange(trade_instructions_df: pd.DataFrame) -> List[float]:
        """
        Get the net change from the trade instructions.
        """
        try:
            return trade_instructions_df.iloc[-1]
        except Exception:
            return [500]  # an arbitrary large number

    def handle_candidates(
        self,
        best_profit: float,
        profit: float,
        trade_instructions_df: pd.DataFrame,
        trade_instructions_dic: Dict[str, Any],
        src_token: str,
        trade_instructions: Any,
    ) -> List[Tuple[float, pd.DataFrame, Dict[str, Any], str, Any]]:
        """
        Handle candidate addition based on conditions.

        Parameters:
        ----------
        best_profit : float
            Best profit
        profit : float
            Profit
        trade_instructions_df : pd.DataFrame
            Trade instructions dataframe
        trade_instructions_dic : dict
            Trade instructions dictionary
        src_token : str
            Source token
        trade_instructions : any
            Trade instructions

        Returns:
        -------
        candidates : list
            Candidates
        """
        netchange = self.get_netchange(trade_instructions_df)
        condition_zeros_one_token = max(netchange) < 1e-4

        if (
            condition_zeros_one_token
            and profit > self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN
        ):  # candidate regardless if profitable
            return [
                (
                    profit,
                    trade_instructions_df,
                    trade_instructions_dic,
                    src_token,
                    trade_instructions,
                )
            ]
        return []

    def find_best_operations(
        self,
        best_profit: float,
        ops: Tuple[float, pd.DataFrame, Dict[str, Any], str, Any],
        profit: float,
        trade_instructions_df: pd.DataFrame,
        trade_instructions_dic: Dict[str, Any],
        src_token: str,
        trade_instructions: Any,
    ) -> Tuple[float, Tuple[float, pd.DataFrame, Dict[str, Any], str, Any]]:
        """
        Find the best operations based on conditions.

        Parameters:
        ----------
        best_profit : float
            Best profit
        ops : tuple
            Operations
        profit : float
            Profit
        trade_instructions_df : pd.DataFrame
            Trade instructions dataframe
        trade_instructions_dic : dict
            Trade instructions dictionary
        src_token : str
            Source token
        trade_instructions : any
            Trade instructions

        Returns:
        -------
        best_profit : float
            Best profit
        ops : tuple
            Operations
        """
        netchange = self.get_netchange(trade_instructions_df)
        condition_better_profit = profit > best_profit
        condition_zeros_one_token = max(netchange) < 1e-4
        if condition_better_profit and condition_zeros_one_token:
            return self._set_best_ops(
                best_profit,
                ops,
                profit,
                src_token,
                trade_instructions,
                trade_instructions_df,
                trade_instructions_dic,
            )
        return best_profit, ops

    def _check_limit_flashloan_tokens_for_bancor3(self):
        """
        Limit the flashloan tokens for bancor v3.
        """
        fltkns = self.CCm.byparams(exchange="bancor_v3").tknys()
        if self.ConfigObj.LIMIT_BANCOR3_FLASHLOAN_TOKENS:
            # Filter out tokens that are not in the existing flashloan_tokens list
            self.flashloan_tokens = [
                tkn for tkn in fltkns if tkn in self.flashloan_tokens
            ]
            self.ConfigObj.logger.info(
                f"[modes.base._check_limit_flashloan_tokens_for_bancor3] limiting flashloan_tokens to {self.flashloan_tokens}"
            )
        else:
            self.flashloan_tokens = fltkns
