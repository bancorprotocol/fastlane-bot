"""
A module to manage Carbon strategies.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import argparse
import glob
import json
import os
import time
from typing import Dict, List, Tuple

import pandas as pd
import requests
from datetime import datetime
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI
from fastlane_bot.tests.deterministic.dtest_constants import (
    DEFAULT_GAS,
    DEFAULT_GAS_PRICE,
    ETH_ADDRESS,
    TEST_DATA_DIR,
    TOKENS_MODIFICATIONS,
)
from fastlane_bot.tests.deterministic.dtest_cmd_line_args import TestCommandLineArgs
from fastlane_bot.tests.deterministic.dtest_strategy import TestStrategy


class TestManager:
    """
    A class to manage Web3 contracts and Carbon strategies.
    """

    def __init__(self, args: argparse.Namespace):
        """
        Initializes the TestManager.

        Args:
            args (argparse.Namespace): The command-line arguments.
        """
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
        self.args = args

    @property
    def logs_path(self) -> str:
        """TODO TESTS: This should be read from dtest_constants"""
        return os.path.normpath("./logs_dtest/logs/*")

    def get_carbon_controller(self, address: Address or str) -> Contract:
        """
        Gets the Carbon Controller contract on the given network.

        Args:
            address (Address or str): The address.

        Returns:
            Contract: The Carbon Controller contract.
        """
        return self.w3.eth.contract(address=address, abi=CARBON_CONTROLLER_ABI)

    @staticmethod
    def get_carbon_controller_address(
        multichain_addresses_path: str, network: str
    ) -> str:
        """
        Gets the Carbon Controller contract address on the given network.

        Args:
            multichain_addresses_path (str): The path to the multichain addresses file.
            network (str): The network.

        Returns:
            str: The Carbon Controller contract address.
        """
        lookup_table = pd.read_csv(multichain_addresses_path)
        return (
            lookup_table.query("exchange_name=='carbon_v1'")
            .query(f"chain=='{network}'")
            .factory_address.values[0]
        )

    @staticmethod
    def create_new_testnet() -> Tuple[str, int]:
        """
        Creates a new testnet on Tenderly.

        Returns:
            tuple: The URI and the block number.
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
    def process_order_data(log_args: Dict, order_key: str) -> Dict:
        """
        Transforms nested order data by appending a suffix to each key.

        Args:
            log_args (dict): The log arguments.
            order_key (str): The order key.

        Returns:
            dict: The processed order data.
        """
        if order_data := log_args.get(order_key):
            suffix = order_key[-1]  # Assumes order_key is either 'order0' or 'order1'
            return {f"{key}{suffix}": value for key, value in order_data.items()}
        return {}

    @staticmethod
    def print_state_changes(
        args: argparse.Namespace,
        all_carbon_strategies: List,
        deleted_strategies: List,
        remaining_carbon_strategies: List,
    ) -> None:
        """
        Prints the state changes of Carbon strategies.

        Args:
            args (argparse.Namespace): The command-line arguments.
            all_carbon_strategies (list): The all carbon strategies.
            deleted_strategies (list): The deleted strategies.
            remaining_carbon_strategies (list): The remaining carbon strategies.
        """
        args.logger.debug(
            f"{len(all_carbon_strategies)} Carbon strategies have been created"
        )
        args.logger.debug(
            f"{len(deleted_strategies)} Carbon strategies have been deleted"
        )
        args.logger.debug(
            f"{len(remaining_carbon_strategies)} Carbon strategies remain"
        )

    def get_generic_events(
        self, args: argparse.Namespace, event_name: str, from_block: int
    ) -> pd.DataFrame:
        """
        Fetches logs for a specified event from a smart contract.

        Args:
            args (argparse.Namespace): The command-line arguments.
            event_name (str): The event name.
            from_block (int): The block number.

        Returns:
            pd.DataFrame: The logs for the specified event.
        """
        args.logger.debug(
            f"Fetching logs for {event_name} event, from_block: {from_block}"
        )
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
            args.logger.debug(
                f"Error fetching logs for {event_name} event: {e}, returning empty df"
            )
            return pd.DataFrame({})

    def get_state_of_carbon_strategies(
        self, args: argparse.Namespace, from_block: int
    ) -> Tuple:
        """
        Fetches the state of Carbon strategies.

        Args:
            args (argparse.Namespace): The command-line arguments.
            from_block (int): The block number.

        Returns:
            tuple: The strategy created dataframe, the strategy deleted dataframe, and the remaining carbon strategies.
        """
        strategy_created_df = self.get_generic_events(
            args=args, event_name="StrategyCreated", from_block=from_block
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
            args=args, event_name="StrategyDeleted", from_block=from_block
        )
        deleted_strategies = (
            [] if strategy_deleted_df.empty else strategy_deleted_df["id"].to_list()
        )
        remaining_carbon_strategies = [
            x for x in all_carbon_strategies if x[0] not in deleted_strategies
        ]
        self.print_state_changes(
            args, all_carbon_strategies, deleted_strategies, remaining_carbon_strategies
        )
        return strategy_created_df, strategy_deleted_df, remaining_carbon_strategies

    def modify_storage(self, w3: Web3, address: str, slot: str, value: str):
        """Modify storage directly via Tenderly.

        Args:
            w3 (Web3): The Web3 instance.
            address (str): The address.
            slot (str): The slot.
            value (str): The value.
        """
        params = [address, slot, value]
        w3.provider.make_request(method="tenderly_setStorageAt", params=params)

    @staticmethod
    def set_balance_via_faucet(
        args: argparse.Namespace,
        w3: Web3,
        token_address: str,
        amount_wei: int,
        wallet: Address or ChecksumAddress,
        retry_num=0,
    ):
        """
        Set the balance of a wallet via a faucet.

        Args:
            args (argparse.Namespace): The command-line arguments.
            w3 (Web3): The Web3 instance.
            token_address (str): The token address.
            amount_wei (int): The amount in wei.
            wallet (Address or ChecksumAddress): The wallet address.
            retry_num (int): The number of retries.
        """
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
                args.logger.debug(f"Retrying faucet request for {token_address}")
                TestManager.set_balance_via_faucet(
                    args, w3, token_address, amount_wei, wallet, retry_num + 1
                )

        args.logger.debug(f"Reset Balance to {amount_wei}")

    def modify_token(
        self,
        args: argparse.Namespace,
        token_address: str,
        modifications: Dict,
        strategy_id: int,
        strategy_beneficiary: Address,
    ):
        """General function to modify token parameters and handle deletion.

        Args:
            args (argparse.Namespace): The command-line arguments.
            token_address (str): The token address.
            modifications (dict): The modifications to be made.
            strategy_id (int): The strategy id.
            strategy_beneficiary (Address): The strategy beneficiary.
        """

        # Modify the tax parameters
        for slot, value in modifications["before"].items():
            self.modify_storage(self.w3, token_address, slot, value)

        # Ensure there is sufficient funds for withdrawal
        self.set_balance_via_faucet(
            args,
            self.w3,
            token_address,
            modifications["balance"],
            self.carbon_controller.address,
        )

        self.delete_strategy(strategy_id, strategy_beneficiary)

        # Reset the tax parameters to their original state
        for slot, value in modifications["after"].items():
            self.modify_storage(self.w3, token_address, slot, value)

        # Empty out this token from CarbonController
        self.set_balance_via_faucet(
            args, self.w3, token_address, 0, self.carbon_controller.address
        )

    def modify_tokens_for_deletion(self, args: argparse.Namespace) -> None:
        """Custom modifications to tokens to allow their deletion from Carbon.

        Args:
            args (argparse.Namespace): The command-line arguments.
        """
        for token_name, details in TOKENS_MODIFICATIONS.items():
            args.logger.debug(f"Modifying {token_name} token..., details: {details}")
            self.modify_token(
                args,
                details["address"],
                details["modifications"],
                details["strategy_id"],
                details["strategy_beneficiary"],
            )
            args.logger.debug(f"Modification for {token_name} token completed.")

    def create_strategy(self, args: argparse.Namespace, strategy: TestStrategy) -> str:
        """
        Creates a Carbon strategy.

        Args:
            args (argparse.Namespace): The command-line arguments.
            strategy (TestStrategy): The test strategy.

        Returns:
            str: The transaction hash.
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
            args.logger.debug("Creation Failed")
            return None
        else:
            args.logger.debug("Successfully Created Strategy")
            return self.w3.to_hex(tx_receipt.transactionHash)

    def delete_strategy(self, strategy_id: int, wallet: Address) -> int:
        """
        Deletes a Carbon strategy.

        Args:
            strategy_id (int): The strategy id.
            wallet (Address): The wallet address.

        Returns:
            int: The transaction receipt status.
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

    def delete_all_carbon_strategies(
        self, args: argparse.Namespace, carbon_strategy_id_owner_list: List
    ) -> List:
        """
        Deletes all Carbon strategies.

        Args:
            args (argparse.Namespace): The command-line arguments.
            carbon_strategy_id_owner_list (list): The carbon strategy id owner list.

        Returns:
            list: The undeleted strategies.
        """
        self.modify_tokens_for_deletion(args)
        undeleted_strategies = []
        for strategy_id, owner in carbon_strategy_id_owner_list:
            args.logger.debug("Attempt 1")
            status = self.delete_strategy(strategy_id, owner)
            if status == 0:
                try:
                    strategy_info = self.carbon_controller.functions.strategy(
                        strategy_id
                    ).call()
                    current_owner = strategy_info[1]
                    try:
                        args.logger.debug("Attempt 2")
                        status = self.delete_strategy(strategy_id, current_owner)
                        if status == 0:
                            args.logger.debug(
                                f"Unable to delete strategy {strategy_id}"
                            )
                            undeleted_strategies += [strategy_id]
                    except Exception as e:
                        args.logger.debug(
                            f"Strategy {strategy_id} not found - already deleted {e}"
                        )
                except Exception as e:
                    args.logger.debug(
                        f"Strategy {strategy_id} not found - already deleted {e}"
                    )
            elif status == 1:
                args.logger.debug(f"Strategy {strategy_id} successfully deleted")
            else:
                args.logger.debug("Possible error")
        return undeleted_strategies

    @staticmethod
    def get_test_strategies(args: argparse.Namespace) -> Dict:
        """
        Gets test strategies from a JSON file.
        """
        test_strategies_path = os.path.normpath(
            f"{TEST_DATA_DIR}/test_strategies.json"
        )
        with open(test_strategies_path) as file:
            test_strategies = json.load(file)["test_strategies"]
            args.logger.debug(f"{len(test_strategies.keys())} test strategies imported")
        return test_strategies

    def append_strategy_ids(
        self, args: argparse.Namespace, test_strategy_txhashs: Dict, from_block: int
    ) -> Dict:
        """
        Appends the strategy ids to the test strategies.

        Args:
            args (argparse.Namespace): The command-line arguments.
            test_strategy_txhashs (dict): The test strategy txhashs.
            from_block (int): The block number.

        Returns:
            dict: The test strategy txhashs with the strategy ids.
        """
        args.logger.debug("\nAdd the strategy ids...")

        # Get the new state of the carbon strategies
        (
            strategy_created_df,
            strategy_deleted_df,
            remaining_carbon_strategies,
        ) = self.get_state_of_carbon_strategies(args, from_block)

        for i in test_strategy_txhashs:
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
    def write_strategy_txhashs_to_json(test_strategy_txhashs: Dict):
        """
        Writes the test strategy txhashs to a file.

        Args:
            test_strategy_txhashs (dict): The test strategy txhashs.
        """
        test_strategy_txhashs_path = os.path.normpath(
            f"{TEST_DATA_DIR}/test_strategy_txhashs.json"
        )
        with open(test_strategy_txhashs_path, "w") as f:
            json.dump(test_strategy_txhashs, f)
            f.close()

    @staticmethod
    def get_strats_created_from_block(args: argparse.Namespace, w3: Web3) -> int:
        """
        Gets the block number from which new strategies were created.

        Args:
            args (argparse.Namespace): The command-line arguments.

        Returns:
            int: The block number.
        """
        strats_created_from_block = w3.eth.get_block_number()
        args.logger.debug(f"strats_created_from_block: {strats_created_from_block}")
        return strats_created_from_block

    def approve_and_create_strategies(
        self, args: argparse.Namespace, test_strategies: Dict, from_block: int
    ) -> Dict:
        """
        Approves and creates test strategies.

        Args:
            args (argparse.Namespace): The command-line arguments.
            test_strategies (dict): The test strategies.
            from_block (int): The block number.

        Returns:
            dict: All the relevant test strategies
        """
        test_strategy_txhashs: Dict[TestStrategy] or Dict = {}
        for i, (key, arg) in enumerate(test_strategies.items()):
            arg["w3"] = self.w3
            test_strategy = TestStrategy(**arg)
            test_strategy.get_token_approval(
                args=args, token_id=0, approval_address=self.carbon_controller.address
            )
            test_strategy.get_token_approval(
                args=args, token_id=1, approval_address=self.carbon_controller.address
            )
            tx_hash = self.create_strategy(args, test_strategy)
            test_strategy_txhashs[str(i + 1)] = {"txhash": tx_hash}

        test_strategy_txhashs = self.append_strategy_ids(
            args, test_strategy_txhashs, from_block
        )
        return test_strategy_txhashs

    @staticmethod
    def overwrite_command_line_args(args: argparse.Namespace) -> TestCommandLineArgs:
        """
        Overwrites the command-line arguments with the default main args.

        Args:
            args (argparse.Namespace): The command-line arguments.

        Returns:
            TestCommandLineArgs: The default main args.
        """
        # Get the default main args
        default_main_args = TestCommandLineArgs()
        default_main_args.blockchain = args.network
        default_main_args.arb_mode = args.arb_mode
        default_main_args.timeout = args.timeout
        default_main_args.rpc_url = args.rpc_url
        return default_main_args

    def get_most_recent_pool_data_path(self, args: argparse.Namespace) -> str:
        """
        Gets the path to the most recent pool data file.

        Args:
            args (argparse.Namespace): The command-line arguments.

        Returns:
            str: The path to the most recent pool data file.
        """

        # Use glob to list all directories
        most_recent_log_folder = [
            f for f in glob.glob(self.logs_path) if os.path.isdir(f)
        ][-1]
        args.logger.debug(f"[dtest_manager.get_most_recent_pool_data_path] Accessing log folder {most_recent_log_folder}")
        return os.path.join(most_recent_log_folder, "latest_pool_data.json")

    def delete_old_logs(self, args: argparse.Namespace):
        """
        Deletes all files and directories in the logs directory.

        Args:
            args (argparse.Namespace): The command-line arguments.
        """
        logs = [f for f in glob.glob(self.logs_path) if os.path.isdir(f)]
        for log in logs:
            for root, dirs, files in os.walk(log, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(log)
        args.logger.debug("Deleted old logs")
