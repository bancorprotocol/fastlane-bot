"""
A module to manage Carbon strategies.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import glob
import json
import os
import time
from typing import Dict

import pandas as pd
import requests
from black import datetime
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI
from fastlane_bot.tests.deterministic.test_constants import (
    DEFAULT_GAS,
    DEFAULT_GAS_PRICE,
    ETH_ADDRESS, TEST_FILE_DATA_DIR,
    TOKENS_MODIFICATIONS,
    TestCommandLineArgs,
)
from fastlane_bot.tests.deterministic.test_pool import TestPool
from fastlane_bot.tests.deterministic.test_strategy import TestStrategy


class TestManager:
    """
    A class to manage Web3 contracts and Carbon strategies.
    """

    def __init__(self, args):

        self.w3 = Web3(Web3.HTTPProvider(args.rpc_url, {"timeout": 60}))
        assert self.w3.is_connected(), "Web3 connection failed"

        multichain_addresses_path = os.path.normpath(
            "fastlane_bot/data/multichain_addresses.csv"
        )

        # Get the Carbon Controller Address for the network
        carbon_controller_address = self.get_carbon_controller_address(
            multichain_addresses_path=multichain_addresses_path, network=args.network
        )

        # Initialize the Carbon Controller contract
        carbon_controller = self.get_carbon_controller(
            address=carbon_controller_address
        )

        self.carbon_controller = carbon_controller

    def get_carbon_controller(self, address: Address or str) -> Contract:
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

    @staticmethod
    def process_order_data(log_args: dict, order_key: str) -> dict:
        """
        Transforms nested order data by appending a suffix to each key.
        """
        if order_data := log_args.get(order_key):
            suffix = order_key[-1]  # Assumes order_key is either 'order0' or 'order1'
            return {f"{key}{suffix}": value for key, value in order_data.items()}
        return {}

    @staticmethod
    def print_state_changes(
        all_carbon_strategies: list,
        deleted_strategies: list,
        remaining_carbon_strategies: list,
    ) -> None:
        """
        Prints the state changes of Carbon strategies.
        """
        print(f"{len(all_carbon_strategies)} Carbon strategies have been created")
        print(f"{len(deleted_strategies)} Carbon strategies have been deleted")
        print(f"{len(remaining_carbon_strategies)} Carbon strategies remain")

    def get_generic_events(self, event_name: str, from_block: int) -> pd.DataFrame:
        """
        Fetches logs for a specified event from a smart contract.
        """
        print(f"Fetching logs for {event_name} event, from_block: {from_block}")
        try:
            log_list = getattr(self.carbon_controller.events, event_name).get_logs(
                fromBlock=from_block
            )
            data = []
            for log in log_list:
                log_data = {
                    "block_number": log["blockNumber"],
                    "transaction_hash": self.w3.to_hex(log["transactionHash"]),
                    **log["args"],
                }

                # Process and update log_data for 'order0' and 'order1', if present
                for order_key in ["order0", "order1"]:
                    if order_data := self.process_order_data(log["args"], order_key):
                        log_data.update(order_data)
                        del log_data[order_key]

                data.append(log_data)

            df = pd.DataFrame(data)
            return (
                df.sort_values(by="block_number")
                if "block_number" in df.columns
                else df
            ).reset_index(drop=True)
        except Exception as e:
            print(
                f"Error fetching logs for {event_name} event: {e}, returning empty df"
            )
            return pd.DataFrame({})

    def get_state_of_carbon_strategies(self, from_block: int) -> tuple:
        """
        Fetches the state of Carbon strategies.
        """
        strategy_created_df = self.get_generic_events(
            event_name="StrategyCreated", from_block=from_block
        )
        all_carbon_strategies = (
            []
            if strategy_created_df.empty
            else [
                (strategy_created_df["id"][i], strategy_created_df["owner"][i])
                for i in strategy_created_df.index
            ]
        )
        strategy_deleted_df = self.get_generic_events(
            event_name="StrategyDeleted", from_block=from_block
        )
        deleted_strategies = (
            [] if strategy_deleted_df.empty else strategy_deleted_df["id"].to_list()
        )
        remaining_carbon_strategies = [
            x for x in all_carbon_strategies if x[0] not in deleted_strategies
        ]

        # Print state changes
        self.print_state_changes(
            all_carbon_strategies, deleted_strategies, remaining_carbon_strategies
        )

        # Return state changes
        return strategy_created_df, strategy_deleted_df, remaining_carbon_strategies

    def modify_storage(self, w3: Web3, address: str, slot: str, value: str) -> None:
        """Modify storage directly via Tenderly."""
        params = [address, slot, value]
        w3.provider.make_request(method="tenderly_setStorageAt", params=params)

    @staticmethod
    def set_balance_via_faucet(
        w3: Web3,
        token_address: str,
        amount_wei: int,
        wallet: Address or ChecksumAddress,
        retry_num=0,
    ) -> None:
        token_address = w3.to_checksum_address(token_address)
        wallet = w3.to_checksum_address(wallet)
        if token_address in {ETH_ADDRESS}:
            method = "tenderly_setBalance"
            params = [[wallet], w3.to_hex(amount_wei)]
        else:
            method = "tenderly_setErc20Balance"
            params = [token_address, wallet, w3.to_hex(amount_wei)]

        try:
            w3.provider.make_request(method=method, params=params)
        except requests.exceptions.HTTPError:
            time.sleep(1)
            if retry_num < 3:
                print(f"Retrying faucet request for {token_address}")
                TestManager.set_balance_via_faucet(w3, token_address, amount_wei, wallet, retry_num + 1)

        print(f"Reset Balance to {amount_wei}")

    def modify_token(
        self,
        token_address: str,
        modifications: dict,
        strategy_id: int,
        strategy_beneficiary: Address,
    ) -> None:
        """General function to modify token parameters and handle deletion."""

        print(f"Start 1")
        # Modify the tax parameters
        for slot, value in modifications["before"].items():
            self.modify_storage(self.w3, token_address, slot, value)

        print(f"Start 2")
        # Ensure there is sufficient funds for withdrawal
        self.set_balance_via_faucet(
            self.w3,
            token_address,
            modifications["balance"],
            self.carbon_controller.address,
        )

        print(f"Start 3")
        self.delete_strategy(strategy_id, strategy_beneficiary)

        print(f"Start 4")
        # Reset the tax parameters to their original state
        for slot, value in modifications["after"].items():
            self.modify_storage(self.w3, token_address, slot, value)

        print(f"Start 5")
        # Empty out this token from CarbonController
        self.set_balance_via_faucet(
            self.w3, token_address, 0, self.carbon_controller.address
        )

    def modify_tokens_for_deletion(self) -> None:
        """Custom modifications to tokens to allow their deletion from Carbon."""
        for token_name, details in TOKENS_MODIFICATIONS.items():
            print(f"Modifying {token_name} token..., details: {details}")
            self.modify_token(
                details["address"],
                details["modifications"],
                details["strategy_id"],
                details["strategy_beneficiary"],
            )
            print(f"Modification for {token_name} token completed.")

    def create_strategy(self, strategy: TestStrategy) -> str:
        """
        Creates a Carbon strategy.
        """
        tx_params = {
            "from": strategy.wallet.address,
            "nonce": strategy.wallet.nonce,
            "gasPrice": DEFAULT_GAS_PRICE,
            "gas": DEFAULT_GAS,
        }
        if strategy.value:
            tx_params["value"] = strategy.value

        tx_hash = self.carbon_controller.functions.createStrategy(
            strategy.token0.address,
            strategy.token1.address,
            (
                [strategy.y0, strategy.z0, strategy.A0, strategy.B0],
                [strategy.y1, strategy.z1, strategy.A1, strategy.B1],
            ),
        ).transact(tx_params)

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status != 1:
            print("Creation Failed")
            return None
        else:
            print("Successfully Created Strategy")
            return self.w3.to_hex(tx_receipt.transactionHash)

    def delete_strategy(self, strategy_id: int, wallet: Address) -> int:
        """
        Deletes a Carbon strategy.
        """
        nonce = self.w3.eth.get_transaction_count(wallet)
        tx_params = {
            "from": wallet,
            "nonce": nonce,
            "gasPrice": DEFAULT_GAS_PRICE,
            "gas": DEFAULT_GAS,
        }
        tx_hash = self.carbon_controller.functions.deleteStrategy(strategy_id).transact(
            tx_params
        )

        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt.status

    def delete_all_carbon_strategies(self, carbon_strategy_id_owner_list: list) -> list:
        """
        Deletes all Carbon strategies.
        """
        self.modify_tokens_for_deletion()
        undeleted_strategies = []
        for strategy_id, owner in carbon_strategy_id_owner_list:
            print("Attempt 1")
            status = self.delete_strategy(strategy_id, owner)
            if status == 0:
                try:
                    strategy_info = self.carbon_controller.functions.strategy(
                        strategy_id
                    ).call()
                    current_owner = strategy_info[1]
                    try:
                        print("Attempt 2")
                        status = self.delete_strategy(strategy_id, current_owner)
                        if status == 0:
                            print(f"Unable to delete strategy {strategy_id}")
                            undeleted_strategies += [strategy_id]
                    except Exception as e:
                        print(f"Strategy {strategy_id} not found - already deleted {e}")
                except Exception as e:
                    print(f"Strategy {strategy_id} not found - already deleted {e}")
            elif status == 1:
                print(f"Strategy {strategy_id} successfully deleted")
            else:
                print("Possible error")
        return undeleted_strategies

    @staticmethod
    def get_test_strategies() -> dict:
        """
        Gets test strategies from a JSON file.
        """
        test_strategies_path = os.path.normpath(
            f"{TEST_FILE_DATA_DIR}/test_strategies.json"
        )
        with open(test_strategies_path) as file:
            test_strategies = json.load(file)["test_strategies"]
            print(f"{len(test_strategies.keys())} test strategies imported")
        return test_strategies

    def append_strategy_ids(self, args, test_strategy_txhashs, from_block) -> dict:
        args.logger.debug("\nAdd the strategy ids...")

        # Get the new state of the carbon strategies
        (
            strategy_created_df,
            strategy_deleted_df,
            remaining_carbon_strategies,
        ) = self.get_state_of_carbon_strategies(from_block)

        for i in test_strategy_txhashs.keys():
            try:
                test_strategy_txhashs[i]["strategyid"] = strategy_created_df[
                    strategy_created_df["transaction_hash"]
                    == test_strategy_txhashs[i]["txhash"]
                ].id.values[0]
                args.logger.debug(f"Added the strategy ids: {i}")
            except Exception as e:
                args.logger.debug(f"Add the strategy ids Error: {i}, {e}")
        return test_strategy_txhashs

    @staticmethod
    def write_strategy_txhashs_to_json(test_strategy_txhashs):
        # Write the test strategy txhashs to a file
        test_strategy_txhashs_path = os.path.normpath(
            f"{TEST_FILE_DATA_DIR}/test_strategy_txhashs.json"
        )
        with open(test_strategy_txhashs_path, "w") as f:
            json.dump(test_strategy_txhashs, f)
            f.close()

    @staticmethod
    def get_strats_created_from_block(args, w3):
        # Mark the block that new strats were created
        strats_created_from_block = w3.eth.get_block_number()
        args.logger.debug(f"strats_created_from_block: {strats_created_from_block}")
        return strats_created_from_block

    def approve_and_create_strategies(self, args, test_strategies, from_block):

        # populate a dictionary with all the relevant test strategies
        test_strategy_txhashs: Dict[TestStrategy] or Dict = {}
        for i, (key, arg) in enumerate(test_strategies.items()):
            arg["w3"] = self.w3
            test_strategy = TestStrategy(**arg)
            test_strategy.get_token_approval(
                token_id=0, approval_address=self.carbon_controller.address
            )
            test_strategy.get_token_approval(
                token_id=1, approval_address=self.carbon_controller.address
            )
            tx_hash = self.create_strategy(test_strategy)
            test_strategy_txhashs[str(i + 1)] = {"txhash": tx_hash}

        test_strategy_txhashs = self.append_strategy_ids(args, test_strategy_txhashs, from_block)
        return test_strategy_txhashs

    @staticmethod
    def overwrite_command_line_args(args):
        # Get the default main args
        default_main_args = TestCommandLineArgs()
        default_main_args.blockchain = args.network
        default_main_args.arb_mode = args.arb_mode
        default_main_args.timeout = args.timeout
        default_main_args.rpc_url = args.rpc_url
        return default_main_args
    
    @staticmethod
    def get_most_recent_pool_data_path(args):

        # Set the path to the logs directory relative to your notebook's location
        path_to_logs = "./logs/*"
        # Use glob to list all directories
        most_recent_log_folder = [
            f for f in glob.glob(path_to_logs) if os.path.isdir(f)
        ][-1]
        args.logger.debug(f"Accessing log folder {most_recent_log_folder}")
        return os.path.join(most_recent_log_folder, "latest_pool_data.json")


