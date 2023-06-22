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
    def get_mono_direction_carbon_curves(self, miniverse, trade_instructions_df):

        columns = trade_instructions_df.columns
        bancor_3_row = trade_instructions_df.head(1)

        token_in = ''
        token_in_idx = -1
        print(f"columns= {columns}\nbancor 3 first row: {bancor_3_row}")


        first_bancor_v3_pool = trade_instructions_df.iloc[0]
        second_bancor_v3_pool = trade_instructions_df.iloc[1]

        for idx, token in enumerate(columns):
            if token == 'BNT-FF1C':
                continue
            if first_bancor_v3_pool[token] is not None:
                if first_bancor_v3_pool[token] < 0:
                    token_in = token
                    break
            elif second_bancor_v3_pool[token] is not None:
                if second_bancor_v3_pool[token] < 0:
                    token_in = token
                    break

        # for idx, token in enumerate(columns):
        #     if token == 'BNT-FF1C':
        #         continue
        #     print(f"bancor_3_row[token]: {bancor_3_row[token]}")
        #     print(f"bancor_3_row[idx]: {bancor_3_row[idx]}")
        #
        #     if bancor_3_row[token] is not None:
        #         val = bancor_3_row[token]
        #         if val < 0:
        #             token_in = token
        #             token_in_idx = idx
        #             break
        #     else:
        #         token_in = token
        #         token_in_idx = idx
        #         break

        non_carbon_cids = [curve.cid for curve in miniverse if curve.params.get('exchange') != "carbon_v1"]

        non_carbon_row = trade_instructions_df.loc[non_carbon_cids[0]]

        # columns = trade_instructions_df.columns
        # column_index = columns.get_loc(token_in)
        # tkn0_into_carbon = non_carbon_row[0] < 0

        print(f"[base_triangle] get_mono_direction_carbon_curves: token_in={token_in}, column_index={token_in_idx}")
        wrong_direction_cids = []

        for idx, row in trade_instructions_df.iterrows():
            if (row[token_in_idx] < 0) and (
                    "-0" in idx or "-1" in idx):
                wrong_direction_cids.append(idx)


        # for idx, row in trade_instructions_df.iterrows():
        #     if ((tkn0_into_carbon and row[0] < 0) or (not tkn0_into_carbon and row[0] > 0)) and (
        #             "-0" in idx or "-1" in idx):
        #         wrong_direction_cids.append(idx)
        # if non_carbon_cids and wrong_direction_cids:
        #     self.ConfigObj.logger.debug(
        #         f"\n\nRemoving wrong direction pools & rerunning optimizer\ntrade_instructions_df before: {trade_instructions_df.to_string()}")
        return [curve for curve in miniverse if curve.cid not in wrong_direction_cids]