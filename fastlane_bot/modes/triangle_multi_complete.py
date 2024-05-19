"""
Defines the multi-triangle-complete arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List
from itertools import product, combinations

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase

class ArbitrageFinderTriangleMultiComplete(ArbitrageFinderTriangleBase):
    def get_combos(self) -> List[Any]:
        combos = []

        for flt in self.flashloan_tokens:
            # Get the Carbon pairs
            carbon_pairs = sort_pairs(set([x.pair for x in self.CCm.curves if x.params.exchange in self.ConfigObj.CARBON_V1_FORKS]))
            
            # Create a set of unique tokens, excluding 'flt'
            x_tokens = {token for pair in carbon_pairs for token in pair.split('/') if token != flt}
            
            # Get relevant pairs containing the flashloan token
            flt_x_pairs = sort_pairs([f"{x}/{flt}" for x in x_tokens])
            
            # Generate all possible 2-item combinations from the unique tokens that arent the flashloan token
            x_y_pairs = sort_pairs(["{}/{}".format(x, y) for x, y in combinations(x_tokens, 2)])
            
            # Note the relevant pairs
            all_relevant_pairs = flt_x_pairs + x_y_pairs
            self.ConfigObj.logger.debug(f"len(all_relevant_pairs) {len(all_relevant_pairs)}")

            # Generate triangle groups
            triangle_groups = get_triangle_groups(flt, x_y_pairs)
            self.ConfigObj.logger.debug(f"len(triangle_groups) {len(triangle_groups)}")

            # Get pair info for the cohort
            all_relevant_pairs_info = get_all_relevant_pairs_info(self.CCm, all_relevant_pairs, self.ConfigObj.CARBON_V1_FORKS)
            
            # Generate valid triangles for the groups base on arb_mode
            valid_triangles = get_triangle_groups_stats(triangle_groups, all_relevant_pairs_info)
            
            # Get [(flt,curves)] analysis set for the flt
            flt_triangle_analysis_set = get_analysis_set_per_flt(flt, valid_triangles, all_relevant_pairs_info)
            
            # The entire analysis set for all flts
            combos.extend(flt_triangle_analysis_set)

        return combos

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

def get_all_relevant_pairs_info(CCm, all_relevant_pairs, carbon_v1_forks):
    # Get pair info for the cohort to allow decision making at the triangle level
    all_relevant_pairs_info = {}
    for pair in all_relevant_pairs:            
        all_relevant_pairs_info[pair] = {}
        pair_curves = CCm.bypair(pair)
        carbon_curves = []
        non_carbon_curves = []
        for x in pair_curves:
            if x.params.exchange in carbon_v1_forks:
                carbon_curves += [x]
            else:
                non_carbon_curves += [x]
        all_relevant_pairs_info[pair]['curves'] = non_carbon_curves + [carbon_curves] if len(carbon_curves) > 0 else non_carbon_curves  # condense carbon curves into a single list
        all_relevant_pairs_info[pair]['all_counts'] = len(pair_curves)
        all_relevant_pairs_info[pair]['carbon_counts'] = len(carbon_curves)
    return all_relevant_pairs_info

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

def get_analysis_set_per_flt(flt, valid_triangles, all_relevant_pairs_info):
    flt_triangle_analysis_set = []
    for triangle in valid_triangles:
        multiverse = [all_relevant_pairs_info[pair]['curves'] for pair in triangle]
        product_of_triangle = list(product(multiverse[0], multiverse[1], multiverse[2]))
        triangles_to_run = flatten_nested_items_in_list(product_of_triangle)
        flt_triangle_analysis_set += list(zip([flt] * len(triangles_to_run), triangles_to_run))        
    return flt_triangle_analysis_set
