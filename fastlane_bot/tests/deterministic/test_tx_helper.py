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


class TestTxHelper:
    """
    This is a utility class to scan the logs directory for successful transactions and clean and extract the
    transaction data.
    """

    @staticmethod
    def tx_scanner() -> list:
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
        print(f"Accessing log folder {most_recent_log_folder}")

        most_recent_pool_data = os.path.join(
            most_recent_log_folder, "latest_pool_data.json"
        )

        print("Looking for pool data file...")
        while True:
            if os.path.exists(most_recent_pool_data):
                print("File found.")
                break
            else:
                print("File not found, waiting 10 seconds.")
                time.sleep(10)

        with open(most_recent_pool_data) as f:
            pool_data = json.load(f)
            print("len(pool_data)", len(pool_data))

        all_successful_txs = glob.glob(os.path.join(most_recent_log_folder, "*.txt"))

        # Read the successful_txs in as strings
        txt_all_successful_txs = []
        for successful_tx in all_successful_txs:
            with open(successful_tx, "r") as file:
                j = file.read()
                txt_all_successful_txs += [(j)]

        # Successful transactions on Tenderly are marked by status=1
        return [tx for tx in txt_all_successful_txs if "'status': 1" in tx]

    @staticmethod
    def clean_tx_data(tx_data: dict) -> dict:
        """
        This method takes a transaction data dictionary and removes the cid0 key from the trades.
        """
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
