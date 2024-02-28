"""
This module contains the Wallet class, which is a dataclass that represents a wallet on the given network.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import json
import os
from datetime import datetime

import pandas as pd
import requests
from eth_typing import Address
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI


class Web3Manager:
    """
    This class is used to interact with the Carbon Controller contract on the given network.
    """

    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.w3.is_connected(), "Web3 not connected"

    def get_carbon_controller(self, address: Address) -> Contract:
        """
        Gets the Carbon Controller contract on the given network.
        """
        return self.w3.eth.contract(address=address, abi=CARBON_CONTROLLER_ABI)

    @staticmethod
    def get_carbon_controller_address(
        multichain_addresses_path: str, network: str
    ) -> str:
        """
        Gets the Carbon Controller contract address on the given network.
        """
        lookup_table = pd.read_csv(multichain_addresses_path)
        return (
            lookup_table.query("exchange_name=='carbon_v1'")
            .query(f"chain=='{network}'")
            .factory_address.values[0]
        )

    @staticmethod
    def create_new_testnet() -> tuple:
        """
        Creates a new testnet on Tenderly.
        """

        # Replace these variables with your actual data
        ACCOUNT_SLUG = os.environ["TENDERLY_USER"]
        PROJECT_SLUG = os.environ["TENDERLY_PROJECT"]
        ACCESS_KEY = os.environ["TENDERLY_ACCESS_KEY"]

        url = f"https://api.tenderly.co/api/v1/account/{ACCOUNT_SLUG}/project/{PROJECT_SLUG}/testnet/container"

        headers = {"Content-Type": "application/json", "X-Access-Key": ACCESS_KEY}

        data = {
            "slug": f"testing-api-endpoint-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "displayName": "Automated Test Env",
            "description": "",
            "visibility": "TEAM",
            "tags": {"purpose": "development"},
            "networkConfig": {
                "networkId": "1",
                "blockNumber": "latest",
                "baseFeePerGas": "1",
                "chainConfig": {"chainId": "1"},
            },
            "private": True,
            "syncState": False,
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        uri = f"{response.json()['container']['connectivityConfig']['endpoints'][0]['uri']}"
        from_block = int(response.json()["container"]["networkConfig"]["blockNumber"])

        return uri, from_block
