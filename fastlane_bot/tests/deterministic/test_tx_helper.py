"""
This module contains the TxHelper class which is a utility class to scan the logs directory for successful transactions
and clean and extract the transaction data.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import argparse
import glob
import json
import logging
import os
import time

from fastlane_bot.tests.deterministic.test_constants import (
    FILE_DATA_DIR,
    TEST_FILE_DATA_DIR,
)


class TestTxHelper:
    """
    This is a utility class to scan the logs directory for successful transactions and clean and extract the
    transaction data.
    """

    @staticmethod
    def find_most_recent_log_folder(logs_path="./logs/*") -> str:
        """Find the most recent log folder.

        Args:
            logs_path (str): The path to the logs directory. Defaults to "./logs/*".

        Returns:
            str: The most recent log folder.

        """
        log_folders = [f for f in glob.glob(logs_path) if os.path.isdir(f)]
        return max(log_folders, key=os.path.getmtime)

    @staticmethod
    def wait_for_file(file_path: str, logger: logging.Logger, timeout: int = 120, check_interval: int = 10) -> bool:
        """Wait for a specific file to exist, with a timeout.

        Args:
            file_path (str): The path to the file.
            logger (logging.Logger): The logger.
            timeout (int): The timeout in seconds. Defaults to 120.
            check_interval (int): The check interval in seconds. Defaults to 10.

        """
        start_time = time.time()
        while not os.path.exists(file_path):
            if time.time() - start_time > timeout:
                logger.debug("Timeout waiting for file.")
                return False
            logger.debug("File not found, waiting.")
            time.sleep(check_interval)
        logger.debug("File found.")
        return True

    @staticmethod
    def load_json_data(file_path: str) -> dict:
        """Safely load JSON data from a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            dict: The JSON data.
        """
        with open(file_path, "r") as file:
            return json.load(file)

    @staticmethod
    def read_transaction_files(log_folder: str) -> list:
        """Read all transaction files in a folder and return their content.
        
        Args:
            log_folder (str): The path to the log folder.
            
        Returns:
            list: A list of transaction data.
        """
        tx_files = glob.glob(os.path.join(log_folder, "*.txt"))
        transactions = []
        for tx_file in tx_files:
            with open(tx_file, "r") as file:
                transactions.append(file.read())
        return transactions

    def tx_scanner(self, args: argparse.Namespace) -> list:
        """
        Scan for successful transactions in the most recent log folder.
        
        Args:
            args (argparse.Namespace): The command-line arguments.
            
        Returns:
            list: A list of successful transactions.
        """
        most_recent_log_folder = self.find_most_recent_log_folder()
        args.logger.debug(f"Accessing log folder {most_recent_log_folder}")

        pool_data_file = os.path.join(most_recent_log_folder, "latest_pool_data.json")
        if self.wait_for_file(pool_data_file, args.logger):
            pool_data = self.load_json_data(pool_data_file)
            args.logger.debug(f"len(pool_data): {len(pool_data)}")

        transactions = self.read_transaction_files(most_recent_log_folder)
        successful_txs = [tx for tx in transactions if "'status': 1" in tx]
        args.logger.debug(f"Found {len(successful_txs)} successful transactions.")

        return successful_txs

    @staticmethod
    def clean_tx_data(tx_data: dict) -> dict:
        """
        This method takes a transaction data dictionary and removes the cid0 key from the trades.
        
        Args:
            tx_data (dict): The transaction data.
            
        Returns:
            dict: The cleaned transaction data.
        """
        if not tx_data:
            return tx_data

        for trade in tx_data["trades"]:
            if trade["exchange"] == "carbon_v1" and "cid0" in trade:
                del trade["cid0"]
        return tx_data

    @staticmethod
    def get_tx_data(strategy_id: int, txt_all_successful_txs: list) -> dict:
        """
        This method takes a list of successful transactions and a strategy_id and returns the transaction data for the
        given strategy_id.
        
        Args:
            strategy_id (int): The strategy id.
            txt_all_successful_txs (list): A list of successful transactions.
            
        Returns:
            dict: The transaction data for the given strategy_id.
        """
        for tx in txt_all_successful_txs:
            if str(strategy_id) in tx:
                return json.loads(
                    tx.split(
                        """

