import itertools
from typing import List

from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import CPCArbOptimizer
from fastlane_bot.utils import num_format


def get_miniverse(y_match_curves_not_carbon, carbon_curves, x_match_curves_not_carbon, flt, arb_mode, all_miniverses):
    if arb_mode == "single_triangle":
        miniverses = list(
            itertools.product(y_match_curves_not_carbon, carbon_curves, x_match_curves_not_carbon))
        if miniverses:
            all_miniverses += list(zip([flt] * len(miniverses), miniverses))
    elif arb_mode == "multi_triangle":
        external_curve_combos = list(itertools.product(y_match_curves_not_carbon, x_match_curves_not_carbon))
        miniverses = [carbon_curves + list(combo) for combo in external_curve_combos]
        if miniverses:
            all_miniverses += list(zip([flt] * len(miniverses), miniverses))
    return all_miniverses
def get_all_miniverses(flashloan_tokens, CCm, arb_mode):
    candidates = []
    all_miniverses = []
    all_carbon_curves = CCm.byparams(exchange='carbon_v1').curves
    for flt in flashloan_tokens:  # may wish to run this for one flt at a time
        non_flt_carbon_curves = [x for x in all_carbon_curves if flt not in x.pair]
        for non_flt_carbon_curve in non_flt_carbon_curves:
            target_tkny = non_flt_carbon_curve.tkny
            target_tknx = non_flt_carbon_curve.tknx
            carbon_curves = CCm.bypairs(f"{target_tknx}/{target_tkny}").byparams(exchange='carbon_v1').curves
            y_match_curves = CCm.bypairs(
                set(CCm.filter_pairs(onein=target_tknx)) & set(CCm.filter_pairs(onein=flt)))
            x_match_curves = CCm.bypairs(
                set(CCm.filter_pairs(onein=target_tkny)) & set(CCm.filter_pairs(onein=flt)))
            y_match_curves_not_carbon = [x for x in y_match_curves if x.params.exchange != 'carbon_v1']
            x_match_curves_not_carbon = [x for x in x_match_curves if x.params.exchange != 'carbon_v1']
            all_miniverses = get_miniverse(y_match_curves_not_carbon, carbon_curves, x_match_curves_not_carbon, flt, arb_mode, all_miniverses)
    return all_miniverses
