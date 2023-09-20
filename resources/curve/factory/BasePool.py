from .Host import Host

abi = [
    {"name":"get_virtual_price","outputs":[{"type":"uint256","name":""}],"inputs":[],"stateMutability":"view","type":"function"}
]

class BasePool:
    def __init__(self, address: str):
        self.contract = Host.web3.eth.contract(address = address, abi = abi)
        self.virtual_price = self.contract.functions.get_virtual_price().call()
