import json
from typing import List, Dict

from fastlane_bot.helpers import TradeInstruction


class CarbonTradeSplitter:
    NATIVE = "native"
    WRAPPED = "wrapped"
    NEITHER = "neither"

    def __init__(self, ConfigObj):
        self.ConfigObj = ConfigObj

    def split_carbon_trades(
        self, trade_instructions: List[TradeInstruction]
    ) -> List[TradeInstruction]:
        """Splits Carbon trades that cannot be aggregated into a single trade action.

        This function split a single Carbon trade into multiple trades for cases that include a mix of tokens or different Carbon deployments.
        For example NATIVE/WRAPPED -> TKN -> NATIVE -> TKN & WRAPPED -> TKN.

        Args:
            trade_instructions: The list of TradeInstruction objects.

        Returns:
            The processed list of TradeInstruction objects after splitting incompatible trades.

        """
        new_trade_list = []
        for trade in trade_instructions:
            if not self._is_carbon_trade(trade):
                new_trade_list.append(trade)
                continue

            carbon_exchanges = self._process_carbon_trades(trade)
            self._create_new_trades_from_carbon_exchanges(
                carbon_exchanges, trade, new_trade_list
            )

        return new_trade_list

    def _is_carbon_trade(self, trade: TradeInstruction) -> bool:
        """Checks if a trade is on a Carbon deployment.

        Args:
            trade: a single TradeInstruction object.

        Returns:
            True if the trade is on a Carbon deployment. False otherwise.

        """
        return trade.exchange_name in self.ConfigObj.CARBON_V1_FORKS

    def _get_real_tkn(self, token_address: str, token_type: str):
        """Returns the correct token address for the trade.

        This function returns the real token address for the pool. If the token isn't the native/wrapped gas token address, it just returns the token.
        If the token is native/wrapped, it will use the token_type to return the correct address.

        Args:
            token_address: the token address
            token_type: the self.NATIVE, self.WRAPPED, or SELF.NEITHER

        Returns:
            The correct token address for the pool.

        """
        if token_address not in [
            self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS,
            self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS,
        ]:
            return token_address
        return (
            self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS
            if token_type == self.NATIVE
            else self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
        )

    def _process_carbon_trades(self, trade: TradeInstruction) -> Dict:
        """Processes

        Process Carbon trades and organize them by exchange and token type.

        Args:
            trade: a single TradeInstruction object

        Returns:
            A dictionary containing a list of

        """
        carbon_exchanges = {}

        raw_tx_str = trade.raw_txs.replace("'", '"')

        raw_txs = json.loads(raw_tx_str)

        for _tx in raw_txs:
            curve = trade.db.get_pool(cid=str(_tx["cid"]).split("-")[0])
            exchange = curve.exchange_name
            token_type = self._get_token_type(curve)

            if exchange not in carbon_exchanges:
                carbon_exchanges[exchange] = self._initialize_exchange_data()

            self._update_exchange_data(
                carbon_exchanges[exchange], token_type, _tx, trade
            )

        return carbon_exchanges

    def _get_token_type(self, curve) -> str:
        """Determines if the trade uses native or wrapped gas tokens.

        Args:
            curve: the Pool object representing the curve.

        Returns:
            A string indicating if the curve contains native gas tokens, wrapped gas tokens, or neither.

        """
        if self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS in curve.get_tokens:
            return self.NATIVE
        elif self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS in curve.get_tokens:
            return self.WRAPPED
        return self.NEITHER

    def _initialize_exchange_data(self) -> Dict:
        """Initializes data structure for a new exchange."""
        return {
            self.NATIVE: self._new_trade_data_structure(),
            self.WRAPPED: self._new_trade_data_structure(),
            self.NEITHER: self._new_trade_data_structure(),
        }

    def _new_trade_data_structure(self) -> Dict:
        """Initializes a new trade data structure."""
        return {
            "raw_txs": [],
            "amtin": 0,
            "amtout": 0,
            "_amtin_wei": 0,
            "_amtout_wei": 0,
        }

    def _update_exchange_data(
        self, exchange_data: Dict, token_type: str, _tx: Dict, trade: TradeInstruction
    ):
        """Combines like-trades.

        Update exchange data with information from a transaction.

        Args:
            exchange_data: The dictionary containing trades for each Carbon deployment being traded through.
            token_type: a string indicating if the pool contains native/wrapped gas token, or neither.
            _tx: the TX dictionary containing trade details.
            trade: the TradeInstruction object.

        """
        _tx["tknin"] = self._get_real_tkn(trade.tknin, token_type)
        _tx["tknout"] = self._get_real_tkn(trade.tknout, token_type)

        data = exchange_data[token_type]
        data["raw_txs"].append(_tx)
        data["amtin"] += _tx["amtin"]
        data["amtout"] += _tx["amtout"]
        data["_amtin_wei"] += _tx["_amtin_wei"]
        data["_amtout_wei"] += _tx["_amtout_wei"]
        data["tknin"] = _tx["tknin"]
        data["tknout"] = _tx["tknout"]

    def _create_new_trades_from_carbon_exchanges(
        self,
        carbon_exchanges: Dict,
        original_trade: TradeInstruction,
        new_trade_list: List[TradeInstruction],
    ):
        """Creates new TradeInstruction instances from processed Carbon exchanges data.

        This function adds trades that were added as a result of splitting Carbon trades.

         Args:
             carbon_exchanges: The list of Carbon deployments being traded through in this trade.
             original_trade: The original TradeInstruction object, utilized here to pass the db & Config objects.
             new_trade_list: The updated list of TradeInstruction objects with any trades that were added from the splitting process.

        """
        for exchange, data in carbon_exchanges.items():
            for token_type, trade_data in data.items():
                if trade_data["raw_txs"]:
                    trade_data["db"] = original_trade.db
                    trade_data["ConfigObj"] = original_trade.ConfigObj
                    trade_data["cid"] = trade_data["raw_txs"][0]["cid"]
                    trade_data["raw_txs"] = str(trade_data["raw_txs"])
                    new_trade_list.append(TradeInstruction(**trade_data))
