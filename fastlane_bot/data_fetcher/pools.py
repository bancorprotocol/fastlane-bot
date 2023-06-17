from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Tuple, List

from web3.contract import Contract

from fastlane_bot import Config


@dataclass
class Pool(ABC):
    """
    Abstract base class representing a pool.

    Attributes:
        state (Dict[str, Any]): The state of the pool. Defaults to an empty dictionary.
    """
    state: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def get_common_data(
            event: Dict[str, Any], pool_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get common (common to all Pool child classes) data from an event and pool info.

        Args:
            event (Dict[str, Any]): The event data.
            pool_info (Dict[str, Any]): The pool information.

        Returns:
            Dict[str, Any]: A dictionary containing common data extracted from the event and pool info.
        """
        return {
            "last_updated_block": event["blockNumber"],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "pair_name": pool_info["pair_name"],
            "descr": pool_info["descr"],
            "address": event["address"],
        }

    @staticmethod
    @abstractmethod
    def update_from_event(
        event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from an event.

        Args:
            event_args (Dict[str, Any]): The event arguments.
            data (Dict[str, Any]): The pool data.

        Returns:
            Dict[str, Any]: The updated pool data.
        """
        pass

    @abstractmethod
    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        Update the pool state from a contract.
        """
        pass

    @staticmethod
    @abstractmethod
    def unique_key() -> str:
        """
        Returns the unique key for the pool.
        """
        pass


@dataclass
class SushiswapPool(Pool):
    """
    Class representing a Sushiswap pool.
    """
    exchange_name: str = "sushiswap_v2"

    @staticmethod
    def unique_key() -> str:
        return "address"

    @classmethod
    def event_matches_format(cls, event_args: Dict[str, Any]) -> bool:
        """
        Check if an event matches the format of a Sushiswap event.
        """
        return "reserve0" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from a Sushiswap event.

        Args:
            event_args (Dict[str, Any]): The event arguments.
            data (Dict[str, Any]): The pool data.

        Returns:
            Dict[str, Any]: The updated pool data.
        """
        event_args = event_args["args"]
        data["tkn0_balance"] = event_args["reserve0"]
        data["tkn1_balance"] = event_args["reserve1"]
        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        Update the pool state from a Sushiswap contract.

        Args:
            contract (Contract): The Sushiswap contract.

        Returns:
            Dict[str, Any]: The updated pool state.
        """
        reserve_balance = contract.caller.getReserves()
        params = {
            "fee": "0.003",
            "fee_float": 0.003,
            "tkn0_balance": reserve_balance[0],
            "tkn1_balance": reserve_balance[1],
            "exchange_name": "uniswap_v2",
        }
        for key, value in params.items():
            self.state[key] = value
        return params


@dataclass
class UniswapV2Pool(Pool):
    """
    Class representing a Uniswap v2 pool.
    """
    exchange_name: str = "uniswap_v2"

    @staticmethod
    def unique_key() -> str:
        return "address"

    @classmethod
    def event_matches_format(cls, event_args: Dict[str, Any]) -> bool:
        """
        Check if an event matches the format of a Uniswap v2 event.
        """
        return "reserve0" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from a Uniswap v2 event.

        Args:
            event_args (Dict[str, Any]): The event arguments.
            data (Dict[str, Any]): The pool data.

        Returns:
            Dict[str, Any]: The updated pool data.
        """
        event_args = event_args["args"]
        data["tkn0_balance"] = event_args["reserve0"]
        data["tkn1_balance"] = event_args["reserve1"]
        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        Update the pool state from a Uniswap v2 contract.

        Args:
            contract (Contract): The Uniswap v2 contract.

        Returns:
            Dict[str, Any]: The updated pool state.
        """
        reserve_balance = contract.caller.getReserves()
        params = {
            "fee": "0.003",
            "fee_float": 0.003,
            "tkn0_balance": reserve_balance[0],
            "tkn1_balance": reserve_balance[1],
            "exchange_name": "uniswap_v2",
        }
        for key, value in params.items():
            self.state[key] = value
        return params


@dataclass
class UniswapV3Pool(Pool):
    """
    Class representing a Uniswap v3 pool.
    """
    exchange_name: str = "uniswap_v3"

    @staticmethod
    def unique_key() -> str:
        return "address"

    @classmethod
    def event_matches_format(cls, event_args: Dict[str, Any]) -> bool:
        """
        Check if an event matches the format of a Uniswap v3 event.
        """
        return "sqrtPriceX96" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from an event.

        Args:
            event_args (Dict[str, Any]): The event arguments.
            data (Dict[str, Any]): The pool data.

        Returns:
            Dict[str, Any]: The updated pool data.
        """
        event_args = event_args["args"]
        data["liquidity"] = event_args["liquidity"]
        data["sqrt_price_q96"] = event_args["sqrtPriceX96"]
        data["tick"] = event_args["tick"]

        for key, value in data.items():
            self.state[key] = value

        try:
            data["cid"] = self.state["cid"]
            data["exchange_name"] = self.state["exchange_name"]
            data["fee"] = self.state["fee"]
            data["fee_float"] = self.state["fee_float"]
            data["tick_spacing"] = self.state["tick_spacing"]
        except KeyError as e:
            pass
        except Exception as e:
            print(f"[pools.update_from_event] Exception: {e}")
        return data

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        Update the pool state from a Uniswap v3 contract.

        Args:
            contract: A Uniswap v3 contract.
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
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
        }
        for key, value in params.items():
            self.state[key] = value
        return params


