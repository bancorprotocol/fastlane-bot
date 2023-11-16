from .Pool import Pool

class Pool1(Pool):
    abi = [
        {"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
        {"name":"admin_balances","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"}
    ]

    def _sync(self):
        self.admin_balances = [self.contract.functions.admin_balances(n).call() for n in range(len(self.coins))]

    def _get_balances(self) -> list[int]:
        return [coin.pool_balance - admin_balance for coin, admin_balance in zip(self.coins, self.admin_balances)]

    A_PREC = 100
    D_FLAG = 0
    Y_FLAG = 1
    P_FLAG = 1
