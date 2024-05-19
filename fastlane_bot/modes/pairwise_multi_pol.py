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
    arb_mode = "multi_pairwise_pol"

    def get_combos(self) -> List[Any]:
        bancor_pol_tkns = self.CCm.byparams(exchange="bancor_pol").tokens()
        bancor_pol_tkns = set([tkn for tkn in bancor_pol_tkns if tkn != self.ConfigObj.WETH_ADDRESS])
        return [(tkn0, tkn1) for tkn0, tkn1 in product(bancor_pol_tkns, [self.ConfigObj.WETH_ADDRESS]) if tkn0 != tkn1]

    def get_curve_combos(self, CC: Any) -> List[Any]:
        pol_curves = [x for x in CC.curves if x.params.exchange == "bancor_pol"]
        carbon_curves = [x for x in CC.curves if x.params.exchange in self.ConfigObj.CARBON_V1_FORKS]
        not_carbon_curves = [x for x in CC.curves if x.params.exchange not in ["bancor_pol"] + self.ConfigObj.CARBON_V1_FORKS]
        curve_combos = [[curve] + pol_curves for curve in not_carbon_curves]

        if len(carbon_curves) > 0:
            base_direction_pair = carbon_curves[0].pair
            base_direction_one = [curve for curve in carbon_curves if curve.pair == base_direction_pair]
            base_direction_two = [curve for curve in carbon_curves if curve.pair != base_direction_pair]

            if len(base_direction_one) > 0:
                curve_combos += [[curve] + base_direction_one for curve in pol_curves]

            if len(base_direction_two) > 0:
                curve_combos += [[curve] + base_direction_two for curve in pol_curves]

        return curve_combos
