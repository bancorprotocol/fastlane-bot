import json
from fastlane_bot.helpers import TradeInstruction

def split_carbon_trades(cfg, trade_instructions: list[TradeInstruction]) -> list[TradeInstruction]:
    new_trade_instructions = []
    for trade_instruction in trade_instructions:
        if trade_instruction.exchange_name not in cfg.CARBON_V1_FORKS:
            new_trade_instructions.append(trade_instruction)
            continue

        carbon_exchanges = {}

        raw_tx_str = trade_instruction.raw_txs.replace("'", '"').replace('Decimal("', '').replace('")', '')
        raw_txs = json.loads(raw_tx_str)

        for _tx in raw_txs:
            curve = trade_instruction.db.get_pool(cid=str(_tx["cid"]).split("-")[0])
            exchange = curve.exchange_name

            _tx["tknin"] = _get_token_address(cfg, curve, trade_instruction.tknin)
            _tx["tknout"] = _get_token_address(cfg, curve, trade_instruction.tknout)

            if exchange in carbon_exchanges:
                carbon_exchanges[exchange].append(_tx)
            else:
                carbon_exchanges[exchange] = [_tx]

        for txs in carbon_exchanges.values():
            amtin = 0
            amtout = 0
            _amtin_wei = 0
            _amtout_wei = 0
            for tx in txs:
                amtin += tx["amtin"]
                amtout += tx["amtout"]
                _amtin_wei += tx["_amtin_wei"]
                _amtout_wei += tx["_amtout_wei"]
                new_trade_instructions.append(
                    TradeInstruction(
                        db=trade_instruction.db,
                        ConfigObj=trade_instruction.ConfigObj,
                        cid=tx["cid"],
                        tknin=tx["tknin"],
                        tknout=tx["tknout"],
                        amtin=amtin,
                        amtout=amtout,
                        _amtin_wei=_amtin_wei,
                        _amtout_wei=_amtout_wei,
                        raw_txs=str(txs)
                    )
                )

    return new_trade_instructions

def _get_token_address(cfg, curve, token_address: str) -> str:
    if cfg.NATIVE_GAS_TOKEN_ADDRESS in curve.get_tokens and token_address == cfg.WRAPPED_GAS_TOKEN_ADDRESS:
        return cfg.NATIVE_GAS_TOKEN_ADDRESS
    if cfg.WRAPPED_GAS_TOKEN_ADDRESS in curve.get_tokens and token_address == cfg.NATIVE_GAS_TOKEN_ADDRESS:
        return cfg.WRAPPED_GAS_TOKEN_ADDRESS
    return token_address
