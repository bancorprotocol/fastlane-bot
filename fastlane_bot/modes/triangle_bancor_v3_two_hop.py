"""
Defines the b3-two-hop-triangle arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import math
from typing import Any, List
from itertools import product

from fastlane_bot.tools.cpc import CPCContainer, ConstantProductCurve
from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase

class ArbitrageFinderTriangleBancor3TwoHop(ArbitrageFinderTriangleBase):
    def get_combos(self) -> List[Any]:
        fltkns = self.CCm.byparams(exchange="bancor_v3").tknys()
        if self.ConfigObj.LIMIT_BANCOR3_FLASHLOAN_TOKENS:
            # Filter out tokens that are not in the existing flashloan_tokens list
            flashloan_tokens = [tkn for tkn in fltkns if tkn in self.flashloan_tokens]
            self.ConfigObj.logger.info(f"limiting flashloan_tokens to {self.flashloan_tokens}")
        else:
            flashloan_tokens = fltkns

        miniverse_combos = []
        combos = [(tkn0, tkn1) for tkn0, tkn1 in product(flashloan_tokens, flashloan_tokens) if tkn0 != tkn1]

        for tkn0, tkn1 in combos:
            all_curves = list(set(self.CCm.bypairs(f"{tkn0}/{tkn1}")) | set(self.CCm.bypairs(f"{tkn1}/{tkn0}")))

            carbon_curves = [curve for curve in all_curves if curve.params.get("exchange") in self.ConfigObj.CARBON_V1_FORKS]
            if not carbon_curves:
                continue

            external_curves = [curve for curve in all_curves if curve.params.get("exchange") not in self.ConfigObj.CARBON_V1_FORKS]
            if not external_curves:
                continue

            bancor_v3_curve_0 = self.CCm.bypairs(f"{self.ConfigObj.BNT_ADDRESS}/{tkn0}").byparams(exchange="bancor_v3").curves
            if not bancor_v3_curve_0:
                continue

            bancor_v3_curve_1 = self.CCm.bypairs(f"{self.ConfigObj.BNT_ADDRESS}/{tkn1}").byparams(exchange="bancor_v3").curves
            if not bancor_v3_curve_1:
                continue

            miniverses = [bancor_v3_curve_0 + bancor_v3_curve_1 + [curve] for curve in external_curves]

            base_direction_one = [curve for curve in carbon_curves if curve.pair == carbon_curves[0].pair]
            base_direction_two = [curve for curve in carbon_curves if curve.pair != carbon_curves[0].pair]

            if len(base_direction_one) > 0:
                miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + base_direction_one]

            if len(base_direction_two) > 0:
                miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + base_direction_two]

            miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + carbon_curves]

            miniverse_combos += [(tkn1, miniverse) for miniverse in miniverses]

        return miniverse_combos

    @staticmethod
    def get_tkn(pool: Any, tkn_num: int) -> str:
        """
        Gets the token ID from a pool object

        Parameters
        ----------
        pool: ConstantProductCurve
            The ConstantProductCurve object
        tkn_num: int
            The token number to get, either 0 or 1

        Returns
        -------
        str
        """
        return pool.pair.split("/")[tkn_num]

    @staticmethod
    def get_fee_safe(fee: int or float):
        """
        Fixes the format of the fee if the fee is in PPM format

        Parameters
        ----------
        fee: int or float

        Returns
        -------
        float
        """
        if fee > 1:
            fee = fee / 1000000
        return fee

    def get_exact_pools(self, cids: List[str]) -> List[CPCContainer]:
        """
        Gets the specific pools that will be used for calculations. It does this inefficiently to preserve the order.

        Parameters
        ----------
        cids: List

        Returns
        -------
        List
        """

        pools = [curve for curve in self.CCm if curve.cid == cids[0]]
        pools += [curve for curve in self.CCm if curve.cid == cids[1]]
        pools += [curve for curve in self.CCm if curve.cid == cids[2]]
        return pools

    def get_optimal_arb_trade_amts(self, cids: List[str], flt: str) -> float:
        """
        Gets the optimal trade 0 amount for a triangular arb cycle

        Parameters
        ----------
        cids: List
        flt: str

        Returns
        -------
        float
        """
        pools = self.get_exact_pools(cids=cids)
        tkn1 = self.get_tkn(pool=pools[0], tkn_num=1) if self.get_tkn(pool=pools[0], tkn_num=1) != flt else self.get_tkn(pool=pools[0], tkn_num=0)
        p0t0 = pools[0].x if self.get_tkn(pool=pools[0], tkn_num=0) == flt else pools[0].y
        p0t1 = pools[0].y if self.get_tkn(pool=pools[0], tkn_num=0) == flt else pools[0].x
        p1t0 = pools[1].x if tkn1 == self.get_tkn(pool=pools[1], tkn_num=0) else pools[1].y
        p1t1 = pools[1].y if tkn1 == self.get_tkn(pool=pools[1], tkn_num=0) else pools[1].x
        p2t0 = pools[2].x if self.get_tkn(pool=pools[2], tkn_num=0) != flt else pools[2].y
        p2t1 = pools[2].y if self.get_tkn(pool=pools[2], tkn_num=0) != flt else pools[2].x
        fee0 = self.get_fee_safe(pools[0].fee)
        fee1 = self.get_fee_safe(pools[1].fee)
        fee2 = self.get_fee_safe(pools[2].fee)

        if pools[1].params.exchange in self.ConfigObj.CARBON_V1_FORKS:
            y = pools[1].y
            z = pools[1].z
            A = pools[1].A
            B = pools[1].B
            C = (B * z + A * y) ** 2
            D = B * A * z + A ** 2 * y
            return (z * (-p0t0 * p2t0 * z + math.sqrt(C * p0t0 * p2t0 * p0t1 * p2t1))) / (p0t1 * C + p0t1 * D * p2t0 + z ** 2 * p2t0)

        return (-p1t0*p2t0*p0t0 + (p1t0*p2t0*p0t0*p1t1*p2t1*p0t1*(-fee1*fee2*fee0 + fee1*fee2 + fee1*fee0 - fee1 + fee2*fee0 - fee2 - fee0 + 1)) ** 0.5) / (p1t0*p2t0 - p2t0*p0t1*fee0 + p2t0*p0t1 + p1t1*p0t1*fee1*fee0 - p1t1*p0t1*fee1 - p1t1*p0t1*fee0 + p1t1*p0t1)
