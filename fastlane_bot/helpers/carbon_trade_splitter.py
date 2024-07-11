"""
Helper function to split Carbon trades into multiple trades, eg if ETH and WETH is involved

Defines the ``split_carbon_trades`` function 

TODO: maybe this should be moved into a slightly bigger context

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List
from json import loads, dumps
from fastlane_bot.config import Config
from fastlane_bot.helpers import TradeInstruction

def split_carbon_trades(cfg: Config, trade_instructions: List[TradeInstruction]) -> List[TradeInstruction]:
    """
    This method splits every trade instruction which includes a mix of gas tokens and/or a mix of Carbon deployments,
    into several trade instructions. For example, `NATIVE/WRAPPED -> TKN` is split into `NATIVE -> TKN` and `WRAPPED -> TKN`.

    Args:
        cfg: the configuration object.
        trade_instructions: A list of trade instructions.

    Returns:
        new_trade_instructions: A new list of trade instructions.
    """

    new_trade_instructions = []
    for trade_instruction in trade_instructions:
        if trade_instruction.exchange_name not in cfg.CARBON_V1_FORKS:
            new_trade_instructions.append(trade_instruction)
            continue

        carbon_exchanges = {}

        for tx in loads(trade_instruction.raw_txs.replace("'", '"').replace('Decimal("', '').replace('")', '')):
            pool = trade_instruction.db.get_pool(cid=str(tx["cid"]).split("-")[0])

            if cfg.NATIVE_GAS_TOKEN_ADDRESS in pool.get_tokens:
                pool_type = cfg.NATIVE_GAS_TOKEN_ADDRESS
            elif cfg.WRAPPED_GAS_TOKEN_ADDRESS in pool.get_tokens:
                pool_type = cfg.WRAPPED_GAS_TOKEN_ADDRESS
            else:
                pool_type = ''

            tx["tknin"] = _get_token_address(cfg, pool_type, trade_instruction.tknin)
            tx["tknout"] = _get_token_address(cfg, pool_type, trade_instruction.tknout)

            exchange_id = pool.exchange_name + pool_type
            if exchange_id in carbon_exchanges:
                carbon_exchanges[exchange_id].append(tx)
            else:
                carbon_exchanges[exchange_id] = [tx]

        assert len(carbon_exchanges) > 0, f"Carbon trade instruction raw_txs = {trade_instruction.raw_txs}"

        for txs in carbon_exchanges.values():
            new_trade_instructions.append(
                TradeInstruction(
                    ConfigObj=cfg,
                    db=trade_instruction.db,
                    cid=txs[0]["cid"],
                    tknin=txs[0]["tknin"],
                    tknout=txs[0]["tknout"],
                    amtin=sum([tx["amtin"] for tx in txs]),
                    amtout=sum([tx["amtout"] for tx in txs]),
                    _amtin_wei=sum([tx["_amtin_wei"] for tx in txs]),
                    _amtout_wei=sum([tx["_amtout_wei"] for tx in txs]),
                    raw_txs=dumps(txs)
                )
            )

    return new_trade_instructions

def _get_token_address(cfg: Config, pool_type: str, token_address: str) -> str:
    """
    This method takes a pool and a token as input,
    and determines the actual token which should be traded on that pool.

    If the pool supports trading the native token but the given token is the wrapped token,
    then the actual token which should be traded on that pool is the native token.

    If the pool supports trading the wrapped token but the given token is the native token,
    then the actual token which should be traded on that pool is the wrapped token.

    In all other cases, the actual token which should be traded on that pool is the given one.

    Args:
        pool_type: Native, Wrapped or Neither.
        token_address: The address of the token.

    Returns:
        the actual token which should be traded on then given pool.
    """

    if pool_type == cfg.NATIVE_GAS_TOKEN_ADDRESS and token_address == cfg.WRAPPED_GAS_TOKEN_ADDRESS:
        return cfg.NATIVE_GAS_TOKEN_ADDRESS
    if pool_type == cfg.WRAPPED_GAS_TOKEN_ADDRESS and token_address == cfg.NATIVE_GAS_TOKEN_ADDRESS:
        return cfg.WRAPPED_GAS_TOKEN_ADDRESS
    return token_address
