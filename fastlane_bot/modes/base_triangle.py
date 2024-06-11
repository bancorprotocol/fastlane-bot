"""
Defines the base class for triangular arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
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
        if arb_mode in ["b3_two_hop"]:
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
                    if len(base_exchange_curves) == 0:
                        continue

                    base_direction_pair = base_exchange_curves[0].pair
                    base_direction_one = [curve for curve in base_exchange_curves if curve.pair == base_direction_pair]
                    base_direction_two = [curve for curve in base_exchange_curves if curve.pair != base_direction_pair]
                    assert len(base_exchange_curves) == len(base_direction_one) + len(base_direction_two)
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
                    if len(y_match_curves_not_carbon) == 0:
                        continue
                    x_match_curves_not_carbon = [
                        x
                        for x in x_match_curves
                        if x.params.exchange != self.base_exchange
                    ]
                    if len(x_match_curves_not_carbon) == 0:
                        continue
                    if len(base_direction_one) > 0:
                        combos = self.get_miniverse(
                            y_match_curves_not_carbon,
                            base_direction_one,
                            x_match_curves_not_carbon,
                            flt,
                            arb_mode,
                            combos,
                        )
                    if len(base_direction_two) > 0:
                        combos = self.get_miniverse(
                            y_match_curves_not_carbon,
                            base_direction_two,
                            x_match_curves_not_carbon,
                            flt,
                            arb_mode,
                            combos,
                        )
        return combos

    def build_pstart(self, CCm, tkn0list, tkn1):
        tkn0list = [x for x in tkn0list if x not in [tkn1]]
        pstart = {}
        for tkn0 in tkn0list:
            try:
                pstart[tkn0] = CCm.bytknx(tkn0).bytkny(tkn1)[0].p
            except:
                try:
                    pstart[tkn0] = 1/CCm.bytknx(tkn1).bytkny(tkn0)[0].p
                except Exception as e:
                    self.ConfigObj.logger.info(f"[pstart build] {tkn0}/{tkn1} price error {e}")
        pstart[tkn1] = 1
        return pstart
