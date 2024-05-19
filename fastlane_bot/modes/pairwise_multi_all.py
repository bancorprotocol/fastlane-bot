"""
Defines the Multi-pairwise arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Any, Tuple
from itertools import product

from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase

class ArbitrageFinderMultiPairwiseAll(ArbitrageFinderPairwiseBase):
    arb_mode = "multi_pairwise_all"

    def get_combos(self, flashloan_tokens: List[str], CCm: Any) -> Tuple[List[str], List[Any]]:
        """
        Get combos for pairwise arbitrage

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
        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in product(all_tokens, flashloan_tokens_intersect)
            # tkn1 is always the token being flash loaned
            # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
            if tkn0 != tkn1
        ]
        return all_tokens, combos

    def get_curve_combos(self, CC: Any) -> List[Any]:
        carbon_curves = [x for x in CC.curves if x.params.exchange in self.ConfigObj.CARBON_V1_FORKS]
        not_carbon_curves = [x for x in CC.curves if x.params.exchange not in self.ConfigObj.CARBON_V1_FORKS]
        curve_combos = [[_curve0] + [_curve1] for _curve0 in not_carbon_curves for _curve1 in not_carbon_curves if (_curve0 != _curve1)]

        if len(carbon_curves) > 0:
            base_direction_pair = carbon_curves[0].pair
            base_direction_one = [curve for curve in carbon_curves if curve.pair == base_direction_pair]
            base_direction_two = [curve for curve in carbon_curves if curve.pair != base_direction_pair]
            curve_combos = []

            if len(base_direction_one) > 0:
                curve_combos += [[curve] + base_direction_one for curve in not_carbon_curves]

            if len(base_direction_two) > 0:
                curve_combos += [[curve] + base_direction_two for curve in not_carbon_curves]

            if len(carbon_curves) >= 2:
                curve_combos += [carbon_curves]

        return curve_combos
