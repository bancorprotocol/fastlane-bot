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

from .base import Pool
from ..interfaces.event import Event


@dataclass
class BalancerPool(Pool):
    """
    Class representing a Balancer weighted pool.
    """

    exchange_name: str = "balancer"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "cid"

    @classmethod
    def event_matches_format(
        cls, event: Dict[str, Any], static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        see base class.

        Not using events to update Balancer pools
        """

        return False

    def update_from_event(
        self, event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.

        Not using events to update Balancer pools
        """

        return data

    async def update_from_contract(
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
        pool_balances = await contract.caller.getPoolTokens(self.state["anchor"])
        tokens = pool_balances[0]
        token_balances = pool_balances[1]
        params = {key: self.state[key] for key in self.state.keys()}

        for idx, tkn in enumerate(tokens):
            tkn_bal = "tkn" + str(idx) + "_balance"
            params[tkn_bal] = token_balances[idx]

        for key, value in params.items():
            self.state[key] = value

        return params
