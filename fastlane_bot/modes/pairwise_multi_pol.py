"""
Defines the Multi-pairwise arbitrage finder class for Bancor POL

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Any, Tuple
from itertools import product

from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase

class FindArbitrageMultiPairwisePol(ArbitrageFinderPairwiseBase):
    arb_mode = "multi_pairwise_pol"

    def get_combos(self, flashloan_tokens: List[str], CCm: Any) -> Tuple[List[str], List[Any]]:
        """
        Get combos for pairwise arbitrage specific to Bancor POL

        Parameters
        ----------
        flashloan_tokens : list
            List of flashloan tokens
        CCm : object
            CCm object

        Returns
        -------
        all_tokens : list
            List of all tokens

        """

        bancor_pol_tkns = CCm.byparams(exchange="bancor_pol").tokens()
        bancor_pol_tkns = set([tkn for tkn in bancor_pol_tkns if tkn != self.ConfigObj.WETH_ADDRESS])

        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in product(bancor_pol_tkns, [self.ConfigObj.WETH_ADDRESS])
            # tkn1 is always the token being flash loaned
            # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
            if tkn0 != tkn1
        ]
        return bancor_pol_tkns, combos

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
