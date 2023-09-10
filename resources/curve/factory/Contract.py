from .Host import Host

class Contract:
    def __init__(self, address: str, abi: list[dict]):
        self.contract = Host.web3.eth.contract(address=address, abi=abi)
