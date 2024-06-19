"""
Defines the multi-pairwise-pol arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List
from itertools import product

from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase

class ArbitrageFinderMultiPairwisePol(ArbitrageFinderPairwiseBase):
    def get_combos(self) -> List[Any]:
        bancor_pol_tkns = self.CCm.byparams(exchange="bancor_pol").tokens()
        bancor_pol_tkns = set([tkn for tkn in bancor_pol_tkns if tkn != self.ConfigObj.WETH_ADDRESS])
        return [(tkn0, tkn1) for tkn0, tkn1 in product(bancor_pol_tkns, [self.ConfigObj.WETH_ADDRESS]) if tkn0 != tkn1]

    def get_curve_combos(self, curves: List[Any]) -> List[Any]:
        pol_curves = [curve for curve in curves if curve.params.exchange == "bancor_pol"]
        carbon_curves = [curve for curve in curves if curve.params.exchange in self.ConfigObj.CARBON_V1_FORKS]
        other_curves = [curve for curve in curves if curve.params.exchange not in ["bancor_pol"] + self.ConfigObj.CARBON_V1_FORKS]
        curve_combos = [[curve] + pol_curves for curve in other_curves]

        if len(carbon_curves) > 0:
            base_dir_one = [curve for curve in carbon_curves if curve.pair == carbon_curves[0].pair]
            base_dir_two = [curve for curve in carbon_curves if curve.pair != carbon_curves[0].pair]

            if len(base_dir_one) > 0:
                curve_combos += [[curve] + base_dir_one for curve in pol_curves]

            if len(base_dir_two) > 0:
                curve_combos += [[curve] + base_dir_two for curve in pol_curves]

        return curve_combos
