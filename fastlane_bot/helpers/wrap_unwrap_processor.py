"""
Deals with wrap and unwrap trades (eg WETH <-> ETH) in the route.

Defines the ``add_wrap_or_unwrap_trades_to_route`` method.

TODO: see whether to consolidate this with other objects

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List
from dataclasses import asdict
from fastlane_bot.config import Config
from fastlane_bot.helpers import TradeInstruction, RouteStruct
from fastlane_bot.exceptions import FlashloanTokenException

def add_wrap_or_unwrap_trades_to_route(
    cfg: Config,
    flashloans: List[dict],
    routes: List[dict],
    trade_instructions: List[TradeInstruction]
) -> List[dict]:
    """
    This method adds wrap and/or unwrap routes.

    Args:
        cfg: the configuration object.
        flashloans: A list of flashloans.
        routes: A list of routes.
        trade_instructions: A list of trade instructions.

    Returns:
        new_routes: A new list of routes.
    """

    balance_tracker = {}
    for flashloan in flashloans:
        for token, amount in zip(flashloan["sourceTokens"], flashloan["sourceAmounts"]):
            balance_tracker[token] = amount

    flashloan_native_gas_token = cfg.NATIVE_GAS_TOKEN_ADDRESS in balance_tracker
    flashloan_wrapped_gas_token = cfg.WRAPPED_GAS_TOKEN_ADDRESS in balance_tracker

    if flashloan_native_gas_token and flashloan_wrapped_gas_token:
        raise FlashloanTokenException("[add_wrap_or_unwrap_trades_to_route] Cannot flashloan both wrapped & native gas tokens!")

    segmented_routes = {}
    for idx in range(len(routes)):
        pair = "/".join(trade_instructions[idx].get_real_tokens())
        if pair not in segmented_routes:
            segmented_routes[pair] = {
                "amt_out": 0,
                "amt_in": 0,
                "trades": {},
            }

        segmented_routes[pair]["amt_out"] += trade_instructions[idx].amtout_wei
        segmented_routes[pair]["amt_in"] += trade_instructions[idx].amtin_wei
        segmented_routes[pair]["trades"][idx] = trade_instructions[idx].exchange_name in cfg.CARBON_V1_FORKS

    new_routes = []
    deadline = routes[0]["deadline"]

    for pair, segment in segmented_routes.items():
        token_in, token_out = pair.split("/")
        amount_in = segment["amt_in"]

        if token_in in [cfg.NATIVE_GAS_TOKEN_ADDRESS, cfg.WRAPPED_GAS_TOKEN_ADDRESS] and amount_in > balance_tracker.get(token_in, 0):
            token_in_inv = cfg.NATIVE_GAS_TOKEN_ADDRESS if token_in == cfg.WRAPPED_GAS_TOKEN_ADDRESS else cfg.WRAPPED_GAS_TOKEN_ADDRESS
            new_routes.append(
                _get_wrap_or_unwrap_native_gas_tkn_struct(
                    cfg=cfg,
                    sourceToken=token_in_inv,
                    targetToken=token_in,
                    amount=amount_in,
                    deadline=deadline
                )
            )
            balance_tracker[token_in_inv] = balance_tracker.get(token_in_inv, 0) - amount_in
            balance_tracker[token_in] = balance_tracker.get(token_in, 0) + amount_in

        balance_tracker[token_in] = balance_tracker.get(token_in, 0) - segment["amt_in"]
        balance_tracker[token_out] = balance_tracker.get(token_out, 0) + segment["amt_out"]

        new_routes.extend([routes[trade_idx] for trade_idx in segment["trades"] if segment["trades"][trade_idx] == True])
        new_routes.extend([routes[trade_idx] for trade_idx in segment["trades"] if segment["trades"][trade_idx] == False])

    should_wrap = flashloan_wrapped_gas_token and balance_tracker.get(cfg.NATIVE_GAS_TOKEN_ADDRESS, 0) > 0
    should_unwrap = flashloan_native_gas_token and balance_tracker.get(cfg.WRAPPED_GAS_TOKEN_ADDRESS, 0) > 0

    if should_wrap or should_unwrap:
        new_routes.append(
            _get_wrap_or_unwrap_native_gas_tkn_struct(
                cfg=cfg,
                sourceToken=cfg.NATIVE_GAS_TOKEN_ADDRESS if should_wrap else cfg.WRAPPED_GAS_TOKEN_ADDRESS,
                targetToken=cfg.WRAPPED_GAS_TOKEN_ADDRESS if should_wrap else cfg.NATIVE_GAS_TOKEN_ADDRESS,
                amount=0,
                deadline=deadline
            )
        )

    return new_routes

def _get_wrap_or_unwrap_native_gas_tkn_struct(
    cfg: Config,
    sourceToken: str,
    targetToken: str,
    amount: int,
    deadline: int
) -> dict:
    return asdict(
        RouteStruct(
            platformId=cfg.EXCHANGE_IDS[cfg.WRAP_UNWRAP_NAME],
            sourceToken=sourceToken,
            targetToken=targetToken,
            sourceAmount=amount,
            minTargetAmount=amount,
            deadline=deadline,
            customAddress=cfg.ZERO_ADDRESS,
            customInt=0,
            customData="0x"
        )
    )
