from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot import Config
from fastlane_bot.data.abi import (
    UNISWAP_V2_POOL_ABI,
    UNISWAP_V3_POOL_ABI,
    SUSHISWAP_POOLS_ABI,
    CARBON_CONTROLLER_ABI,
    BANCOR_V3_POOL_COLLECTION_ABI,
)
from fastlane_bot.data_fetcher.pools import Pool


@dataclass
class Exchange(ABC):
    cfg: Config
    pools: Dict[str, Pool] = field(default_factory=dict)

    def get_pools(self) -> List[Pool]:
        return list(self.pools.values())

    @abstractmethod
    def add_pool(self, pool: Pool):
        pass

    @abstractmethod
    def get_abi(self):
        pass

    @abstractmethod
    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        pass

    @abstractmethod
    def get_fee(self, address: str, contract: Contract) -> float:
        pass

    @abstractmethod
    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        pass

    @abstractmethod
    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        pass

    def get_pool(self, key: str) -> Pool:
        """

        Parameters
        ----------
        key: str
            pool_address if UniswapV2 or SushiswapV2 or UniswapV3
            else tkn1_address if BancorV3
            else cid if Carbon

        Returns
        -------
        Pool
            The pool object

        """
        return self.pools[key] if key in self.pools else None


@dataclass
class UniswapV2(Exchange):
    exchange_name: str = "uniswap_v2"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return UNISWAP_V2_POOL_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.003", 0.003

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token0().call()

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token1().call()


@dataclass
class SushiswapV2(Exchange):
    exchange_name: str = "sushiswap_v2"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return SUSHISWAP_POOLS_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.003", 0.003

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token0().call()

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token1().call()


@dataclass
class UniswapV3(Exchange):
    exchange_name: str = "uniswap_v3"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return UNISWAP_V3_POOL_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Swap]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        pool = self.get_pool(address)
        fee, fee_float = (
            (pool.state["fee"], pool.state["fee_float"])
            if pool
            else (
                contract.functions.fee().call(),
                float(contract.functions.fee().call()) / 1e6,
            )
        )
        return fee, fee_float

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token0().call()

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token1().call()


@dataclass
class BancorV3(Exchange):
    exchange_name: str = "bancor_v3"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["tkn1_address"]] = pool

    def get_abi(self):
        return BANCOR_V3_POOL_COLLECTION_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.TradingLiquidityUpdated]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.000", 0.000

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return self.cfg.BNT_ADDRESS

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return address


@dataclass
class CarbonV1(Exchange):

    exchange_name: str = "carbon_v1"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["cid"]] = pool

    def get_abi(self):
        return CARBON_CONTROLLER_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [
            contract.events.StrategyCreated,
            contract.events.StrategyUpdated,
            contract.events.StrategyDeleted,
        ]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.002", 0.002

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        if event is None:
            return contract.functions.token0().call()
        else:
            return event["args"]["token0"]

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        if event is None:
            return contract.functions.token1().call()
        else:
            return event["args"]["token1"]


class ExchangeFactory:
    def __init__(self, cfg: Config = None):
        self._creators = {}
        self.cfg = cfg

    def register_exchange(self, key, creator):
        self._creators[key] = creator

    def get_exchange(self, key):
        creator = self._creators.get(key)
        if not creator:
            raise ValueError(key)
        return creator(cfg=self.cfg)


# Create a single instance of ExchangeFactory
exchange_factory = ExchangeFactory()

# Register the exchanges with the factory
exchange_factory.register_exchange("uniswap_v2", UniswapV2)
exchange_factory.register_exchange("uniswap_v3", UniswapV3)
exchange_factory.register_exchange("sushiswap_v2", SushiswapV2)
exchange_factory.register_exchange("bancor_v3", BancorV3)
exchange_factory.register_exchange("carbon_v1", CarbonV1)
