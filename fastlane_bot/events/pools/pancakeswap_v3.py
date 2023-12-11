# coding=utf-8
"""
Contains the pool class for Uniswap v3. This class is responsible for handling Uniswap v3 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, List

from web3 import Web3
from web3.contract import Contract

from fastlane_bot import Config
from fastlane_bot.events.pools.base import Pool


@dataclass
class PancakeswapV3Pool(Pool):
    """
    Class representing a Uniswap v3 pool.
    """

    exchange_name: str = "pancakeswap_v3"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "address"

    @classmethod
    def event_matches_format(
        cls, event: Dict[str, Any], static_pools: Dict[str, Any]
    ) -> bool:
        """
        Check if an event matches the format of a Uniswap v3 event.
        """
        event_args = event["args"]
        return (
            "protocolFeesToken0" in event_args
            and event["address"] in static_pools["pancakeswap_v3_pools"]
        )

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        event_args = event_args["args"]
        data["liquidity"] = event_args["liquidity"]
        data["sqrt_price_q96"] = event_args["sqrtPriceX96"]
        data["tick"] = event_args["tick"]

        self.update_pool_state_from_data(data)

        try:
            data["cid"] = self.state.index.get_level_values("cid").tolist()[0]
            data["exchange_name"] = self.state.index.get_level_values(
                "exchange_name"
            ).tolist()[0]
            data["fee"] = self.state["fee"].iloc[0]
            data["fee_float"] = self.state["fee_float"].iloc[0]
            data["tick_spacing"] = self.state["tick_spacing"].iloc[0]
        except KeyError as e:
            pass
        except Exception as e:
            print(f"[pools.update_from_event] Exception: {e}")
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
        slot0 = contract.caller.slot0()
        fee = contract.caller.fee()
        params = {
            "tick": slot0[1],
            "sqrt_price_q96": slot0[0],
            "liquidity": contract.caller.liquidity(),
            "fee": fee,
            "fee_float": fee / 1e6,
            "tick_spacing": contract.caller.tickSpacing(),
            "exchange_name": self.state.index.get_level_values(
                "exchange_name"
            ).tolist()[0],
            "address": self.state.index.get_level_values("address").tolist()[0],
        }
        self.update_pool_state_from_data(params)
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
        slot0 = await contract.caller.slot0()
        fee = await contract.caller.fee()
        params = {
            "tick": slot0[1],
            "sqrt_price_q96": slot0[0],
            "liquidity": await contract.caller.liquidity(),
            "fee": fee,
            "fee_float": fee / 1e6,
            "tick_spacing": await contract.caller.tickSpacing(),
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
        }
        for key, value in params.items():
            self.state[key] = value
        return params
