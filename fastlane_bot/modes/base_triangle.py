import abc

from fastlane_bot.modes.base import ArbitrageFinderBase


class ArbitrageFinderMultiBase(ArbitrageFinderBase):

    @abc.abstractmethod
    def get_trade_instructions(
        self, arb_mode, trade_instructions_df, curve_combo, tkn0, tkn1, src_token, r, O
    ):
        pass

    def find_arbitrage(self, arb_mode: str):
        pass

    def optimize(self, arb_mode, src_token, curve_combo, tkn0, tkn1, O, CC_cc):
        pass
