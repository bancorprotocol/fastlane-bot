from .Pool import Pool
from .BasePool import BasePool

BASE_CACHE_EXPIRES: int = 10 * 60  # 10 min

abi = [
    {"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    {"name":"balances","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    {"name":"base_cache_updated","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"base_virtual_price","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"base_pool","outputs":[{"type":"address","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class Pool8(Pool):
    def __init__(self, address: str, coins: list[any]):
        super().__init__(address, abi)
        self.coins = [coins[n](self.contract.functions.coins(n).call(), address) for n in range(len(coins))]
        self.balances = [self.contract.functions.balances(n).call() for n in range(len(coins))]
        self.base_cache_updated = self.contract.functions.base_cache_updated().call()
        self.base_virtual_price = self.contract.functions.base_virtual_price().call()
        self.base_pool = BasePool(self.contract.functions.base_pool().call())

    def _get_rates(self, values: list[int]) -> list[int]:
        return values[:-1] + [self.base_pool.virtual_price if self.timestamp > self.base_cache_updated + BASE_CACHE_EXPIRES else self.base_virtual_price]

    A_PREC = 100
    D_FLAG = 0
    Y_FLAG = 1
    P_FLAG = 0
