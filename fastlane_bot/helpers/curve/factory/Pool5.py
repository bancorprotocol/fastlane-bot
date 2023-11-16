from .Pool import Pool

class Pool5(Pool):
    abi = [
        {"name":"coins","outputs":[{"type":"address","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"},
        {"name":"balances","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"uint256","name":""}],"stateMutability":"view","type":"function"}
    ]

    def _sync(self):
        self.balances = [self.contract.functions.balances(n).call() for n in range(len(self.coins))]

    A_PREC = 1
    D_FLAG = 0
    Y_FLAG = 1
    P_FLAG = 1
