"""
This module contains the TxHelper class which is a utility class to scan the logs directory for successful transactions
and clean and extract the transaction data.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import glob
import json
import os
import time

from fastlane_bot.tests.deterministic.test_constants import FILE_DATA_DIR, TEST_FILE_DATA_DIR


class TestTxHelper:
    """
    This is a utility class to scan the logs directory for successful transactions and clean and extract the
    transaction data.
    """

    @staticmethod
    def tx_scanner(args) -> list:
        """
        This method scans the logs directory for successful transactions and returns a list of the successful
        transactions.
        """
        # Set the path to the logs directory relative to your notebook's location
        path_to_logs = "./logs/*"

        # Use glob to list all directories
        most_recent_log_folder = [
            f for f in glob.glob(path_to_logs) if os.path.isdir(f)
        ][-1]
        args.logger.debug(f"Accessing log folder {most_recent_log_folder}")

        most_recent_pool_data = os.path.join(
            most_recent_log_folder, "latest_pool_data.json"
        )

        args.logger.debug("Looking for pool data file...")
        while True:
            if os.path.exists(most_recent_pool_data):
                args.logger.debug("File found.")
                break
            else:
                args.logger.debug("File not found, waiting 10 seconds.")
                time.sleep(10)

        with open(most_recent_pool_data) as f:
            pool_data = json.load(f)
            args.logger.debug(f"len(pool_data): {len(pool_data)}")

        all_successful_txs = glob.glob(os.path.join(most_recent_log_folder, "*.txt"))

        # Read the successful_txs in as strings
        txt_all_successful_txs = []
        for successful_tx in all_successful_txs:
            with open(successful_tx, "r") as file:
                j = file.read()
                txt_all_successful_txs += [(j)]

        # Successful transactions on Tenderly are marked by status=1
        successful_txs = [tx for tx in txt_all_successful_txs if "'status': 1" in tx]
        args.logger.debug(
            f"len(actually_txt_all_successful_txs): {len(successful_txs)}"
        )
        return successful_txs

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
                return json.loads(tx.split("\n\n")[-1])

    @staticmethod
    def load_json_file(file_name: str, args) -> dict:
        if '/' not in file_name:
            file_path = os.path.normpath(f"{TEST_FILE_DATA_DIR}/{file_name}")
        else:
            file_path = os.path.normpath(file_name)
        if not os.path.exists(file_path):
            return {}
        with open(file_path) as f:
            data = json.load(f)
            f.close()
            args.logger.debug(f"len({file_name})={len(data.keys())}")
        return data

    @staticmethod
    def log_txs(tx_list, args):
        # print first 3 examples of actually_txt_all_successful_txs
        for i, tx in enumerate(tx_list):
            args.logger.debug(f"\nsuccessful_txs[{i}]: {tx}")

    def log_results(self, args, successful_txs, test_datas, test_strategy_txhashs):
        results_description = {}
        all_tests_passed = True

        # Loop over the created test strategies and verify test data
        for i in test_strategy_txhashs.keys():
            if 'strategyid' not in test_strategy_txhashs[str(i)]:
                continue
            search_id = test_strategy_txhashs[str(i)]["strategyid"]
            print(f"search_id: {search_id}")
            tx_data = self.clean_tx_data(self.get_tx_data(search_id, successful_txs))
            if str(i) not in test_datas:
                results_description[i] = {"msg": f"Test {i} FAILED",
                                          "tx_data": tx_data,
                                          "test_data": f"{i} not in test_datas: {test_datas.keys()}"}
                all_tests_passed = False
                continue

            test_data = test_datas[str(i)]
            if tx_data == test_data:
                results_description[str(i)] = {"msg": f"Test {i} PASSED"}
            else:
                results_description[str(i)] = {"msg": f"Test {i} FAILED",
                                          "tx_data": tx_data,
                                          "test_data": test_data}
                all_tests_passed = False

        if not all_tests_passed:
            args.logger.warning("SOME TESTS FAILED")
        else:
            args.logger.info("ALL TESTS PASSED")

        return results_description

    def wait_for_txs(self, args):
        test_strategy_txhashs = self.load_json_file("test_strategy_txhashs.json", args)
        sleep_seconds = int(35 * len(test_strategy_txhashs.keys()) + 15)
        args.logger.debug(f"sleep_seconds: {sleep_seconds}")
        time.sleep(sleep_seconds)
        return test_strategy_txhashs
