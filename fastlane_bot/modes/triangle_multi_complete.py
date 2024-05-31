"""
Defines the Triangular arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Any, Tuple, Union
import random
import itertools

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import MargPOptimizer

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
        pair_curves = CCm.bypair(pair)
        carbon_curves = [curve for curve in pair_curves if curve.params.exchange in carbon_v1_forks]
        other_curves = [curve for curve in pair_curves if curve.params.exchange not in carbon_v1_forks]
        all_relevant_pairs_info[pair] = {
            "has_any": len(pair_curves) > 0,
            "has_carbon": len(carbon_curves) > 0,
            "curves": other_curves
        }
        if len(carbon_curves) > 0:
            base_dir_one = [curve for curve in carbon_curves if curve.pair == carbon_curves[0].pair]
            base_dir_two = [curve for curve in carbon_curves if curve.pair != carbon_curves[0].pair]
            if len(base_dir_one) > 0:
                all_relevant_pairs_info[pair]["curves"].append(base_dir_one)
            if len(base_dir_two) > 0:
                all_relevant_pairs_info[pair]["curves"].append(base_dir_two)
    return all_relevant_pairs_info

def get_triangle_groups_stats(triangle_groups, all_relevant_pairs_info):
    # Get the stats on the triangle group cohort for decision making
    valid_carbon_triangles = []
    for triangle in triangle_groups:
        path_len = sum(all_relevant_pairs_info[pair]["has_any"] for pair in triangle)
        has_carbon = any(all_relevant_pairs_info[pair]["has_carbon"] for pair in triangle)
        if path_len == 3 and has_carbon == True:
            valid_carbon_triangles.append(triangle)
    return valid_carbon_triangles

def get_analysis_set_per_flt(flt, valid_triangles, all_relevant_pairs_info):
    flt_triangle_analysis_set = []
    for triangle in valid_triangles:
        multiverse = [all_relevant_pairs_info[pair]["curves"] for pair in triangle]
        product_of_triangle = list(itertools.product(multiverse[0], multiverse[1], multiverse[2]))
        triangles_to_run = flatten_nested_items_in_list(product_of_triangle)
        flt_triangle_analysis_set += list(zip([flt] * len(triangles_to_run), triangles_to_run))
    return flt_triangle_analysis_set

def get_params(self, CCm, dst_tokens, src_token):
    # For a triangle, the pstart of each dst_token is derived from its rate vs the src_token.
    # Since Carbon orders can contain diverse prices independent of external market prices, and
    # we require that the pstart be on the Carbon curve to get successful optimizer runs,
    # then for Carbon orders only we must randomize the pstart from the list of available Carbon curves.
    # Random selection chosen as opposed to iterating over all possible combinations.

    # ASSUMPTIONS: There must be a complete triangle arb available i.e. src_token->dst_token1->dst_token2->src_token
    sort_sequence = ['bancor_v2','bancor_v3'] + self.ConfigObj.UNI_V2_FORKS + self.ConfigObj.UNI_V3_FORKS
    pstart = {src_token: 1}
    for dst_token in [token for token in dst_tokens if token != src_token]:
        curves = list(CCm.bytknx(dst_token).bytkny(src_token))
        CC = CPCContainer(custom_sort(curves, sort_sequence, self.ConfigObj.CARBON_V1_FORKS))
        if CC:
            if CC[0].params['exchange'] in self.ConfigObj.CARBON_V1_FORKS: #only carbon curve options left
                pstart[dst_token] = random.choice(CC).p
            else:
                pstart[dst_token] = CC[0].p
        else:
            curves = list(CCm.bytknx(src_token).bytkny(dst_token))
            CC = CPCContainer(custom_sort(curves, sort_sequence, self.ConfigObj.CARBON_V1_FORKS))
            if CC:
                if CC[0].params['exchange'] in self.ConfigObj.CARBON_V1_FORKS: #only carbon curve options left
                    pstart[dst_token] = 1/(random.choice(CC).p)
                else:
                    pstart[dst_token] = 1 / CC[0].p
            else:
                return None
    return pstart

def custom_sort(data, sort_sequence, carbon_v1_forks):
    sort_order = {key: index for index, key in enumerate(sort_sequence) if key not in carbon_v1_forks}
    return sorted(data, key=lambda item: float('inf') if item.params['exchange'] in carbon_v1_forks else sort_order.get(item.params['exchange'], float('inf')))

class ArbitrageFinderTriangleMultiComplete(ArbitrageFinderTriangleBase):
    """
    Triangular arbitrage finder mode
    """

    arb_mode = "multi_triangle_complete"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """

        if candidates is None:
            candidates = []

        combos = self.get_comprehensive_triangles(self.flashloan_tokens, self.CCm)

        for src_token, miniverse in combos:
            try:
                CC_cc = CPCContainer(miniverse)
                O = MargPOptimizer(CC_cc)
                pstart = get_params(self, CC_cc, CC_cc.tokens(), src_token)
                r = O.optimize(src_token, params=dict(pstart=pstart))
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                if trade_instructions_dic is None or len(trade_instructions_dic) < 3:
                    # Failed to converge
                    continue
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions = r.trade_instructions()

            except Exception as e:
                self.ConfigObj.logger.info(f"[triangle multi] {e}")
                continue
            profit_src = -r.result

            # Get the cids
            cids = [ti["cid"] for ti in trade_instructions_dic]

            # Calculate the profit
            profit = self.calculate_profit(src_token, profit_src, self.CCm, cids)
            if str(profit) == "nan":
                self.ConfigObj.logger.debug("profit is nan, skipping")
                continue

            # Handle candidates based on conditions
            candidates += self.handle_candidates(
                best_profit,
                profit,
                trade_instructions_df,
                trade_instructions_dic,
                src_token,
                trade_instructions,
            )

            # Find the best operations
            best_profit, ops = self.find_best_operations(
                best_profit,
                ops,
                profit,
                trade_instructions_df,
                trade_instructions_dic,
                src_token,
                trade_instructions,
            )

        return candidates if self.result == self.AO_CANDIDATES else ops
    
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
        flashloan_tokens = [x.replace(self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS) for x in self.flashloan_tokens]
        flashloan_tokens = list(set(flashloan_tokens))

        for flt in flashloan_tokens:
            # Get the Carbon pairs
            carbon_pairs = sort_pairs(set([curve.pair for curve in self.CCm.curves if curve.params.exchange in self.ConfigObj.CARBON_V1_FORKS]))

            # Create a set of unique tokens excluding the flashloan token
            x_tokens = {token for pair in carbon_pairs for token in pair.split("/") if token != flt}
            x_tokens = list(set([x.replace(self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS) for x in x_tokens]))

            # Get relevant pairs containing the flashloan token
            flt_x_pairs = sort_pairs([f"{x_token}/{flt}" for x_token in x_tokens])

            # Generate all possible 2-item combinations from the unique tokens that arent the flashloan token
            x_y_pairs = sort_pairs(["{}/{}".format(x, y) for x, y in itertools.combinations(x_tokens, 2)])

            # Note the relevant pairs
            all_relevant_pairs = flt_x_pairs + x_y_pairs
            self.ConfigObj.logger.debug(f"[triangle_multi_complete.get_combos] all_relevant_pairs: {len(all_relevant_pairs)}")

            # Generate triangle groups
            triangle_groups = get_triangle_groups(flt, x_y_pairs)
            self.ConfigObj.logger.debug(f"[triangle_multi_complete.get_combos] triangle_groups: {len(triangle_groups)}")

            # Get pair info for the cohort
            all_relevant_pairs_info = get_all_relevant_pairs_info(self.CCm, all_relevant_pairs, self.ConfigObj.CARBON_V1_FORKS)

            # Generate valid triangles for the groups base on arb_mode
            valid_triangles = get_triangle_groups_stats(triangle_groups, all_relevant_pairs_info)

            # Get [(flt,curves)] analysis set for the flashloan token
            flt_triangle_analysis_set = get_analysis_set_per_flt(flt, valid_triangles, all_relevant_pairs_info)
            self.ConfigObj.logger.debug(f"[triangle_multi_complete.get_combos] flt_triangle_analysis_set {flt, len(flt_triangle_analysis_set)}")

            # The entire analysis set for all flashloan tokens
            combos.extend(flt_triangle_analysis_set)

        return combos
