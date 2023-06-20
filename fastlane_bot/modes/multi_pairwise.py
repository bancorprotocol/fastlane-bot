from fastlane_bot.modes.base import ArbitrageFinderBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import CPCArbOptimizer


class FindArbitrageMultiPairwise(ArbitrageFinderBase):
    def get_trade_instructions(
        self, arb_mode, trade_instructions_df, curve_combo, tkn0, tkn1, src_token, r, O
    ):

        non_base_exchange_cids = [
            curve.cid
            for curve in curve_combo
            if curve.params.get("exchange") != self.base_exchange
        ]
        non_base_exchange_row = trade_instructions_df.loc[non_base_exchange_cids[0]]
        tkn0_into_base_exchange = non_base_exchange_row[0] < 0
        wrong_direction_cids = self.get_wrong_direction_cids(
            tkn0_into_base_exchange, trade_instructions_df
        )

        if non_base_exchange_cids and wrong_direction_cids:
            self.ConfigObj.logger.debug(
                f"\n\nRemoving wrong direction pools & rerunning optimizer\ntrade_instructions_df before: {trade_instructions_df.to_string()}"
            )
            new_curves = [
                curve for curve in curve_combo if curve.cid not in wrong_direction_cids
            ]

            # Rerun main flow with the new set of curves
            O, r, trade_instructions_df = self.rerun_flow_with_new_curves(
                new_curves, src_token, tkn0, tkn1
            )

        trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
        trade_instructions = r.trade_instructions()
        self.ConfigObj.logger.debug(
            f"\n\ntrade_instructions_df={trade_instructions_df}\ntrade_instructions_dic={trade_instructions_dic}\ntrade_instructions={trade_instructions}\n\n"
        )

        return trade_instructions_df, trade_instructions_dic, trade_instructions

    def get_wrong_direction_cids(self, tkn0_into_base_exchange, trade_instructions_df):
        return [
            idx
            for idx, row in trade_instructions_df.iterrows()
            if ("-0" in idx or "-1" in idx)
            and (
                (tkn0_into_base_exchange and row[0] < 0)
                or (not tkn0_into_base_exchange and row[0] > 0)
            )
        ]

    def rerun_flow_with_new_curves(self, new_curves, src_token, tkn0, tkn1):
        CC_cc = CPCContainer(new_curves)
        O = CPCArbOptimizer(CC_cc)
        pstart = {
            tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p
        }  # this intentionally selects the non_base_exchange curve
        r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
        trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
        self.ConfigObj.logger.debug(
            f"trade_instructions_df after: {trade_instructions_df.to_string()}"
        )
        return O, r, trade_instructions_df
