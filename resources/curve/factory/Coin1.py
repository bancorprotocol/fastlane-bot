from .Coin import Coin
from .Host import Host

abi = [
    {"name":"balanceOf","outputs":[{"type":"uint256","name":""}],"inputs":[{"type":"address","name":""}],"stateMutability":"view","type":"function"}
]

class Coin1(Coin):
    def __init__(self, address: str, pool_address: str):
        super().__init__(address, abi)
        if self.is_eth():
            self.pool_balance = Host.web3.eth.get_balance(pool_address)
        else:
            self.pool_balance = self.contract.functions.balanceOf(pool_address).call()
