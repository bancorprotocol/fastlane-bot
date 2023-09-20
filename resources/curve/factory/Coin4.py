from .Coin import Coin

abi = [
    {"name":"exchangeRateStored","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"supplyRatePerBlock","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"accrualBlockNumber","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class Coin4(Coin):
    def __init__(self, address: str):
        super().__init__(address, abi)
        self.exchangeRateStored = self.contract.functions.exchangeRateStored().call()
        self.supplyRatePerBlock = self.contract.functions.supplyRatePerBlock().call()
        self.accrualBlockNumber = self.contract.functions.accrualBlockNumber().call()
