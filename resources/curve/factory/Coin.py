from .Contract import Contract

abi = [
    {"name":"symbol","outputs":[{"type":"string","name":""}],"inputs":[],"stateMutability":"view","type":"function"},
    {"name":"decimals","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class Coin(Contract):
    def __init__(self, address: str, abi_ex: list[dict]):
        super().__init__(address, abi + abi_ex)
        if self.is_eth():
            self.symbol = 'ETH'
            self.decimals = 18
        else:
            self.symbol = self.contract.functions.symbol().call()
            self.decimals = self.contract.functions.decimals().call()
    def is_eth(self) -> bool:
        return self.contract.address.lower() == '0x'.ljust(42, 'e')
