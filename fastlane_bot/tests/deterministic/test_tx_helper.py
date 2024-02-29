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
    def read_transaction_files(log_folder):
        """Read all transaction files in a folder and return their content."""
        tx_files = glob.glob(os.path.join(log_folder, "*.txt"))
        transactions = []
        for tx_file in tx_files:
            with open(tx_file, "r") as file:
                transactions.append(file.read())
        return transactions

    def tx_scanner(self, args) -> list:
        """
        Scan for successful transactions in the most recent log folder.
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

    # @staticmethod
    # def tx_scanner(args) -> list:
    #     """
    #     This method scans the logs directory for successful transactions and returns a list of the successful
    #     transactions.
    #     """
    #     # Set the path to the logs directory relative to your notebook's location
    #     path_to_logs = "./logs/*"
    #
    #     # Use glob to list all directories
    #     most_recent_log_folder = [
    #         f for f in glob.glob(path_to_logs) if os.path.isdir(f)
    #     ][-1]
    #     args.logger.debug(f"Accessing log folder {most_recent_log_folder}")
    #
    #     most_recent_pool_data = os.path.join(
    #         most_recent_log_folder, "latest_pool_data.json"
    #     )
    #
    #     args.logger.debug("Looking for pool data file...")
    #     while True:
    #         if os.path.exists(most_recent_pool_data):
    #             args.logger.debug("File found.")
    #             break
    #         else:
    #             args.logger.debug("File not found, waiting 10 seconds.")
    #             time.sleep(10)
    #
    #     with open(most_recent_pool_data) as f:
    #         pool_data = json.load(f)
    #         args.logger.debug(f"len(pool_data): {len(pool_data)}")
    #
    #     all_successful_txs = glob.glob(os.path.join(most_recent_log_folder, "*.txt"))
    #
    #     # Read the successful_txs in as strings
    #     txt_all_successful_txs = []
    #     for successful_tx in all_successful_txs:
    #         with open(successful_tx, "r") as file:
    #             j = file.read()
    #             txt_all_successful_txs += [(j)]
    #
    #     # Successful transactions on Tenderly are marked by status=1
    #     successful_txs = [tx for tx in txt_all_successful_txs if "'status': 1" in tx]
    #     args.logger.debug(
    #         f"len(actually_txt_all_successful_txs): {len(successful_txs)}"
    #     )
    #     return successful_txs

    @staticmethod
    def clean_tx_data(tx_data: dict) -> dict:
        """
        This method takes a transaction data dictionary and removes the cid0 key from the trades.
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
    def log_txs(tx_list, args):
        for i, tx in enumerate(tx_list):
            args.logger.debug(f"\nsuccessful_txs[{i}]: {tx}")

    def log_results(self, args, actual_txs, expected_txs, test_strategy_txhashs):
        results_description = {}
        all_tests_passed = True

        # Loop over the created test strategies and verify test data
        for i in test_strategy_txhashs.keys():
            if "strategyid" not in test_strategy_txhashs[str(i)]:
                results_description[i] = {
                    "msg": f"Test {i} FAILED",
                    "tx_data": "strategyid not in test_strategy_txhashs",
                }
                continue

            search_id = test_strategy_txhashs[str(i)]["strategyid"]
            tx_data = self.clean_tx_data(self.get_tx_data(search_id, actual_txs))

            print(f"fetched expected_txs: {expected_txs['test_data'].keys()}")

            if str(i) not in expected_txs["test_data"]:
                results_description[i] = {
                    "msg": f"Test {i} FAILED",
                    "tx_data": tx_data,
                    "test_data": f"{i} not in expected_txs: {expected_txs}",
                }
                all_tests_passed = False
                continue

            test_data = expected_txs["test_data"][str(i)]
            # for td in expected_txs:
            #     test_data = expected_txs[td.keys()[0]]
            #     if tx_data == test_data:
            #         break

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

    #
    # def check_test_result(self, i, strategy_id, tx_data, test_datas) -> (dict, bool):
    #     """
    #     This method checks if the test data matches the transaction data and returns a dictionary with the result and a
    #     boolean indicating if the test passed.
    #
    #     Args:
    #         i: The test number.
    #         strategy_id: The strategy id.
    #         tx_data: The transaction data.
    #
    #     Returns:
    #         A dictionary with the result and a boolean indicating if the test passed.
    #     """
    #     result, passed = {}, False
    #     for test_data in test_datas:
    #         if not strategy_id:
    #             result, passed = {"msg": f"Test {i} FAILED", "tx_data": "strategyid not in test_strategy_txhashs"}, False
    #         elif test_data is None:
    #             result, passed = {"msg": f"Test {i} FAILED", "tx_data": tx_data, "test_data": "Test data missing"}, False
    #         elif tx_data == test_data:
    #             result, passed = {"msg": f"Test {i} PASSED"}, True
    #         else:
    #             result, passed = {"msg": f"Test {i} FAILED", "tx_data": tx_data, "test_data": test_data}, False
    #
    #         if passed:
    #             break
    #
    #     return result, passed
    #
    # def log_summary(self, all_tests_passed, args):
    #     if all_tests_passed:
    #         args.logger.info("ALL TESTS PASSED")
    #     else:
    #         args.logger.warning("SOME TESTS FAILED")
    #
    # def log_results(self, args, successful_txs, test_datas, test_strategy_txhashs):
    #     results_description = {}
    #     all_tests_passed = True
    #
    #     for i, txhash in test_strategy_txhashs.items():
    #         strategy_id = txhash.get("strategyid")
    #         print(f"search_id: {strategy_id}")  # Assuming necessary for debugging
    #         tx_data = self.clean_tx_data(self.get_tx_data(strategy_id, successful_txs))
    #
    #         result, test_passed = self.check_test_result(i, strategy_id, tx_data, test_datas)
    #         results_description[i] = result
    #         if not test_passed:
    #             all_tests_passed = False
    #
    #     self.log_summary(all_tests_passed, args)
    #     return results_description

    def wait_for_txs(self, args):
        test_strategy_txhashs = self.load_json_file("test_strategy_txhashs.json", args)
        sleep_seconds = int(35 * len(test_strategy_txhashs.keys()) + 15)
        args.logger.debug(f"sleep_seconds: {sleep_seconds}")
        time.sleep(sleep_seconds)
        return test_strategy_txhashs
