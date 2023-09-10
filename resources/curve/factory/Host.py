from web3 import Web3

class Host:
    def connect(url: str):
        Host.web3 = Web3(Web3.HTTPProvider(url))
