# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + jupyter={"outputs_hidden": true}

import pandas as pd
from typing import List
from fastlane_bot.helpers.tradeinstruction import TradeInstruction

def _aggregate_carbon_trades(listti: List[dict]) -> List[TradeInstruction]:
    """
    Aggregate carbon independent IDs and create trade instructions.

    This function takes a list of dictionaries containing trade instructions,
    aggregates the instructions with carbon independent IDs, and creates
    a list of TradeInstruction objects.

    Parameters
    ----------
    listti : List[dict]
        A list of trade instructions as dictionaries.

    Returns
    -------
    List[TradeInstruction]
        A list of aggregated trade instructions as TradeInstruction objects.

    """
    df = pd.DataFrame(listti)
    carbons = df[df.cid.str.contains("-")].copy()
    nocarbons = df[~df.cid.str.contains("-")]
    carbons["pair_sorting"] = carbons.tknin + carbons.tknout

    new_trade_instructions = [
        {
            "pair_sorting": pair_sorting,
            "cid": newdf.cid.values[0],
            "tknin": newdf.tknin.values[0],
            "amtin": newdf.amtin.sum(),
            "tknout": newdf.tknout.values[0],
            "amtout": newdf.amtout.sum(),
            "raw_txs": str(newdf.to_dict(orient="records")),
        }
        for pair_sorting, newdf in carbons.groupby("pair_sorting")
    ]

    nocarbons["pair_sorting"] = nocarbons.tknin + nocarbons.tknout
    nocarbons["raw_txs"] = str([])
    new_trade_instructions.extend(nocarbons.to_dict(orient="records"))

    trade_instructions = [
        TradeInstruction(**instruction)
        for instruction in new_trade_instructions
    ]

    trade_instructions.sort(key=lambda x: x.pair_sorting)

    return trade_instructions



original_input = [{'cid': '3743106036130323098097120681749450326030-0', 'tknin': 'WETH-6Cc2', 'amtin': 0.1265443077509661, 'tknout': 'BNT-FF1C', 'amtout': -500.0}, {'cid': '8847341539944400050047739793225973497926', 'tknin': 'BNT-FF1C', 'amtin': 485.1494996276915, 'tknout': 'WETH-6Cc2', 'amtout': -0.12919924675225047}]


old_incorrect_output = [TradeInstruction(cid='3743106036130323098097120681749450326030-0', tknin='WETH-6Cc2', amtin=0.12655696344731082, tknout='BNT-FF1C', amtout=-500.0, pair_sorting='WETH-6Cc2BNT-FF1C', raw_txs="[{'cid': '3743106036130323098097120681749450326030-0', 'tknin': 'WETH-6Cc2', 'amtin': 0.12655696344731082, 'tknout': 'BNT-FF1C', 'amtout': -500.0, 'pair_sorting': 'WETH-6Cc2BNT-FF1C'}]", custom_data=''),
                  TradeInstruction(cid='8847341539944400050047739793225973497926', tknin='BNT-FF1C', amtin=490.04999962393083, tknout='WETH-6Cc2', amtout=-0.12919924675225047, pair_sorting='BNT-FF1CWETH-6Cc2', raw_txs='[]', custom_data='')]


correct_output = [TradeInstruction(cid='8847341539944400050047739793225973497926', tknin='BNT-FF1C', amtin=485.1494996276915, tknout='WETH-6Cc2', amtout=-0.12919924675225047, pair_sorting='BNT-FF1CWETH-6Cc2', raw_txs='[]', custom_data=''),
                  TradeInstruction(cid='3743106036130323098097120681749450326030-0', tknin='WETH-6Cc2', amtin=0.1265443077509661, tknout='BNT-FF1C', amtout=-500.0, pair_sorting='WETH-6Cc2BNT-FF1C', raw_txs="[{'cid': '3743106036130323098097120681749450326030-0', 'tknin': 'WETH-6Cc2', 'amtin': 0.1265443077509661, 'tknout': 'BNT-FF1C', 'amtout': -500.0, 'pair_sorting': 'WETH-6Cc2BNT-FF1C'}]", custom_data='')]


new_output = _aggregate_carbon_trades(original_input)


assert new_output == correct_output, "incorrect output"

new_output
