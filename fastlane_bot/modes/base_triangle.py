import itertools

from fastlane_bot.modes.base import ArbitrageFinderBase


class ArbitrageFinderTriangleBase(ArbitrageFinderBase):

    @staticmethod
    def get_miniverse(
        y_match_curves_not_carbon,
        base_exchange_curves,
        x_match_curves_not_carbon,
        flt,
        arb_mode,
        combos,
    ):
        if arb_mode in ["single_triangle", "triangle"]:
            miniverses = list(
                itertools.product(
                    y_match_curves_not_carbon, base_exchange_curves, x_match_curves_not_carbon
                )
            )
        else:
            external_curve_combos = list(
                itertools.product(y_match_curves_not_carbon, x_match_curves_not_carbon)
            )
            miniverses = [
                base_exchange_curves + list(combo) for combo in external_curve_combos
            ]
        if miniverses:
            combos += list(zip([flt] * len(miniverses), miniverses))
        return combos

    def get_combos(self, flashloan_tokens, CCm, arb_mode):
        combos = []
        if arb_mode in ["single_triangle_bancor3", "bancor_v3"]:
            combos = [
                (tkn0, tkn1)
                for tkn0, tkn1 in itertools.product(flashloan_tokens, flashloan_tokens)
                # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
                if tkn0 != tkn1
            ]
        else:
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
                    y_match_curves = CCm.bypairs(
                        set(CCm.filter_pairs(onein=target_tknx))
                        & set(CCm.filter_pairs(onein=flt))
                    )
                    x_match_curves = CCm.bypairs(
                        set(CCm.filter_pairs(onein=target_tkny))
                        & set(CCm.filter_pairs(onein=flt))
                    )
                    y_match_curves_not_carbon = [
                        x for x in y_match_curves if x.params.exchange != self.base_exchange
                    ]
                    x_match_curves_not_carbon = [
                        x for x in x_match_curves if x.params.exchange != self.base_exchange
                    ]
                    combos = self.get_miniverse(
                        y_match_curves_not_carbon,
                        base_exchange_curves,
                        x_match_curves_not_carbon,
                        flt,
                        arb_mode,
                        combos,
                    )
        return combos
