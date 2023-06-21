import itertools

from fastlane_bot.modes.base import ArbitrageFinderBase


class ArbitrageFinderPairwiseBase(ArbitrageFinderBase):

    def get_combos(self, CCm, flashloan_tokens):
        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect)
            # tkn1 is always the token being flash loaned
            # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
            if tkn0 != tkn1
        ]
        return all_tokens, combos

    def get_curve_combos(
        self, arb_mode, base_exchange_curves, not_base_exchange_curves
    ):
        if arb_mode in {"multi", "pairwise_multi"}:
            return [
                [curve] + base_exchange_curves for curve in not_base_exchange_curves
            ]
        elif arb_mode in {"single", "pairwise_single"}:
            return list(
                itertools.product(not_base_exchange_curves, base_exchange_curves)
            )




