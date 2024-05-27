"""
Defines the multi-triangle arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List
from itertools import product

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase

class ArbitrageFinderTriangleMulti(ArbitrageFinderTriangleBase):
    def get_combos(self) -> List[Any]:
        combos = []
        all_carbon_curves = self.CCm.byparams(exchange="carbon_v1").curves

        for flt in self.flashloan_tokens:
            non_flt_carbon_curves = [curve for curve in all_carbon_curves if flt not in curve.pair]
            for non_flt_carbon_curve in non_flt_carbon_curves:
                tkny = non_flt_carbon_curve.tkny
                tknx = non_flt_carbon_curve.tknx

                carbon_curves = self.CCm.bypairs(f"{tknx}/{tkny}").byparams(exchange="carbon_v1").curves
                if len(carbon_curves) == 0:
                    continue

                y_match_curves = self.CCm.bypairs(set(self.CCm.filter_pairs(onein=tknx)) & set(self.CCm.filter_pairs(onein=flt))).curves
                x_match_curves = self.CCm.bypairs(set(self.CCm.filter_pairs(onein=tkny)) & set(self.CCm.filter_pairs(onein=flt))).curves

                y_match_other_curves = [curve for curve in y_match_curves if curve.params.exchange != "carbon_v1"]
                if len(y_match_other_curves) == 0:
                    continue

                x_match_other_curves = [curve for curve in x_match_curves if curve.params.exchange != "carbon_v1"]
                if len(x_match_other_curves) == 0:
                    continue

                base_dir_one = [curve for curve in carbon_curves if curve.pair == carbon_curves[0].pair]
                base_dir_two = [curve for curve in carbon_curves if curve.pair != carbon_curves[0].pair]

                if len(base_dir_one) > 0:
                    combos += get_miniverse_combos(y_match_other_curves, x_match_other_curves, base_dir_one, flt)

                if len(base_dir_two) > 0:
                    combos += get_miniverse_combos(y_match_other_curves, x_match_other_curves, base_dir_two, flt)

        return combos

def get_miniverse_combos(
    y_match_other_curves: List[Any],
    x_match_other_curves: List[Any],
    base_exchange_curves: List[Any],
    flt: str
):
    """
    Get miniverse for triangular arbitrage

    Parameters
    ----------
    y_match_other_curves : list
        List of curves that match the y token and are not on carbon
    x_match_other_curves : list
        List of curves that match the x token and are not on carbon
    base_exchange_curves : list
        List of curves on carbon
    flt : str
        Flashloan token

    Returns
    -------
    A list of miniverse combos
    """
    curve_combos = list(product(y_match_other_curves, x_match_other_curves))
    miniverses = [base_exchange_curves + list(combo) for combo in curve_combos]
    return [(flt, miniverse) for miniverse in miniverses]
