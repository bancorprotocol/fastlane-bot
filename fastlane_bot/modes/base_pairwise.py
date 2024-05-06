"""
Defines the base class for pairwise arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import abc
import itertools
from typing import List, Tuple, Any, Union

from arb_optimizer import CurveContainer

from fastlane_bot.modes.base import ArbitrageFinderBase


class ArbitrageFinderPairwiseBase(ArbitrageFinderBase):
    """
    Base class for pairwise arbitrage finder modes
    """

    @abc.abstractmethod
    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """
        pass

    @staticmethod
    def get_combos(
        CCm: CurveContainer, flashloan_tokens: List[str]
    ) -> Tuple[List[Any], List[Any]]:
        """
        Get combos for pairwise arbitrage

        Parameters
        ----------
        CCm : CurveContainer
            Container for all the curves
        flashloan_tokens : list
            List of flashloan tokens

        Returns
        -------
        all_tokens : list
            List of all tokens

        """
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
