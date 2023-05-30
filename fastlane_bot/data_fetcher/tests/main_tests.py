import json
import os
import unittest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

import pandas as pd
from web3 import Web3
from dotenv import load_dotenv
from events.main import (
    main,
    run,
    complex_handler,
    attribute_dict_to_dict,
    filter_latest_events,
)

"""
Test Plan:
This test module aims to test the functionality of the main script which includes the `main` function, 
`run` function and utility functions for handling and manipulating event data. 
We use mocking to avoid the necessity for real blockchain interaction and file access, and 
to provide expected return values. 
"""


class MainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()
        cls.web3 = Web3(
            Web3.HTTPProvider("http://127.0.0.1:8545")
        )  # Mock web3 provider
        cls.df = pd.DataFrame()  # Mock dataframe

        # Mock the 'Manager' object and its methods
        cls.manager = MagicMock()
        cls.manager.web3 = cls.web3
        cls.manager.events = []

        load_dotenv()  # Load environment variables

    def test_main_with_invalid_csv_file(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                main, ["--n_jobs", 1, "--external_exchanges", "uniswap_v3"]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertIn("CSV file does not exist", result.output)

    @patch("pandas.read_csv")
    def test_main_with_valid_csv_file(self, mock_read_csv):
        mock_read_csv.return_value = self.df
        with self.runner.isolated_filesystem():
            with open("fastlane_bot/data/combined_tables_new.csv", "w") as f:
                f.write("")
            result = self.runner.invoke(
                main, ["--n_jobs", 1, "--external_exchanges", "uniswap_v3"]
            )
            self.assertEqual(result.exit_code, 0)

    @patch("main.Manager")
    def test_run(self, mock_manager):
        mock_manager.return_value = self.manager
        run(self.manager, n_jobs=1)

    def test_complex_handler(self):
        self.assertIsNone(complex_handler(123))

    def test_attribute_dict_to_dict(self):
        self.assertDictEqual(attribute_dict_to_dict({"test": "data"}), {"test": "data"})

    def test_filter_latest_events(self):
        events = [
            [{"address": "0x1", "blockNumber": 1}, {"address": "0x2", "blockNumber": 2}]
        ]
        self.assertListEqual(
            list(filter_latest_events(events)),
            [
                {"address": "0x1", "blockNumber": 1},
                {"address": "0x2", "blockNumber": 2},
            ],
        )


if __name__ == "__main__":
    unittest.main()
