from .Coin import Coin

class Coin3(Coin):
    abi = [
        {"name":"getPricePerFullShare","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
    ]

    def _sync(self, _):
        self.pricePerFullShare = self.contract.functions.getPricePerFullShare().call()
