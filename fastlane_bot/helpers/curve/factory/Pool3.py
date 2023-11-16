from .Pool import Pool

class Pool3(Pool):
    abi = [
        {"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
        {"name":"admin_balances","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
        {"name":"offpeg_fee_multiplier","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
    ]

    def _sync(self):
        self.admin_balances = [self.contract.functions.admin_balances(n).call() for n in range(len(self.coins))]
        self.offpeg_fee_multiplier = self.contract.functions.offpeg_fee_multiplier().call()

    def _get_balances(self) -> list[int]:
        return [coin.pool_balance - admin_balance for coin, admin_balance in zip(self.coins, self.admin_balances)]

    def _get_fee_mul(self) -> int:
        return self.offpeg_fee_multiplier

    A_PREC = 100
    D_FLAG = 1
    Y_FLAG = 0
    P_FLAG = 1
