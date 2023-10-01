from .Coin import Coin

class Coin2(Coin):
    abi = [
        {"name":"exchangeRateCurrent","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
    ]

    def sync(self, _):
        self.exchangeRateCurrent = self.contract.functions.exchangeRateCurrent().call()
