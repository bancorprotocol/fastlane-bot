from .Host import Host

abi = [
    {"name":"decimals","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class BaseCoin:
    def __init__(self, address: str):
        self.contract = Host.contract(address, abi)
        self.decimals = self.contract.functions.decimals().call()
