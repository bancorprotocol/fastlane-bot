# coding=utf-8
"""
Contains the exchange class for Balancer weighted pools. This class is responsible for handling Balancer exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.data.abi import BALANCER_VAULT_ABI, BALANCER_POOL_ABI_V1
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class Balancer(Exchange):
    """
    Balancer exchange class
    """

    exchange_name: str = "balancer"
    _tokens: List[str] = None

    def add_pool(self, pool: Pool):
        self.pools[pool.state["cid"]] = pool

    def get_abi(self):
        return BALANCER_VAULT_ABI

    @property
    def get_factory_abi(self):
        # Not used for Balancer
        return BALANCER_VAULT_ABI

    def get_pool_abi(self):
        return BALANCER_POOL_ABI_V1

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.AuthorizerChanged]

    async def get_fee(self, pool_id: str, contract: Contract) -> Tuple[str, float]:
        pool = self.get_pool(pool_id)
        if pool:
            fee, fee_float = pool.state["fee"], pool.state["fee_float"]
        else:
            fee = await contract.functions.getSwapFeePercentage().call()
            fee_float = float(fee) / 1e18
        return fee, fee_float

    async def get_tokens(self, address: str, contract: Contract, event: Any) -> []:
        pool_balances = await contract.caller.getPoolTokens(address).call()
        tokens = pool_balances[0]
        return tokens

    async def get_token_balances(self, address: str, contract: Contract, event: Any) -> []:
        pool_balances = await contract.caller.getPoolTokens(address)
        tokens = pool_balances[0]
        token_balances = pool_balances[1]
        return [{tkn: token_balances[idx]} for idx, tkn in enumerate(tokens)]

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        pool_balances = await contract.caller.getPoolTokens(address)
        tokens = pool_balances[0]
        token_balances = pool_balances[1]
        return token_balances[0]

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        pool_balances = await contract.caller.getPoolTokens(address)
        tokens = pool_balances[0]
        token_balances = pool_balances[1]
        return token_balances[1]

    async def get_tkn_n(self, address: str, contract: Contract, event: Any, index: int) -> str:
        pool_balances = await contract.caller.getPoolTokens(address)
        tokens = pool_balances[0]
        token_balances = pool_balances[1]
        return token_balances[index]