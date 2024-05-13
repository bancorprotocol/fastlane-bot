"""
Defines the base class for triangular arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import abc
import itertools
from typing import List, Any, Tuple, Union

import pandas as pd

from fastlane_bot.modes.base import ArbitrageFinderBase
from fastlane_bot.tools.cpc import T

def sort_pairs(pairs):
    # Clean up the pairs alphabetically
    return ["/".join(sorted(pair.split('/'))) for pair in pairs]

def flatten_nested_items_in_list(nested_list):
    # unpack nested items
    flattened_list = []
    for items in nested_list:
        flat_list = []
        for item in items:
            if isinstance(item, list):
                flat_list.extend(item)
            else:
                flat_list.append(item)
        flattened_list.append(flat_list)
    return flattened_list

def get_triangle_groups(flt, x_y_pairs):
    # Get groups of triangles that conform to (flt/x , x/y, y/flt) where x!=y
    triangle_groups = []
    for pair in x_y_pairs:
        x,y = pair.split('/')
        triangle_groups += [("/".join(sorted([flt,x])), pair, "/".join(sorted([flt,y])))]
    return triangle_groups

def get_triangle_groups_stats(triangle_groups, all_relevant_pairs_info):
    # Get the stats on the triangle group cohort for decision making
    valid_carbon_triangles = []
    for triangle in triangle_groups:
        path_len = 0
        has_carbon = False
        for pair in triangle:
            if all_relevant_pairs_info[pair]['all_counts'] > 0:
                path_len += 1
            if all_relevant_pairs_info[pair]['carbon_counts'] > 0:
                has_carbon = True
        if path_len == 3 and has_carbon == True:
            valid_carbon_triangles.append(triangle)
    return valid_carbon_triangles

class ArbitrageFinderTriangleBase(ArbitrageFinderBase):
    """
    Base class for triangular arbitrage finder modes
    """

    @abc.abstractmethod
    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """
        pass

    @staticmethod
    def get_miniverse(
        y_match_curves_not_carbon: List[Any],
        base_exchange_curves: List[Any],
        x_match_curves_not_carbon: List[Any],
        flt: str,
        arb_mode: str,
        combos: List[Any],
    ) -> List[Any]:
        """
        Get miniverse for triangular arbitrage

        Parameters
        ----------
        y_match_curves_not_carbon : list
            List of curves that match the y token and are not on carbon
        base_exchange_curves : list
            List of curves on the base exchange
        x_match_curves_not_carbon : list
            List of curves that match the x token and are not on carbon
        flt : str
            Flashloan token
        arb_mode : str
            Arbitrage mode
        combos : list
            List of combos

        Returns
        -------
        combos : list
            List of combos

        """
        if arb_mode in ["single_triangle", "triangle"]:
            miniverses = list(
                itertools.product(
                    y_match_curves_not_carbon,
                    base_exchange_curves,
                    x_match_curves_not_carbon,
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

    def get_combos(
        self, flashloan_tokens: List[str], CCm: Any, arb_mode: str
    ) -> Tuple[List[str], List[Any]]:
        """
        Get combos for triangular arbitrage

        Parameters
        ----------
        flashloan_tokens : list
            List of flashloan tokens
        CCm : object
            CCm object
        arb_mode : str
            Arbitrage mode

        Returns
        -------
        combos : list
            List of combos

        """
        combos = []
        if arb_mode in ["b3_two_hop"]:
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
                    if len(base_exchange_curves) == 0:
                        continue

                    base_direction_pair = base_exchange_curves[0].pair
                    base_direction_one = [curve for curve in base_exchange_curves if curve.pair == base_direction_pair]
                    base_direction_two = [curve for curve in base_exchange_curves if curve.pair != base_direction_pair]
                    assert len(base_exchange_curves) == len(base_direction_one) + len(base_direction_two)
                    y_match_curves = CCm.bypairs(
                        set(CCm.filter_pairs(onein=target_tknx))
                        & set(CCm.filter_pairs(onein=flt))
                    )
                    x_match_curves = CCm.bypairs(
                        set(CCm.filter_pairs(onein=target_tkny))
                        & set(CCm.filter_pairs(onein=flt))
                    )

                    y_match_curves_not_carbon = [
                        x
                        for x in y_match_curves
                        if x.params.exchange != self.base_exchange
                    ]
                    if len(y_match_curves_not_carbon) == 0:
                        continue
                    x_match_curves_not_carbon = [
                        x
                        for x in x_match_curves
                        if x.params.exchange != self.base_exchange
                    ]
                    if len(x_match_curves_not_carbon) == 0:
                        continue
                    if len(base_direction_one) > 0:
                        combos = self.get_miniverse(
                            y_match_curves_not_carbon,
                            base_direction_one,
                            x_match_curves_not_carbon,
                            flt,
                            arb_mode,
                            combos,
                        )
                    if len(base_direction_two) > 0:
                        combos = self.get_miniverse(
                            y_match_curves_not_carbon,
                            base_direction_two,
                            x_match_curves_not_carbon,
                            flt,
                            arb_mode,
                            combos,
                        )
        return combos
    
    def get_all_relevant_pairs_info(self, CCm, all_relevant_pairs):
        # Get pair info for the cohort to allow decision making at the triangle level
        all_relevant_pairs_info = {}
        for pair in all_relevant_pairs:            
            all_relevant_pairs_info[pair] = {}
            pair_curves = CCm.bypair(pair)
            carbon_curves = []
            non_carbon_curves = []
            for x in pair_curves:
                if x.params.exchange in self.ConfigObj.CARBON_V1_FORKS:
                    carbon_curves += [x]
                else:
                    non_carbon_curves += [x]
            all_relevant_pairs_info[pair]['non_carbon_curves'] = non_carbon_curves
            all_relevant_pairs_info[pair]['carbon_curves'] = carbon_curves
            all_relevant_pairs_info[pair]['curves'] = non_carbon_curves + [carbon_curves] if len(carbon_curves) > 0 else non_carbon_curves  # condense carbon curves into a single list
            all_relevant_pairs_info[pair]['all_counts'] = len(pair_curves)
            all_relevant_pairs_info[pair]['carbon_counts'] = len(carbon_curves)
        return all_relevant_pairs_info

    def get_analysis_set_per_flt(self, flt, valid_triangles, all_relevant_pairs_info):
        flt_triangle_analysis_set = []
        for triangle in valid_triangles:
            multiverse = [all_relevant_pairs_info[pair]['curves'] for pair in triangle]
            product_of_triangle = list(itertools.product(multiverse[0], multiverse[1], multiverse[2]))
            triangles_to_run = flatten_nested_items_in_list(product_of_triangle)
            flt_triangle_analysis_set += list(zip([flt] * len(triangles_to_run), triangles_to_run))
        
        self.ConfigObj.logger.debug(f"[base_triangle.get_analysis_set_per_flt] Length of flt_triangle_analysis_set: {flt, len(flt_triangle_analysis_set)}")
        return flt_triangle_analysis_set

    def get_comprehensive_triangles(
        self, flashloan_tokens: List[str], CCm: Any
    ) -> Tuple[List[str], List[Any]]:
        """
        Get comprehensive combos for triangular arbitrage

        Parameters
        ----------
        flashloan_tokens : list
            List of flashloan tokens
        CCm : object
            CCm object

        Returns
        -------
        combos : list
            List of combos

        """
        combos = []
        for flt in flashloan_tokens:

            # Get the Carbon pairs
            carbon_pairs = sort_pairs(set([x.pair for x in CCm.curves if x.params.exchange in self.ConfigObj.CARBON_V1_FORKS]))
            
            # Create a set of unique tokens, excluding 'flt'
            x_tokens = {token for pair in carbon_pairs for token in pair.split('/') if token != flt}
            
            # Get relevant pairs containing the flashloan token
            flt_x_pairs = sort_pairs([f"{x}/{flt}" for x in x_tokens])
            
            # Generate all possible 2-item combinations from the unique tokens that arent the flashloan token
            x_y_pairs = sort_pairs(["{}/{}".format(x, y) for x, y in itertools.combinations(x_tokens, 2)])
            
            # Note the relevant pairs
            all_relevant_pairs = flt_x_pairs + x_y_pairs
            self.ConfigObj.logger.debug(f"len(all_relevant_pairs) {len(all_relevant_pairs)}")

            # Generate triangle groups
            triangle_groups = get_triangle_groups(flt, x_y_pairs)
            self.ConfigObj.logger.debug(f"len(triangle_groups) {len(triangle_groups)}")

            # Get pair info for the cohort
            all_relevant_pairs_info = self.get_all_relevant_pairs_info(CCm, all_relevant_pairs)
            
            # Generate valid triangles for the groups base on arb_mode
            valid_triangles = get_triangle_groups_stats(triangle_groups, all_relevant_pairs_info)
            
            # Get [(flt,curves)] analysis set for the flt
            flt_triangle_analysis_set = self.get_analysis_set_per_flt(flt, valid_triangles, all_relevant_pairs_info)
            
            # The entire analysis set for all flts
            combos.extend(flt_triangle_analysis_set)
        return combos

    def build_pstart(self, CCm, tkn0list, tkn1):
        tkn0list = [x for x in tkn0list if x not in [tkn1]]
        pstart = {}
        for tkn0 in tkn0list:
            try:
                pstart[tkn0] = CCm.bytknx(tkn0).bytkny(tkn1)[0].p
            except:
                try:
                    pstart[tkn0] = 1/CCm.bytknx(tkn1).bytkny(tkn0)[0].p
                except Exception as e:
                    self.ConfigObj.logger.info(f"[pstart build] {tkn0}/{tkn1} price error {e}")
        pstart[tkn1] = 1
        return pstart
