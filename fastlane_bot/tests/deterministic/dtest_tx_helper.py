"""
This module contains the TxHelper class which is a utility class to scan the logs directory for successful transactions
and clean and extract the transaction data.

(c) Copyright Bprotocol foundation 2024.
All rights reserved.
Licensed under MIT License.
"""
import argparse
import glob
import json
import logging
import os
import time
from typing import Dict, List

from fastlane_bot.tests.deterministic import dtest_constants as constants


class TestTxHelper:
    """
    This is a utility class to scan the logs directory for successful transactions and clean and extract the
    transaction data.
    """
    @property
    def logs_path(self) -> str:
        """TODO TESTS: This should be read from dtest_constants"""
        return os.path.normpath("./logs_dtest/logs/*")

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
    def load_json_data(file_path: str) -> Dict:
        """Safely load JSON data from a file.

        Args:
            file_path (str): The path to the file.

        Returns:
            dict: The JSON data.
        """
        with open(file_path, "r") as file:
            return json.load(file)

    @staticmethod
    def read_transaction_files(log_folder: str) -> List:
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

    def tx_scanner(self, args: argparse.Namespace) -> List:
        """
        Scan for successful transactions in the most recent log folder.
        
        Args:
            args (argparse.Namespace): The command-line arguments.
            
        Returns:
            list: A list of successful transactions.
        """
        most_recent_log_folder = [
            f for f in glob.glob(self.logs_path) if os.path.isdir(f)
        ][-1]
        args.logger.debug(f"[dtest_tx_helper.tx_scanner] Accessing log folder {most_recent_log_folder}")

        pool_data_file = os.path.join(most_recent_log_folder, "latest_pool_data.json")
        if self.wait_for_file(pool_data_file, args.logger):
            pool_data = self.load_json_data(pool_data_file)
            args.logger.debug(f"len(pool_data): {len(pool_data)}")

        transactions = self.read_transaction_files(most_recent_log_folder)
        successful_txs = [tx for tx in transactions if '"tx_status": "succeeded",' in tx]
        args.logger.debug(f"Found {len(successful_txs)} successful transactions.")

        return successful_txs

    @staticmethod
    def clean_tx_data(tx_data: Dict) -> Dict:
        """
        This method takes a transaction data dictionary and removes the cid0 key from the trades. Note that the same dict object is modified in place.
        
        Args:
            tx_data (dict): The transaction data.
            
        Returns:
            dict: The cleaned transaction data.
        """
        if not tx_data:
            return tx_data

        # filter out the non-deterministic factors derieved from unique strategyids
        for trade in tx_data["trades"]:
            if trade["exchange"] in constants.CARBON_V1_FORKS and "cid0" in trade:
                del trade["cid0"]
        for trade in tx_data["route_struct"]:
            if "deadline" in trade:
                del trade['deadline']
            if trade["platformId"] == 6  and "customData" in trade:
                del trade["customData"]
        return tx_data

    @staticmethod
    def get_tx_data(strategy_id: int, txt_all_successful_txs: List) -> Dict:
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
            if hex(strategy_id).replace("0x","") in tx:
                return json.loads(
                    tx
                )['log_dict']

    @staticmethod
    def load_json_file(file_name: str, args: argparse.Namespace) -> Dict:
        """
        This method loads a json file and returns the data as a dictionary.
        
        Args:
            file_name (str): The name of the file.
            args (argparse.Namespace): The command-line arguments.
            
        Returns:
            dict: The data from the json file.
        """
        file_path = (
            os.path.normpath(f"{constants.TEST_DATA_DIR}/{file_name}")
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
    def log_txs(tx_list: List, args: argparse.Namespace):
        """
        This method logs the transactions in a list.
        
        Args:
            tx_list (list): A list of transactions.
            args (argparse.Namespace): The command-line arguments.
        """
        for i, tx in enumerate(tx_list):
            args.logger.debug(f"\nsuccessful_txs[{i}]: {tx}")

    def log_results(self, args: argparse.Namespace, actual_txs: List, expected_txs: Dict, test_strategy_txhashs: Dict) -> Dict:
        """
        Logs the results of the tests and returns a dictionary with the results.

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

        for test_id, strategy in test_strategy_txhashs.items():
            strategy_id = strategy.get("strategyid")

            # Failure case 1: strategyid missing in test_strategy_txhashs
            if not strategy_id:
                self.log_test_failure(test_id, "strategyid missing in test_strategy_txhashs", results_description)
                continue

            tx_data = self.clean_tx_data(self.get_tx_data(strategy_id, actual_txs))

            # Failure case 2: The test_id is not found in expected_txs
            if test_id not in expected_txs["test_data"]:
                self.log_test_failure(test_id, f"Test ID {test_id} not found in expected_txs", results_description, tx_data)
                all_tests_passed = False
                continue

            expected_test_data = expected_txs["test_data"][test_id]

            # Failure case 3: The tx_data does not match the expected_test_data
            if tx_data != expected_test_data:
                self.log_test_failure(test_id, "Data mismatch", results_description, tx_data, expected_test_data)
                all_tests_passed = False
                continue

            # Success case
            results_description[test_id] = {"msg": f"Test {test_id} PASSED"}

        self.log_final_result(args, all_tests_passed)
        return results_description

    @staticmethod
    def log_test_failure(test_id: int,
                         reason: str, results_description: Dict,
                         tx_data: Dict = None, expected_data: Dict = None):
        """
        Logs a test failure.

        Args:
            test_id (int): The test id.
            reason (str): The reason for the failure.
            results_description (dict): The dictionary with the results.
            tx_data (dict): The transaction data.
            expected_data (dict): The expected data.
        """
        result = {"msg": f"Test {test_id} FAILED", "reason": reason}
        if tx_data:
            result["tx_data"] = tx_data
        if expected_data:
            result["expected_data"] = expected_data
        results_description[test_id] = result

    @staticmethod
    def log_final_result(args: argparse.Namespace, all_tests_passed: bool):
        """
        Logs the final result of all tests.

        Args:
            args (argparse.Namespace): The command-line arguments.
            all_tests_passed (bool): Whether all tests passed.
        """
        if all_tests_passed:
            args.logger.info("ALL TESTS PASSED")
        else:
            args.logger.warning("SOME TESTS FAILED")

    def wait_for_txs(self, args: argparse.Namespace) -> Dict:
        """
        This method waits for the transactions to be executed and returns the test strategy txhashs.

        Args:
            args (argparse.Namespace): The command-line arguments.

        Returns:
            dict: The test strategy txhashs.
        """
        test_strategy_txhashs = self.load_json_file("test_strategy_txhashs.json", args)
        sleep_seconds = int(20 * len(test_strategy_txhashs.keys()) + 15)
        args.logger.debug(f"sleep_seconds: {sleep_seconds}")
        time.sleep(sleep_seconds)
        return test_strategy_txhashs
