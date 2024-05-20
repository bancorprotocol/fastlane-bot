"""
[DOC-TODO-short description of what the file does, max 80 chars]

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import Dict, Any, List

from web3 import Web3
from web3.contract import Contract

from fastlane_bot.events.pools.base import Pool
from ..interfaces.event import Event

def _balances_A(contract: Contract) -> List[int]:
    return contract.caller.getReserves()

async def _async_balances_A(contract: Contract) -> List[int]:
    return await contract.caller.getReserves()

def _balances_B(contract: Contract) -> List[int]:
    return contract.caller.getStates()

async def _async_balances_B(contract: Contract) -> List[int]:
    return await contract.caller.getStates()

def _is_stable_A(contract: Contract) -> bool:
    return contract.caller.stable()

async def _async_is_stable_A(contract: Contract) -> bool:
    return await contract.caller.stable()

def _is_stable_B(contract: Contract) -> bool:
    return False

async def _async_is_stable_B(contract: Contract) -> bool:
    return False

EXCHANGE_INFO = {
    "velocimeter_v2": {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "equalizer_v2"  : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "aerodrome_v2"  : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "velodrome_v2"  : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "scale_v2"      : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "cleopatra_v2"  : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "stratum_v2"    : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "lynex_v2"      : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "nile_v2"       : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
    "xfai_v0"       : {"balances": _balances_B, "async_balances": _async_balances_B, "is_stable": _is_stable_B, "async_is_stable": _async_is_stable_B},
    "archly_v2"     : {"balances": _balances_A, "async_balances": _async_balances_A, "is_stable": _is_stable_A, "async_is_stable": _async_is_stable_A},
}

@dataclass
class SolidlyV2Pool(Pool):
    """
    Class representing a Solidly v2 pool.
    """
    base_exchange_name: str = "solidly_v2"
    exchange_name: str = "solidly_v2"
    fee: str = None
    router_address: str = None
    # If this is false, it's a Uni V2 style pool
    is_stable: bool = None


    @property
    def fee_float(self):
        return float(self.fee)

    @property
    def pool_type(self):
        return "stable" if self.is_stable else "volatile"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "address"

    @classmethod
    def event_matches_format(
        cls, event: Dict[str, Any], static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        Check if an event matches the format of a Uniswap v2 event.
        """
        event_args = event.args
        return (
            "reserve0" in event_args
            and event.address in static_pools[f"{exchange_name}_pools"]
        )

    def update_from_event(
        self, event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        data["tkn0_balance"] = event.args["reserve0"]
        data["tkn1_balance"] = event.args["reserve1"]
        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["strategy_id"] = 0
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        data["router"] = self.router_address
        return data

    def update_from_contract(
        self,
        contract: Contract,
        tenderly_fork_id: str = None,
        w3_tenderly: Web3 = None,
        w3: Web3 = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        exchange_info = EXCHANGE_INFO[self.exchange_name]
        balances = exchange_info["balances"](contract)
        self.is_stable = exchange_info["is_stable"](contract)
        params = {

            "tkn0_balance": balances[0],
            "tkn1_balance": balances[1],
            "exchange_name": self.exchange_name,
            "router": self.router_address,
            "pool_type": self.pool_type,
        }
        for key, value in params.items():
            self.state[key] = value
        return params

    async def async_update_from_contract(
        self,
        contract: Contract,
        tenderly_fork_id: str = None,
        w3_tenderly: Web3 = None,
        w3: Web3 = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        exchange_info = EXCHANGE_INFO[self.exchange_name]
        balances = await exchange_info["async_balances"](contract)
        self.is_stable = await exchange_info["async_is_stable"](contract)
        params = {

            "tkn0_balance": balances[0],
            "tkn1_balance": balances[1],
            "exchange_name": self.exchange_name,
            "router": self.router_address,
            "pool_type": self.pool_type,
        }
        for key, value in params.items():
            self.state[key] = value
        return params
