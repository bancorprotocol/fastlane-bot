from .Contract import Contract

abi = [
    {"name":"decimals","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class BaseCoin(Contract):
    def __init__(self, address: str):
        super().__init__(address, abi)
        self.decimals = self.contract.functions.decimals().call()
