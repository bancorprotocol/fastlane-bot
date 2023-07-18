# coding=utf-8
"""
Base class for triangular arbitrage finder modes

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import abc
import itertools
from typing import List, Any, Tuple, Union

import pandas as pd

from fastlane_bot.modes.base import ArbitrageFinderBase
from fastlane_bot.tools.cpc import T


class ArbitrageFinderTriangleBase(ArbitrageFinderBase):
    """
    Base class for triangular arbitrage finder modes
    """

    @abc.abstractmethod
    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """
        pass

    @staticmethod
    def get_miniverse(
        y_match_curves_not_carbon: List[Any],
        base_exchange_curves: List[Any],
        x_match_curves_not_carbon: List[Any],
        flt: str,
        arb_mode: str,
        combos: List[Any],
    ) -> List[Any]:
        """
        Get miniverse for triangular arbitrage

        Parameters
        ----------
        y_match_curves_not_carbon : list
            List of curves that match the y token and are not on carbon
        base_exchange_curves : list
            List of curves on the base exchange
        x_match_curves_not_carbon : list
            List of curves that match the x token and are not on carbon
        flt : str
            Flashloan token
        arb_mode : str
            Arbitrage mode
        combos : list
            List of combos

        Returns
        -------
        combos : list
            List of combos

        """
        if arb_mode in ["single_triangle", "triangle"]:
            miniverses = list(
                itertools.product(
                    y_match_curves_not_carbon,
                    base_exchange_curves,
                    x_match_curves_not_carbon,
                )
            )
        else:
            external_curve_combos = list(
                itertools.product(y_match_curves_not_carbon, x_match_curves_not_carbon)
            )
            miniverses = [
                base_exchange_curves + list(combo) for combo in external_curve_combos
            ]
        if miniverses:
            combos += list(zip([flt] * len(miniverses), miniverses))
        return combos

    def get_combos(
        self, flashloan_tokens: List[str], CCm: Any, arb_mode: str
    ) -> Tuple[List[str], List[Any]]:
        """
        Get combos for triangular arbitrage

        Parameters
        ----------
        flashloan_tokens : list
            List of flashloan tokens
        CCm : object
            CCm object
        arb_mode : str
            Arbitrage mode

        Returns
        -------
        combos : list
            List of combos

        """
        combos = []
        if arb_mode in ["single_triangle_bancor3", "bancor_v3", "b3_two_hop"]:
            combos = [
                (tkn0, tkn1)
                for tkn0, tkn1 in itertools.product(flashloan_tokens, flashloan_tokens)
                # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
                if tkn0 != tkn1
            ]
        else:
            all_base_exchange_curves = CCm.byparams(exchange=self.base_exchange).curves
            for flt in flashloan_tokens:  # may wish to run this for one flt at a time
                non_flt_base_exchange_curves = [
                    x for x in all_base_exchange_curves if flt not in x.pair
                ]
                for non_flt_base_exchange_curve in non_flt_base_exchange_curves:
                    target_tkny = non_flt_base_exchange_curve.tkny
                    target_tknx = non_flt_base_exchange_curve.tknx
                    base_exchange_curves = (
                        CCm.bypairs(f"{target_tknx}/{target_tkny}")
                        .byparams(exchange=self.base_exchange)
                        .curves
                    )
                    y_match_curves = CCm.bypairs(
                        set(CCm.filter_pairs(onein=target_tknx))
                        & set(CCm.filter_pairs(onein=flt))
                    )
                    x_match_curves = CCm.bypairs(
                        set(CCm.filter_pairs(onein=target_tkny))
                        & set(CCm.filter_pairs(onein=flt))
                    )
                    y_match_curves_not_carbon = [
                        x
                        for x in y_match_curves
                        if x.params.exchange != self.base_exchange
                    ]
                    x_match_curves_not_carbon = [
                        x
                        for x in x_match_curves
                        if x.params.exchange != self.base_exchange
                    ]
                    combos = self.get_miniverse(
                        y_match_curves_not_carbon,
                        base_exchange_curves,
                        x_match_curves_not_carbon,
                        flt,
                        arb_mode,
                        combos,
                    )
        return combos

    @staticmethod
    def get_mono_direction_carbon_curves(
        miniverse: List[Any], trade_instructions_df: pd.DataFrame, token_in: str=None
    ) -> List[Any]:
        """
        Get mono direction carbon curves for triangular arbitrage

        Parameters
        ----------
        miniverse : list
            List of miniverses
        token_in : str
            Token in
        trade_instructions_df : DataFrame
            Trade instructions dataframe

        Returns
        -------
        mono_direction_carbon_curves : list
            List of mono direction carbon curves

        """

        if token_in is None:
            columns = trade_instructions_df.columns
            check_nan = trade_instructions_df.copy().fillna(0)
            first_bancor_v3_pool = check_nan.iloc[0]
            second_bancor_v3_pool = check_nan.iloc[1]

            for idx, token in enumerate(columns):
                if token == T.BNT:
                    continue
                if first_bancor_v3_pool[token] < 0:
                    token_in = token
                    break
                if second_bancor_v3_pool[token] < 0:
                    token_in = token
                    break

        wrong_direction_cids = []
        for idx, row in trade_instructions_df.iterrows():
            if (row[token_in] < 0) and ("-0" in idx or "-1" in idx):
                wrong_direction_cids.append(idx)

        return [curve for curve in miniverse if curve.cid not in wrong_direction_cids]
