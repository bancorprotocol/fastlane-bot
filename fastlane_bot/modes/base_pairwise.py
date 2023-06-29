# coding=utf-8
"""
Base class for pairwise arbitrage finder modes

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import abc
import itertools
from typing import List, Tuple, Any, Union

from fastlane_bot.modes.base import ArbitrageFinderBase
from fastlane_bot.tools.cpc import CPCContainer


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
        CCm: CPCContainer, flashloan_tokens: List[str]
    ) -> Tuple[List[Any], List[Any]]:
        """
        Get combos for pairwise arbitrage

        Parameters
        ----------
        CCm : CPCContainer
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
