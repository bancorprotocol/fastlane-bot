"""
Defines the multi-pairwise-all arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List
from itertools import product

from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase

class ArbitrageFinderMultiPairwiseAll(ArbitrageFinderPairwiseBase):
    def get_combos(self) -> List[Any]:
        all_tokens = self.CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(self.flashloan_tokens))
        return [(tkn0, tkn1) for tkn0, tkn1 in product(all_tokens, flashloan_tokens_intersect) if tkn0 != tkn1]

    def get_curve_combos(self, curves: List[Any]) -> List[Any]:
        carbon_curves = [curve for curve in curves if curve.params.exchange in self.ConfigObj.CARBON_V1_FORKS]
        other_curves = [curve for curve in curves if curve.params.exchange not in self.ConfigObj.CARBON_V1_FORKS]

        if len(carbon_curves) > 0:
            curve_combos = []

            base_dir_one = [curve for curve in carbon_curves if curve.pair == carbon_curves[0].pair]
            base_dir_two = [curve for curve in carbon_curves if curve.pair != carbon_curves[0].pair]

            if len(base_dir_one) > 0:
                curve_combos += [[curve] + base_dir_one for curve in other_curves]

            if len(base_dir_two) > 0:
                curve_combos += [[curve] + base_dir_two for curve in other_curves]

            if len(carbon_curves) > 1:
                curve_combos += [carbon_curves]

            return curve_combos

        return [[curve0, curve1] for curve0 in other_curves for curve1 in other_curves if curve0 != curve1]
