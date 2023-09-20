from web3 import Web3

class Host:
    def connect(url: str):
        Host.web3 = Web3(Web3.HTTPProvider(url))
    def contract(address: str, abi: list[dict]) -> any:
        return Host.web3.eth.contract(address=address, abi=abi)
