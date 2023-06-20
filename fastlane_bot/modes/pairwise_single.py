from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase


class FindArbitrageSinglePairwise(ArbitrageFinderPairwiseBase):
    def get_trade_instructions(
        self, arb_mode, trade_instructions_df, curve_combo, tkn0, tkn1, src_token, r, O
    ):
        trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
        trade_instructions = r.trade_instructions()
        self.ConfigObj.logger.debug(
            f"\n\ntrade_instructions_df={trade_instructions_df}\ntrade_instructions_dic={trade_instructions_dic}\ntrade_instructions={trade_instructions}\n\n"
        )
        return trade_instructions_df, trade_instructions_dic, trade_instructions
