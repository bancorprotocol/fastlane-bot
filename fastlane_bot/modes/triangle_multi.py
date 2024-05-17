"""
Defines the multi-triangle arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Any, Tuple
from itertools import product

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase

class ArbitrageFinderTriangleMulti(ArbitrageFinderTriangleBase):
    arb_mode = "multi_triangle"

    def handle_exchange(self):
        assert self.base_exchange in self.ConfigObj.CARBON_V1_FORKS, "base_exchange for `multi_triangle` mode must be a carbon_v1 fork"

    def get_combos(self, flashloan_tokens: List[str], CCm: Any) -> Tuple[List[str], List[Any]]:
        """
        Get combos for triangular arbitrage

        Parameters
        ----------
        flashloan_tokens : list
            List of flashloan tokens
        CCm : object
            CCm object

        Returns
        -------
        combos : list
            List of combos

        """
        combos = []
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
                    get_miniverse(
                        y_match_curves_not_carbon,
                        base_direction_one,
                        x_match_curves_not_carbon,
                        flt,
                        combos,
                    )
                if len(base_direction_two) > 0:
                    get_miniverse(
                        y_match_curves_not_carbon,
                        base_direction_two,
                        x_match_curves_not_carbon,
                        flt,
                        combos,
                    )
        return combos

def get_miniverse(
    y_match_curves_not_carbon: List[Any],
    base_exchange_curves: List[Any],
    x_match_curves_not_carbon: List[Any],
    flt: str,
    combos: List[Any],
):
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
    combos : list
        List of combos

    """
    external_curve_combos = list(
        product(y_match_curves_not_carbon, x_match_curves_not_carbon)
    )
    miniverses = [
        base_exchange_curves + list(combo) for combo in external_curve_combos
    ]
    combos += list(zip([flt] * len(miniverses), miniverses))
