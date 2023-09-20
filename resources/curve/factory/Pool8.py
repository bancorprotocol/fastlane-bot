from .Pool import Pool
from .BaseCoin import BaseCoin

abi = [
    {"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    {"name":"balances","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    {"name":"underlying_coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"}
]

class Pool8(Pool):
    def __init__(self, address: str, coins: list[any]):
        super().__init__(address, abi)
        self.coins = [coins[n](self.contract.functions.coins(n).call()) for n in range(len(coins))]
        self.balances = [self.contract.functions.balances(n).call() for n in range(len(coins))]
        self.underlying_coins = [BaseCoin(self.contract.functions.underlying_coins(n).call()) for n in range(len(coins))]
        self.block_number = self.contract.w3.eth.get_block('latest')['number']

    def _get_factors(self, default: int) -> list[int]:
        return [coin.exchangeRateStored + coin.exchangeRateStored * coin.supplyRatePerBlock * (self.block_number - coin.accrualBlockNumber) // default for coin in self.coins]

    def _get_coins(self) -> list[any]:
        return self.underlying_coins

    A_PREC = 100
    D_FLAG = 0
    Y_FLAG = 1
    P_FLAG = 0
