import os
from typing import Any, List, Dict

from web3 import AsyncWeb3

from fastlane_bot.events.exchanges import exchange_factory


def get_contract_chunks(contracts: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    return [contracts[i : i + 1000] for i in range(0, len(contracts), 1000)]


def get_abis_and_exchanges(mgr: Any) -> Dict[str, Any]:
    abis = {}
    exchanges = {}
    for exchange in mgr.exchanges:
        exchanges[exchange] = exchange_factory.get_exchange(key=exchange, cfg=mgr.cfg, exchange_initialized=False)
        abis[exchange] = exchanges[exchange].get_abi()
    return abis
