import json
from fastlane_bot.helpers import TradeInstruction

def split_carbon_trades(cfg, trade_instructions: list[TradeInstruction]) -> list[TradeInstruction]:
    new_trade_instructions = []
    for trade_instruction in trade_instructions:
        if trade_instruction.exchange_name not in cfg.CARBON_V1_FORKS:
            new_trade_instructions.append(trade_instruction)
            continue

        carbon_exchanges = {}

        for tx in json.loads(trade_instruction.raw_txs.replace("'", '"').replace('Decimal("', '').replace('")', '')):
            curve = trade_instruction.db.get_pool(cid=str(tx["cid"]).split("-")[0])

            if cfg.NATIVE_GAS_TOKEN_ADDRESS in curve.get_tokens:
                id = cfg.NATIVE_GAS_TOKEN_ADDRESS
            elif cfg.WRAPPED_GAS_TOKEN_ADDRESS in curve.get_tokens:
                id = cfg.WRAPPED_GAS_TOKEN_ADDRESS
            else:
                id = cfg.ZERO_ADDRESS

            tx["tknin"] = _get_token_address(cfg, id, trade_instruction.tknin)
            tx["tknout"] = _get_token_address(cfg, id, trade_instruction.tknout)

            exchange_id = curve.exchange_name + id
            if exchange_id in carbon_exchanges:
                carbon_exchanges[exchange_id].append(tx)
            else:
                carbon_exchanges[exchange_id] = [tx]

        for txs in carbon_exchanges.values():
            new_trade_instructions.append(
                TradeInstruction(
                    ConfigObj=cfg,
                    db=trade_instruction.db,
                    cid=trade_instruction.cid,
                    tknin=trade_instruction.tknin,
                    tknout=trade_instruction.tknout,
                    amtin=sum([tx["amtin"] for tx in txs]),
                    amtout=sum([tx["amtout"] for tx in txs]),
                    _amtin_wei=sum([tx["_amtin_wei"] for tx in txs]),
                    _amtout_wei=sum([tx["_amtout_wei"] for tx in txs]),
                    raw_txs=json.dumps(txs)
                )
            )

    return new_trade_instructions

def _get_token_address(cfg, id: str, token_address: str) -> str:
    if id == cfg.NATIVE_GAS_TOKEN_ADDRESS and token_address == cfg.WRAPPED_GAS_TOKEN_ADDRESS:
        return cfg.NATIVE_GAS_TOKEN_ADDRESS
    if id == cfg.WRAPPED_GAS_TOKEN_ADDRESS and token_address == cfg.NATIVE_GAS_TOKEN_ADDRESS:
        return cfg.WRAPPED_GAS_TOKEN_ADDRESS
    return token_address
