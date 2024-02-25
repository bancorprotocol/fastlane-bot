from typing import Any, List, Dict

from fastlane_bot.helpers import TradeInstruction, RouteStruct
from dataclasses import asdict


class WrapUnwrapProcessor:
    """
    Handles the decision-making for wrapping & unwrapping gas tokens within trade routes.

    This class tracks token balances of trades, and decides when to add wrap or unwrap trades.

    Typical usage example:
    wrap_unwrap_processor = WrapUnwrapProcessor(cfg=self.ConfigObj)
    route_struct_processed = wrap_unwrap_processor.add_wrap_or_unwrap_trades_to_route(trade_instructions=split_calculated_trade_instructions, route_struct=route_struct, flashloan_struct=flashloan_struct)

    """

    def __init__(self, cfg: Any):
        self.cfg = cfg

    def add_wrap_or_unwrap_trades_to_route(
        self,
        trade_instructions: List[TradeInstruction],
        route_struct: List[Dict],
        flashloan_struct: List,
    ) -> List[Dict]:
        """Adds wrap or unwrap trade actions to a route struct.

        This method takes in trade instructions, route struct and flashloan struct and returns a new route struct with wrap/unwrap trades added.

        Args:
            trade_instructions: a list of TradeInstruction objects
            route_struct: a list of Dictionaries containing the route struct to be submitted to the Fast Lane contract.
            flashloan_struct: a list containing flashloan instructions

        Returns:
            The route struct - an ordered List of Dictionaries - with the added wrap/unwrap trades.

        """
        self._init_balance_tracker(flashloan_struct)
        self._ensure_unique_flashloan_token()
        segmented_routes = self._segment_routes(trade_instructions, route_struct)
        return self._generate_new_route_struct(segmented_routes, route_struct)

    def _init_balance_tracker(self, flashloan_struct: List):
        """Initializes the balance tracker object.

        This function initializes the balance tracker with token amounts from the flashloan struct. It also adds a flag indicating if native/wrapped gas tokens are being flashloaned.

        Args:
            flashloan_struct: a list containing flashloan instructions
        """
        self.balance_tracker = {}
        self.flashloan_native_gas_token = False
        self.flashloan_wrapped_gas_token = False

        for flash in flashloan_struct:
            for idx, token in enumerate(flash["sourceTokens"]):
                self.balance_tracker[token] = flash["sourceAmounts"][idx]
                if token == self.cfg.NATIVE_GAS_TOKEN_ADDRESS:
                    self.flashloan_native_gas_token = True
                elif token == self.cfg.WRAPPED_GAS_TOKEN_ADDRESS:
                    self.flashloan_wrapped_gas_token = True

    def _ensure_unique_flashloan_token(self):
        """Performs a sanity check that we are not trying to flashloan wrapped & native gas token simultaneously.

        Raises:
            FlashloanTokenException: An error indicating that incompatible flashloan tokens are used.

        """
        if self.flashloan_wrapped_gas_token and self.flashloan_native_gas_token:
            raise self.FlashloanTokenException(
                "[WrapUnwrapProcessor _ensure_unique_flashloan_token] Cannot flashloan both wrapped & native gas tokens!"
            )

    def _segment_routes(
        self, trade_instructions: List[TradeInstruction], route_struct: List[Dict]
    ) -> Dict:
        """Sorts routes into like-trades.

        Sorts routes into 'segments', which are trades of the same token pair, ie ETH > BNT.

        Args:
            trade_instructions: a list of TradeInstruction objects
            route_struct: a list of Dictionaries containing the route struct to be submitted to the Fast Lane contract.

        Returns:
            A dict containing segments with key values of the token pair, ie: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'.
            For example:
                {
                '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': {
                    amt_out: 100000000
                    amt_in: 1000000000000000000
                    token_in: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
                    token_out: '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
                    trades: {1: "carbon_v1", 2: "uniswap_v2"}
                    }
                }

        """
        segmented_routes = {}
        for idx, route in enumerate(route_struct):
            real_tkn_in, real_tkn_out = trade_instructions[idx].get_real_tokens()
            pair = f"{real_tkn_in}/{real_tkn_out}"
            if pair not in segmented_routes:
                segmented_routes[pair] = {
                    "amt_out": 0,
                    "amt_in": 0,
                    "token_in": real_tkn_in,
                    "token_out": real_tkn_out,
                    "trades": {},
                }

            segmented_routes[pair]["amt_out"] += trade_instructions[idx].amtout_wei
            segmented_routes[pair]["amt_in"] += trade_instructions[idx].amtin_wei
            segmented_routes[pair]["trades"][idx] = trade_instructions[
                idx
            ].exchange_name
        return segmented_routes

    def _generate_new_route_struct(
        self, segmented_routes: Dict, route_struct: List[Dict]
    ) -> List[Dict]:
        """Generates the new route struct with wrap/unwrap trades added.

        This function loops through the

        Args:
            segmented_routes: a dictionary of trade actions aggregated into same-token trades.
            route_struct: a list of Dictionaries containing the route struct to be submitted to the Fast Lane contract.

        Returns:
            The processed list of trade action dictionaries.

            For example:
            [
                {
                "platformId": 10,
                "targetToken": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "sourceToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                "sourceAmount": "1000000000000000000",
                "minTargetAmount": "1000000000000000000",
                "deadline": "124124124",
                "customAddress": "0x0000000000000000000000000000000000000000",
                "customInt": 0,
                "customData": "0x",
                },
                ...
            ]

        """
        new_route_struct = []
        deadline = route_struct[0]["deadline"]

        for segment in segmented_routes.values():
            self._handle_wrap_or_unwrap(segment, deadline, new_route_struct)
            self._append_trades_based_on_exchange(
                segment, route_struct, new_route_struct
            )

        self._handle_final_balance(deadline, new_route_struct)
        return new_route_struct

    def _handle_wrap_or_unwrap(
        self, segment: Dict, deadline: int, new_route_struct: List[Dict]
    ):
        """Decides if a wrap or unwrap trade should be added.

        This function checks if wrapping or unwrapping is needed based on balance and token type.
        If needed, it adds a wrap/unwrap trade, and adjusts tracked balances

        Args:
            segment: The trade segment to process, including one or more trades that include the same input & output tokens.
            deadline: The deadline by which the trade must be executed.
            new_route_struct: The processed list of trade action dictionaries.

        """
        token_in = segment["token_in"]
        amount_in = segment["amt_in"]

        if amount_in > self.balance_tracker.get(token_in, 0):
            is_wrapping = token_in == self.cfg.WRAPPED_GAS_TOKEN_ADDRESS
            new_route_struct.append(
                self._get_wrap_or_unwrap_native_gas_tkn_struct(
                    deadline=deadline, wrap=is_wrapping, source_amount=amount_in
                )
            )
            self._adjust_balance_for_wrap_unwrap(is_wrapping, amount_in)

    def _adjust_balance_for_wrap_unwrap(self, is_wrapping: bool, amount: int):
        """Adjusts balances for native/wrapped gas token after a wrap/unwrap is added.

        This function adjusts the tracked balances when a wrap or unwrap trade is added.

        Args:
            is_wrapping: True if native tokens are being wrapped, False if tokens are being unwrapped.
            amount: The number of tokens to wrap or unwrap.

        """
        token_in = (
            self.cfg.NATIVE_GAS_TOKEN_ADDRESS
            if is_wrapping
            else self.cfg.WRAPPED_GAS_TOKEN_ADDRESS
        )
        token_out = (
            self.cfg.WRAPPED_GAS_TOKEN_ADDRESS
            if is_wrapping
            else self.cfg.NATIVE_GAS_TOKEN_ADDRESS
        )
        self._update_token_balance(
            token_address=token_in, token_amount=amount, add=False
        )
        self._update_token_balance(
            token_address=token_out, token_amount=amount, add=True
        )

    def _update_token_balance(self, token_address: str, token_amount: int, add: bool):
        """Updates the tracked balance of a token.

        This function adjusts the tracked balance of a token following a trade.

        Args:
            token_address: The address of the token for which to update the balance.
            token_amount: The number of tokens to change the balance by.
            add: True if the tokens should be added. False if the tokens should be subtracted.

        """
        _token_amount = -token_amount if not add else token_amount
        self.balance_tracker[token_address] = (
            self.balance_tracker.get(token_address, 0) + _token_amount
        )

    def _append_trades_based_on_exchange(
        self, segment: Dict, route_struct: List[Dict], new_route_struct: List[Dict]
    ):
        """Sort and add trade actions.

        This function sorts trade actions to be non-Carbon trades first, then adds them to the updated list of trade actions.

        Args:
            segment: The trade segment to process, including one or more trades that include the same input & output tokens.
            route_struct: The unprocessed list of trade action dictionaries.
            new_route_struct: The processed list of trade action dictionaries.

        """
        new_route_struct.extend(
            [
                route_struct[trade_idx]
                for trade_idx in segment["trades"]
                if segment["trades"][trade_idx] not in self.cfg.CARBON_V1_FORKS
            ]
            + [
                route_struct[trade_idx]
                for trade_idx in segment["trades"]
                if segment["trades"][trade_idx] in self.cfg.CARBON_V1_FORKS
            ]
        )
        self._update_token_balance(
            token_address=segment["token_in"], token_amount=segment["amt_in"], add=False
        )
        self._update_token_balance(
            token_address=segment["token_out"],
            token_amount=segment["amt_out"],
            add=True,
        )

    def _handle_final_balance(self, deadline: int, new_route_struct: List[Dict]):
        """Adds a final wrap/unwrap trade action.

        This function checks if there is a leftover balance of native/wrapped gas tokens at the end of the trade actions, and adds a final wrap/unwrap trade to convert the balance into the flashloan token.

        Args:
            deadline: the deadline for the trade to be completed by.
            new_route_struct: the processed list of trade actions, as dictionaries.


        """
        should_wrap = (
            self.flashloan_wrapped_gas_token
            and self.balance_tracker.get(self.cfg.NATIVE_GAS_TOKEN_ADDRESS, 0) > 0
        )
        should_unwrap = (
            self.flashloan_native_gas_token
            and self.balance_tracker.get(self.cfg.WRAPPED_GAS_TOKEN_ADDRESS, 0) > 0
        )

        if should_wrap or should_unwrap:
            new_route_struct.append(
                self._get_wrap_or_unwrap_native_gas_tkn_struct(
                    deadline=deadline, wrap=should_wrap or not should_unwrap
                )
            )

    def _get_wrap_or_unwrap_native_gas_tkn_struct(
        self, deadline: int, wrap: bool, source_amount: int = 0
    ):
        """
        This function provides a trade struct to wrap or unwrap the native gas token.

        :param deadline: the deadline by which the trade must be executed.
        :param wrap: if True, wrap the native gas token, else unwrap the native gas token.
        :param source_amount: the number of tokens to wrap or unwrap. If 0, this will wrap or unwrap the current balance of tokens.

        returns: A dictionary containing the wrap or unwrap trade instructions that will be sent to the contract.
        For example:
            {
            "platformId": 10,
            "targetToken": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "sourceToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "sourceAmount": "1000000000000000000",
            "minTargetAmount": "1000000000000000000",
            "deadline": "124124124",
            "customAddress": "0x0000000000000000000000000000000000000000",
            "customInt": 0,
            "customData": "0x",
            }

        """
        return asdict(
            RouteStruct(
                platformId=self.cfg.PLATFORM_ID_WRAP_UNWRAP,
                targetToken=self.cfg.WRAPPED_GAS_TOKEN_ADDRESS
                if wrap
                else self.cfg.NATIVE_GAS_TOKEN_ADDRESS,
                sourceToken=self.cfg.NATIVE_GAS_TOKEN_ADDRESS
                if wrap
                else self.cfg.WRAPPED_GAS_TOKEN_ADDRESS,
                sourceAmount=int(source_amount),
                minTargetAmount=int(source_amount),
                deadline=deadline,
                customAddress=self.cfg.WRAPPED_GAS_TOKEN_ADDRESS
                if wrap
                else self.cfg.NATIVE_GAS_TOKEN_ADDRESS,
                customInt=0,
                customData="0x",
            )
        )

    class FlashloanTokenException(Exception):
        """Error that represents incompatible an Flashloan token combination."""

        pass
