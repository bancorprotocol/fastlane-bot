from .Contract import Contract

abi = [
    {"name":"get_virtual_price","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class BasePool(Contract):
    def __init__(self, address: str):
        super().__init__(address, abi)
        self.virtual_price = self.contract.functions.get_virtual_price().call()
