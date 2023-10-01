from .Coin import Coin

class Coin4(Coin):
    abi = [
        {"name":"exchangeRateStored","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
        {"name":"supplyRatePerBlock","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
        {"name":"accrualBlockNumber","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
    ]

    def sync(self, _):
        self.exchangeRateStored = self.contract.functions.exchangeRateStored().call()
        self.supplyRatePerBlock = self.contract.functions.supplyRatePerBlock().call()
        self.accrualBlockNumber = self.contract.functions.accrualBlockNumber().call()