"""
                    )[-1]
                )

    @staticmethod
    def load_json_file(file_name: str, args: argparse.Namespace) -> dict:
        """
        This method loads a json file and returns the data as a dictionary.
        
        Args:
            file_name (str): The name of the file.
            args (argparse.Namespace): The command-line arguments.
            
        Returns:
            dict: The data from the json file.
        """
        file_path = (
            os.path.normpath(f"{TEST_FILE_DATA_DIR}/{file_name}")
            if "/" not in file_name
            else os.path.normpath(file_name)
        )

        try:
            with open(file_path) as f:
                data = json.load(f)
            args.logger.debug(f"len({file_name})={len(data)}")
        except FileNotFoundError:
            data = {}
        return data

    @staticmethod
    def log_txs(tx_list: list, args: argparse.Namespace):
        """
        This method logs the transactions in a list.
        
        Args:
            tx_list (list): A list of transactions.
            args (argparse.Namespace): The command-line arguments.
        """
        for i, tx in enumerate(tx_list):
            args.logger.debug(f"\nsuccessful_txs[{i}]: {tx}")

    def log_results(self, args: argparse.Namespace, actual_txs: list, expected_txs: dict,
                    test_strategy_txhashs: dict) -> dict:
        """
        This method logs the results of the tests and returns a dictionary with the results.

        Args:
            args (argparse.Namespace): The command-line arguments.
            actual_txs (list): A list of actual transactions.
            expected_txs (dict): A dictionary of expected transactions.
            test_strategy_txhashs (dict): A dictionary of test strategy txhashs.

        Returns:
            dict: A dictionary with the results of the tests.
        """
        results_description = {}
        all_tests_passed = True

        # Loop over the created test strategies and verify test data
        for i in test_strategy_txhashs:
            if "strategyid" not in test_strategy_txhashs[str(i)]:
                results_description[i] = {
                    "msg": f"Test {i} FAILED",
                    "tx_data": "strategyid not in test_strategy_txhashs",
                }
                continue

            search_id = test_strategy_txhashs[str(i)]["strategyid"]
            tx_data = self.clean_tx_data(self.get_tx_data(search_id, actual_txs))

            args.logger.debug(f"fetched expected_txs: {expected_txs['test_data'].keys()}")

            if str(i) not in expected_txs["test_data"]:
                results_description[i] = {
                    "msg": f"Test {i} FAILED",
                    "tx_data": tx_data,
                    "test_data": f"{i} not in expected_txs: {expected_txs}",
                }
                all_tests_passed = False
                continue

            test_data = expected_txs["test_data"][str(i)]
            if tx_data == test_data:
                results_description[str(i)] = {"msg": f"Test {i} PASSED"}
            else:
                results_description[str(i)] = {
                    "msg": f"Test {i} FAILED",
                    "tx_data": tx_data,
                    "test_data": test_data,
                }
                all_tests_passed = False

        if not all_tests_passed:
            args.logger.warning("SOME TESTS FAILED")
        else:
            args.logger.info("ALL TESTS PASSED")

        return results_description

    def wait_for_txs(self, args: argparse.Namespace) -> dict:
        """
        This method waits for the transactions to be executed and returns the test strategy txhashs.

        Args:
            args (argparse.Namespace): The command-line arguments.

        Returns:
            dict: The test strategy txhashs.
        """
        test_strategy_txhashs = self.load_json_file("test_strategy_txhashs.json", args)
        sleep_seconds = int(35 * len(test_strategy_txhashs.keys()) + 15)
        args.logger.debug(f"sleep_seconds: {sleep_seconds}")
        time.sleep(sleep_seconds)
        return test_strategy_txhashs
