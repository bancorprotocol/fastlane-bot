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
        all_curves = [self.CCm.byparams(exchange=exchange).curves for exchange in self.ConfigObj.CARBON_V1_FORKS]

        for flt in self.flashloan_tokens:
            for non_flt_curve in [curve for curve in all_curves if flt not in curve.pair]:
                tkny = non_flt_curve.tkny
                tknx = non_flt_curve.tknx

                pair_curves = self.CCm.bypairs(f"{tknx}/{tkny}")
                if len(pair_curves) == 0:
                    continue

                base_dir_one = [curve for curve in pair_curves[:1] if curve.params.exchange in self.ConfigObj.CARBON_V1_FORKS]
                base_dir_two = [curve for curve in pair_curves[1:] if curve.params.exchange in self.ConfigObj.CARBON_V1_FORKS]

                y_match_curves = self.CCm.bypairs(set(self.CCm.filter_pairs(onein=tknx)) & set(self.CCm.filter_pairs(onein=flt)))
                x_match_curves = self.CCm.bypairs(set(self.CCm.filter_pairs(onein=tkny)) & set(self.CCm.filter_pairs(onein=flt)))

                y_match_other_curves = [curve for curve in y_match_curves if curve.params.exchange not in self.ConfigObj.CARBON_V1_FORKS]
                if len(y_match_other_curves) == 0:
                    continue

                x_match_other_curves = [curve for curve in x_match_curves if curve.params.exchange not in self.ConfigObj.CARBON_V1_FORKS]
                if len(x_match_other_curves) == 0:
                    continue

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
        List of curves on the base exchange
    flt : str
        Flashloan token

    Returns
    -------
    A list of miniverse combos
    """
    curve_combos = list(product(y_match_other_curves, x_match_other_curves))
    miniverses = [base_exchange_curves + list(combo) for combo in curve_combos]
    return [(flt, miniverse) for miniverse in miniverses]
