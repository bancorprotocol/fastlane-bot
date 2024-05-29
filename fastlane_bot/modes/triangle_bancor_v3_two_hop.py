"""
Defines the b3-two-hop-triangle arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List
from itertools import product

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase

class ArbitrageFinderTriangleBancor3TwoHop(ArbitrageFinderTriangleBase):
    def get_combos(self) -> List[Any]:
        miniverse_combos = []

        CC = self.CCm.byparams(exchange="bancor_v3")

        if self.ConfigObj.LIMIT_BANCOR3_FLASHLOAN_TOKENS:
            flashloan_tokens = list(set(CC.tknys()) & set(self.flashloan_tokens))
        else:
            flashloan_tokens = CC.tknys()

        bancor_curves_dict = {tkn: CC.bypairs(f"{self.ConfigObj.BNT_ADDRESS}/{tkn}").curves for tkn in flashloan_tokens}

        for tkn0, tkn1 in [(tkn0, tkn1) for tkn0, tkn1 in product(flashloan_tokens, flashloan_tokens) if tkn0 != tkn1]:
            if len(bancor_curves_dict[tkn0]) == 0 or len(bancor_curves_dict[tkn1]) == 0:
                continue

            all_curves = list(set(self.CCm.bypairs(f"{tkn0}/{tkn1}")) | set(self.CCm.bypairs(f"{tkn1}/{tkn0}")))
            carbon_curves = [curve for curve in all_curves if curve.params.exchange in self.ConfigObj.CARBON_V1_FORKS]
            other_curves = [curve for curve in all_curves if curve.params.exchange not in self.ConfigObj.CARBON_V1_FORKS]
            bancor_curves = bancor_curves_dict[tkn0] + bancor_curves_dict[tkn1]

            base_dir_one = [curve for curve in carbon_curves if curve.pair == carbon_curves[0].pair]
            base_dir_two = [curve for curve in carbon_curves if curve.pair != carbon_curves[0].pair]

            miniverses = []

            if len(other_curves) > 0:
                miniverses += [bancor_curves + [curve] for curve in other_curves]

            if len(base_dir_one) > 0:
                miniverses += [bancor_curves + base_dir_one]

            if len(base_dir_two) > 0:
                miniverses += [bancor_curves + base_dir_two]

            miniverse_combos += [(tkn1, miniverse) for miniverse in miniverses]

        return miniverse_combos
