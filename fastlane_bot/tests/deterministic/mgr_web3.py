"""
This module contains the Wallet class, which is a dataclass that represents a wallet on the given network.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import pandas as pd
from eth_typing import Address
from web3 import Web3

from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI


class Web3Manager:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.w3.is_connected(), "Web3 not connected"

    def get_carbon_controller(self, address: Address):
        return self.w3.eth.contract(address=address, abi=CARBON_CONTROLLER_ABI)

    @staticmethod
    def get_carbon_controller_address(multichain_addresses_path: str, network: str):
        # Initialize the Carbon Controller contract
        lookup_table = pd.read_csv(multichain_addresses_path)
        return (
            lookup_table.query("exchange_name=='carbon_v1'")
            .query(f"chain=='{network}'")
            .factory_address.values[0]
        )