@dataclass
class BancorV3Pool(Pool):
    """
    Class representing a Bancor v3 pool.
    """
    exchange_name: str = "bancor_v3"

    @staticmethod
    def unique_key() -> str:
        return "tkn1_address"

    @classmethod
    def event_matches_format(cls, event_args: Dict[str, Any]) -> bool:
        return "pool" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from a Bancor v3 event.

        Args:
            event_args (Dict[str, Any]): The event arguments.
            data (Dict[str, Any]): The data to update.

        Returns:
            Dict[str, Any]: The updated data.
        """
        event_args = event_args["args"]
        if event_args["tkn_address"] == '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C':
            data["tkn0_balance"] = event_args["newLiquidity"]
        else:
            data["tkn1_balance"] = event_args["newLiquidity"]

        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        Update the pool state from a Bancor v3 contract.

        Args:
            contract: (Contract) The contract to update from.
        """
        pool_balances = contract.tradingLiquidity(self.state["tkn1_address"])
        params = {
            "fee": "0.000",
            "fee_float": 0.000,
            "tkn0_balance": pool_balances[0],
            "tkn1_balance": pool_balances[1],
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
        }
        for key, value in params.items():
            self.state[key] = value
        return params


@dataclass
class CarbonV1Pool(Pool):
    """
    Class representing a Carbon v1 pool.
    """
    exchange_name: str = "carbon_v1"

    @staticmethod
    def unique_key() -> str:
        return "cid"

    @classmethod
    def event_matches_format(cls, event_args: Dict[str, Any]) -> bool:
        """
        Check if the event matches the format for this pool.
        """
        return "order0" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from a Carbon v1 event.

        Args:
            event_args (Dict[str, Any]): The event arguments.
            data (Dict[str, Any]): The data to update.

        Returns:
            Dict[str, Any]: The updated data.
        """
        event_type = event_args["event"]
        print(f"\n *********** [pools.update_from_event] event_type: {event_type}, event_args: {event_args}, data: {data} *********** \n")
        data = CarbonV1Pool.parse_event(data, event_args, event_type)
        for key, value in data.items():
            self.state[key] = value
        return data

    @staticmethod
    def parse_event(data: Dict[str, Any], event_args: Dict[str, Any], event_type: str) -> Dict[str, Any]:
        """
        Parse the event args into a dict.

        Args:
            data: The data to update.
            event_args: The event arguments.
            event_type: The event type.

        Returns:
            Dict[str, Any]: The parsed data.
        """
        order0, order1 = CarbonV1Pool.parse_orders(event_args, event_type)
        data["cid"] = event_args["args"].get("id")
        data["y_0"] = order0[0]
        data["z_0"] = order0[1]
        data["A_0"] = order0[2]
        data["B_0"] = order0[3]
        data["y_1"] = order1[0]
        data["z_1"] = order1[1]
        data["A_1"] = order1[2]
        data["B_1"] = order1[3]
        return data

    @staticmethod
    def parse_orders(event_args: Dict[str, Any], event_type: str) -> Tuple[List[int], List[int]]:
        """
        Parse the orders from the event args. If the event type is StrategyDeleted, then return an empty list

        Args:
            event_args (Dict[str, Any]): The event args.
            event_type (str): The event type.

        Returns:
            Tuple[List[int], List[int]]: The orders.
['carbon_v1', 'bancor_v3', 'uniswap_v3', 'uniswap_v2']_17498741_17498743.json
        """
        if event_type != "StrategyDeleted":
            order0 = event_args["args"].get("order0")
            order1 = event_args["args"].get("order1")
        else:
            order0 = [0, 0, 0, 0]
            order1 = [0, 0, 0, 0]
        return order0, order1

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        strategy = contract.caller.strategy(self.state["cid"])
        fake_event = {
            "args": {
                "id": strategy[0],
                "order0": strategy[3][0],
                "order1": strategy[3][1],
            }
        }
        params = self.parse_event(self.state, fake_event, "None")
        params["fee"] = "0.002"
        params["fee_float"] = 0.002
        params["exchange_name"] = "carbon_v1"
        for key, value in params.items():
            self.state[key] = value
        return params


class PoolFactory:
    """
    Factory class for creating pools.
    """
    def __init__(self):
        self._creators = {}

    def register_format(self, format_name: str, creator: Pool) -> None:
        """
        Register a pool type.

        Args:
            format_name: The name of the pool type.
        """
        self._creators[format_name] = creator

    def get_pool(self, format_name: str) -> Pool:
        """
        Get a pool.

        Args:
            format_name: The name of the pool type.
        """
        creator = self._creators.get(format_name)
        if not creator:
            raise ValueError(format_name)
        return creator


# create an instance of the factory
pool_factory = PoolFactory()

# register your pool types
pool_factory.register_format("uniswap_v2", UniswapV2Pool)
pool_factory.register_format("uniswap_v3", UniswapV3Pool)
pool_factory.register_format("sushiswap_v2", SushiswapPool)
pool_factory.register_format("bancor_v3", BancorV3Pool)
pool_factory.register_format("carbon_v1", CarbonV1Pool)
