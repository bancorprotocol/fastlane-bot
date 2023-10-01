from .Coin import Coin

class Coin1(Coin):
    abi = [
        {"name":"balanceOf","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":""}],"stateMutability":"view","type":"function"}
    ]

    def sync(self, pool_address: str):
        if self.is_eth():
            self.pool_balance = self.contract.w3.eth.get_balance(pool_address)
        else:
            self.pool_balance = self.contract.functions.balanceOf(pool_address).call()
