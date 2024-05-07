"""
Defines the base class for all arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import abc
from typing import Any, Tuple, Dict, List, Union
from _decimal import Decimal
import pandas as pd


class ArbitrageFinderBase:
    """
    Base class for all arbitrage finder modes
    """

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

    def get_prices_simple(self, CCm, tkn0, tkn1):
        curve_prices = [(x.params['exchange'],x.descr,x.cid,x.p) for x in CCm.bytknx(tkn0).bytkny(tkn1)]
        curve_prices += [(x.params['exchange'],x.descr,x.cid,1/x.p) for x in CCm.bytknx(tkn1).bytkny(tkn0)]
        return curve_prices
    
    # Global constant for 'carbon_v1' order
    CARBON_SORTING_ORDER = float('inf')

    # Create a sort order mapping function
    def create_sort_order(self, sort_sequence):
        # Create a dictionary mapping from sort sequence to indices, except for 'carbon_v1'
        return {key: index for index, key in enumerate(sort_sequence) if key != 'carbon_v1'}

    # Define the sort key function separately
    def sort_key(self, item, sort_order):
        # Check if the item is 'carbon_v1'
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
            self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS,
            self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS,
        ]:
            if src_token == self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS:
                fl_token_with_weth = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
            else:
                fl_token_with_weth = src_token

            sort_sequence = ['bancor_v2','bancor_v3','uniswap_v2','uniswap_v3']
            price_curves = self.get_prices_simple(CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, fl_token_with_weth)
            sorted_price_curves = self.custom_sort(price_curves, sort_sequence)
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit sort_sequence] {sort_sequence}")
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit price_curves] {price_curves}")
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit sorted_price_curves] {sorted_price_curves}")
            if len(sorted_price_curves)>0:
                fltkn_eth_conversion_rate = sorted_price_curves[0][-1]
                best_profit_eth = Decimal(str(best_profit_fl_token)) / Decimal(str(fltkn_eth_conversion_rate))
                self.ConfigObj.logger.debug(f"[modes.base.calculate_profit] {src_token, best_profit_fl_token, fltkn_eth_conversion_rate, best_profit_eth}")
            else:
                self.ConfigObj.logger.error(
                    f"[modes.base.calculate_profit] Failed to get conversion rate for {fl_token_with_weth} and {self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS}. Raise"
                )
                raise
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
