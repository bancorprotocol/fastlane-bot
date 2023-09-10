from .Pool import Pool

abi = [
    {"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    {"name":"admin_balances","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
    {"name":"offpeg_fee_multiplier","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class Pool3(Pool):
    def __init__(self, address: str, coins: list[any]):
        super().__init__(address, abi)
        self.coins = [coins[n](self.contract.functions.coins(n).call(), address) for n in range(len(coins))]
        self.admin_balances = [self.contract.functions.admin_balances(n).call() for n in range(len(coins))]
        self.offpeg_fee_multiplier = self.contract.functions.offpeg_fee_multiplier().call()

    def _get_balances(self) -> list[int]:
        return [coin.pool_balance - admin_balance for coin, admin_balance in zip(self.coins, self.admin_balances)]

    def _get_fee_mul(self) -> int:
        return self.offpeg_fee_multiplier

    A_PREC = 100
    D_FLAG = 1
    Y_FLAG = 0
    P_FLAG = 1
