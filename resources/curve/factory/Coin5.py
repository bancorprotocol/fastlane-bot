from .Coin import Coin

abi = [
]

class Coin5(Coin):
    def __init__(self, address: str):
        super().__init__(address, abi)
