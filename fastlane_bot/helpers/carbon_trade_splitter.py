from json import loads, dumps
from fastlane_bot.config import Config
from fastlane_bot.helpers import TradeInstruction

def split_carbon_trades(
    cfg: Config,
    trade_instructions: list[TradeInstruction]
) -> list[TradeInstruction]:
    """
    This method splits every trade instruction which includes a mix of gas tokens and/or a mix of Carbon deployments,
    into several trade instructions. For example, `NATIVE/WRAPPED -> TKN` is split into `NATIVE -> TKN` and `WRAPPED -> TKN`.

    Args:
        - `cfg`: the configuration object.
        - `trade_instructions`: A list of trade instructions.

    Returns:
        - `new_trade_instructions`: A new list of trade instructions.
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
                token_type = cfg.NATIVE_GAS_TOKEN_ADDRESS
            elif cfg.WRAPPED_GAS_TOKEN_ADDRESS in pool.get_tokens:
                token_type = cfg.WRAPPED_GAS_TOKEN_ADDRESS
            else:
                token_type = cfg.ZERO_ADDRESS

            tx["tknin"] = _get_token_address(cfg, token_type, trade_instruction.tknin)
            tx["tknout"] = _get_token_address(cfg, token_type, trade_instruction.tknout)

            exchange_id = pool.exchange_name + token_type
            if exchange_id in carbon_exchanges:
                carbon_exchanges[exchange_id].append(tx)
            else:
                carbon_exchanges[exchange_id] = [tx]

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

def _get_token_address(cfg, token_type: str, token_address: str) -> str:
    if token_type == cfg.NATIVE_GAS_TOKEN_ADDRESS and token_address == cfg.WRAPPED_GAS_TOKEN_ADDRESS:
        return cfg.NATIVE_GAS_TOKEN_ADDRESS
    if token_type == cfg.WRAPPED_GAS_TOKEN_ADDRESS and token_address == cfg.NATIVE_GAS_TOKEN_ADDRESS:
        return cfg.WRAPPED_GAS_TOKEN_ADDRESS
    return token_address
