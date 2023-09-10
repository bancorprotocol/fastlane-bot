from .Coin import Coin

abi = [
    {"name":"getPricePerFullShare","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class Coin3(Coin):
    def __init__(self, address: str):
        super().__init__(address, abi)
        self.share_price = self.contract.functions.getPricePerFullShare().call()