def _find_arbitrage_opportunities_carbon_single_triangle(
        self, flashloan_tokens: List[str], CCm: CPCContainer, *, mode: str = "bothin", result=None,
):
    assert mode == "bothin", "parameter not used"

    best_profit = 0
    best_src_token = None
    best_trade_instructions = None
    best_trade_instructions_df = None
    best_trade_instructions_dic = None
    ops = (
        best_profit,
        best_trade_instructions_df,
        best_trade_instructions_dic,
        best_src_token,
        best_trade_instructions
    )
    all_miniverses = get_all_miniverses(flashloan_tokens, CCm, arb_mode='single_triangle')

    for src_token, miniverse in all_miniverses:
        r = None
        self.C.logger.debug(f"Checking flashloan token = {src_token}, miniverse = {miniverse}")
        CC_cc = CPCContainer(miniverse)
        O = CPCArbOptimizer(CC_cc)
        try:
            r = O.margp_optimizer(src_token)
            profit_src = -r.result
            trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
            trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
            trade_instructions = r.trade_instructions()
        except Exception:
            continue

        cids = [ti['cid'] for ti in trade_instructions_dic]
        if src_token == 'BNT-FF1C':
            profit = profit_src
        else:
            try:
                price_src_per_bnt = CCm.bypair(pair=f"BNT-FF1C/{src_token}").byparams(exchange='bancor_v3')[0].p
                profit = profit_src/price_src_per_bnt
            except Exception as e:
                self.ConfigObj.logger.error(f"[TODO CLEAN UP]{e}")
        self.ConfigObj.logger.debug(f"Profit in bnt: {num_format(profit)} {cids}")
        try:
            netchange = trade_instructions_df.iloc[-1]
        except Exception as e:
            netchange = [500]  # an arbitrary large number

        if len(trade_instructions_df) > 0:
            condition_better_profit = (profit > best_profit)
            self.ConfigObj.logger.debug(f"profit > best_profit: {condition_better_profit}")
            condition_zeros_one_token = max(netchange) < 1e-4
            self.ConfigObj.logger.debug(f"max(netchange)<1e-4: {condition_zeros_one_token}")

            if condition_zeros_one_token and profit > self.ConfigObj.DEFAULT_MIN_PROFIT:  # candidate regardless if profitable
                candidates += [
                    (profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]

            if condition_better_profit and condition_zeros_one_token:
                best_profit, ops = self._find_ops(best_profit, ops, profit, src_token, trade_instructions,
                                                  trade_instructions_df, trade_instructions_dic)

    return candidates if result == self.AO_CANDIDATES else ops

def _find_arbitrage_opportunities_carbon_multi_triangle(
        self, flashloan_tokens: List[str], CCm: CPCContainer, *, mode: str = "bothin", result=None,
):
    assert mode == "bothin", "parameter not used"
    best_profit = 0
    best_src_token = None
    best_trade_instructions = None
    best_trade_instructions_df = None
    best_trade_instructions_dic = None
    ops = (
        best_profit,
        best_trade_instructions_df,
        best_trade_instructions_dic,
        best_src_token,
        best_trade_instructions
    )
    # candidates = []
    # all_miniverses = []
    # all_carbon_curves = CCm.byparams(exchange='carbon_v1').curves
    # for flt in flashloan_tokens:  # may wish to run this for one flt at a time
    #     non_flt_carbon_curves = [x for x in all_carbon_curves if flt not in x.pair]
    #     for non_flt_carbon_curve in non_flt_carbon_curves:
    #         target_tkny = non_flt_carbon_curve.tkny
    #         target_tknx = non_flt_carbon_curve.tknx
    #         carbon_curves = CCm.bypairs(f"{target_tknx}/{target_tkny}").byparams(exchange='carbon_v1').curves
    #         y_match_curves = CCm.bypairs(
    #             set(CCm.filter_pairs(onein=target_tknx)) & set(CCm.filter_pairs(onein=flt)))
    #         x_match_curves = CCm.bypairs(
    #             set(CCm.filter_pairs(onein=target_tkny)) & set(CCm.filter_pairs(onein=flt)))
    #         y_match_curves_not_carbon = [x for x in y_match_curves if x.params.exchange != 'carbon_v1']
    #         x_match_curves_not_carbon = [x for x in x_match_curves if x.params.exchange != 'carbon_v1']
            external_curve_combos = list(itertools.product(y_match_curves_not_carbon, x_match_curves_not_carbon))
            miniverses = [carbon_curves + list(combo) for combo in external_curve_combos]
            if miniverses:
                all_miniverses += list(zip([flt] * len(miniverses), miniverses))

    for src_token, miniverse in all_miniverses:
        r = None
        self.C.logger.debug(f"Checking flashloan token = {src_token}, miniverse = {[(x.pair, x.cid[-5:]) for x in miniverse]}")
        # print(f"Checking flashloan token = {src_token}, miniverse = {[(x.pair, x.cid[-5:]) for x in miniverse]}")
        CC_cc = CPCContainer(miniverse)
        O = CPCArbOptimizer(CC_cc)
        try:
            r = O.margp_optimizer(src_token)
            profit_src = -r.result
            trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
            trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
            trade_instructions = r.trade_instructions()

            """
            The following handles an edge case until parallel execution is available:
            1 Determine correct direction - opposite of non-Carbon pool
            2 Get cids of wrong-direction Carbon pools
            3 Create new CPCContainer with correct pools
            4 Rerun optimizer
            5 Resume normal flow
            """
            non_carbon_cids = [curve.cid for curve in miniverse if curve.params.get('exchange') != "carbon_v1"]
            non_carbon_row = trade_instructions_df.loc[non_carbon_cids[0]]
            tkn0_into_carbon = non_carbon_row[0] < 0
            wrong_direction_cids = []

            for idx, row in trade_instructions_df.iterrows():
                if ((tkn0_into_carbon and row[0] < 0) or (not tkn0_into_carbon and row[0] > 0)) and ("-0" in idx or "-1" in idx):
                    wrong_direction_cids.append(idx)

            if non_carbon_cids and wrong_direction_cids:
                self.ConfigObj.logger.debug(
                    f"\n\nRemoving wrong direction pools & rerunning optimizer\ntrade_instructions_df before: {trade_instructions_df.to_string()}")
                new_curves = [curve for curve in miniverse if curve.cid not in wrong_direction_cids]
                # Rerun main flow with the new set of curves
                CC_cc = CPCContainer(new_curves)
                O = CPCArbOptimizer(CC_cc)
                r = O.margp_optimizer(src_token)
                profit_src = -r.result
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions = r.trade_instructions()
                self.ConfigObj.logger.debug(f"trade_instructions_df after: {trade_instructions_df.to_string()}")

            self.ConfigObj.logger.debug(
                f"\n\ntrade_instructions_df={trade_instructions_df}\ntrade_instructions_dic={trade_instructions_dic}\ntrade_instructions={trade_instructions}\n\n")

        except Exception:
            continue

        cids = [ti['cid'] for ti in trade_instructions_dic]
        if src_token == 'BNT-FF1C':
            profit = profit_src
        else:
            try:
                price_src_per_bnt = CCm.bypair(pair=f"BNT-FF1C/{src_token}").byparams(exchange='bancor_v3')[0].p
                profit = profit_src/price_src_per_bnt
            except Exception as e:
                self.ConfigObj.logger.error(f"[TODO CLEAN UP]{e}")
        self.ConfigObj.logger.debug(f"Profit in bnt: {num_format(profit)} {cids}")
        try:
            netchange = trade_instructions_df.iloc[-1]
        except Exception as e:
            netchange = [500]  # an arbitrary large number

        if len(trade_instructions_df) > 0:
            condition_better_profit = (profit > best_profit)
            self.ConfigObj.logger.debug(f"profit > best_profit: {condition_better_profit}")
            condition_zeros_one_token = max(netchange) < 1e-4
            self.ConfigObj.logger.debug(f"max(netchange)<1e-4: {condition_zeros_one_token}")

            if condition_zeros_one_token and profit > self.ConfigObj.DEFAULT_MIN_PROFIT:  # candidate regardless if profitable
                candidates += [
                    (profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions)]

            if condition_better_profit and condition_zeros_one_token:
                best_profit, ops = self._find_ops(best_profit, ops, profit, src_token, trade_instructions,
                                                  trade_instructions_df, trade_instructions_dic)
            # except Exception as e:
            #     self.ConfigObj.logger.debug(f"Error in opt: {e}")
            #     continue

    return candidates if result == self.AO_CANDIDATES else ops