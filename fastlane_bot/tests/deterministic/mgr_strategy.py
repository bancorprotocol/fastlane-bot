"""
A module to manage Carbon strategies.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import json
import os

import pandas as pd
from eth_typing import Address
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.tests.deterministic.constants import (
    DEFAULT_GAS,
    DEFAULT_GAS_PRICE,
    TEST_FILE_DATA_DIR,
)
from fastlane_bot.tests.deterministic.test_strategy import TestStrategy


class StrategyManager:
    """
    A class to manage Carbon strategies.

    Attributes:
        w3 (Web3): The Web3 instance.
        carbon_controller (Contract): The CarbonController contract instance.
    """

    def __init__(self, w3: Web3, carbon_controller: Contract):
        self.w3 = w3
        self.carbon_controller = carbon_controller

    @staticmethod
    def process_order_data(log_args: dict, order_key: str) -> dict:
        """Transforms nested order data by appending a suffix to each key.

        Args:
            log_args (dict): The log arguments.
            order_key (str): The key to process.

        Returns:
            dict: The processed order data.
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

        Args:
            all_carbon_strategies (list): The list of all Carbon strategies.
            deleted_strategies (list): The list of deleted Carbon strategies.
            remaining_carbon_strategies (list): The list of remaining Carbon strategies.
        """
        print(f"{len(all_carbon_strategies)} Carbon strategies have been created")
        print(f"{len(deleted_strategies)} Carbon strategies have been deleted")
        print(f"{len(remaining_carbon_strategies)} Carbon strategies remain")

    def get_generic_events(self, event_name: str, from_block: int) -> pd.DataFrame:
        """
        Fetches logs for a specified event from a smart contract.

        Args:
            event_name (str): The name of the event.
            from_block (int): The block number to start fetching logs from.

        Returns:
            pandas.DataFrame: A DataFrame containing the logs of the specified event.
        """
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
            df.sort_values(by="block_number") if "block_number" in df.columns else df
        ).reset_index(drop=True)

    def get_state_of_carbon_strategies(self, from_block: int) -> tuple:
        """
        Fetches the state of Carbon strategies.

        Args:
            from_block (int): The block number to start fetching logs from.

        Returns: tuple: A tuple containing the DataFrames of the 'StrategyCreated' and 'StrategyDeleted' events,
        and the list of remaining Carbon strategies.
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

    def modify_tokens_for_deletion(self) -> None:
        """
        Modifies tokens for deletion.
        """
        pass

    def create_strategy(self, strategy: TestStrategy) -> str:
        print("Creating Strategy...")
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
        print("Deleting Strategy...")
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
        print("Deleting strategies...")
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
    def get_test_strategies():
        test_strategies_path = os.path.normpath(
            f"{TEST_FILE_DATA_DIR}/test_strategies.json"
        )
        with open(test_strategies_path) as file:
            test_strategies = json.load(file)["test_strategies"]
            print(f"{len(test_strategies.keys())} test strategies imported")
        return test_strategies
