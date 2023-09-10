from .Coin import Coin

abi = [
    {"name":"exchangeRateCurrent","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class Coin2(Coin):
    def __init__(self, address: str):
        super().__init__(address, abi)
        self.exchange_rate = self.contract.functions.exchangeRateCurrent().call()
