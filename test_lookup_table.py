import unittest
from lookup_table import (
    LookupTable,
)  # Assuming the dataclass is saved in lookup_table.py
import json

json_path = "/Users/mikewcasale/Documents/GitHub/bancor/fastlane-bot/logs/20231220-110314/latest_pool_data.json"

with open(json_path) as f:
    json_data = json.load(f)


class TestLookupTable(unittest.TestCase):
    test_data = None

    @classmethod
    def setUpClass(cls):
        # Use a subset of the JSON data for testing
        cls.test_data = json_data[:10]  # Assuming json_data is loaded as shown earlier
        cls.lookup_table = LookupTable(cls.test_data)

    def test_initialization(self):
        self.assertEqual(len(self.lookup_table.json_data), len(self.test_data) - 1)
        self.assertEqual(len(self.lookup_table.df), len(self.test_data) - 1)

        # sourcery skip: no-loop-in-tests
        for key in [
            "address",
            "tkn0_address",
            "tkn1_address",
            "exchange_name",
            "last_updated_block",
        ]:
            self.assertIn(key, self.lookup_table.keys)

    def test_create_dict_from_column(self):
        # sourcery skip: no-loop-in-tests
        for key in [
            "address",
            "tkn0_address",
            "tkn1_address",
            "exchange_name",
            "last_updated_block",
        ]:
            key_dict = self.lookup_table.create_dict_from_column(key)
            self.assertIsInstance(key_dict, dict)
            for value in key_dict:
                self.assertIsInstance(key_dict[value], list)
                self.assertTrue(all(isinstance(cid, str) for cid in key_dict[value]))

    def test_get_cids_with_valid_address(self):
        value = self.lookup_table.df.iloc[0]["address"]
        cids = self.lookup_table.get_cids("address", value)
        self.assertIsInstance(cids, list)
        self.assertTrue(all(isinstance(cid, str) for cid in cids))

    def test_get_cids_with_invalid_key(self):
        with self.assertRaises(ValueError):
            self.lookup_table.get_cids("invalid_key", "some_value")

    def test_get_cids_with_non_existent_address(self):
        cids = self.lookup_table.get_cids("address", "non_existent_address")
        self.assertEqual(cids, [])

    def test_get_records_with_valid_exchange_name(self):
        value = self.lookup_table.df.iloc[0]["exchange_name"]
        records = self.lookup_table.get_records("exchange_name", value)
        self.assertIsInstance(records, list)
        self.assertTrue(all(isinstance(record, dict) for record in records))

    def test_get_records_with_non_existent_exchange_name(self):
        records = self.lookup_table.get_records(
            "exchange_name", "non_existent_exchange"
        )
        self.assertEqual(records, [])

    def test_delete_record_with_specific_address(self):
        value = self.lookup_table.df.iloc[0]["address"]
        self.lookup_table.delete_record("address", value)
        self.assertNotIn(value, self.lookup_table.address_dict)

    def test_add_specific_record(self):
        new_record = json_data[-1]
        new_record["cid"] = "new_cid"
        self.lookup_table.add_record(new_record)
        self.assertIn("new_cid", self.lookup_table.cid_dict)
        self.assertIn(new_record, self.lookup_table.json_data)

    def test_update_specific_record(self):
        cid = self.lookup_table.df.iloc[0]["cid"]
        updated_record = self.lookup_table.df.loc[cid].to_dict()
        updated_record["address"] = "updated_address"
        self.lookup_table.update_record(updated_record)
        self.assertIn("updated_address", self.lookup_table.address_dict)

    def test_get_records_with_condition_last_updated_block(self):
        # Assuming you have at least one record where last_updated_block < some_value
        some_value = int(max(record["last_updated_block"] for record in self.test_data))
        expected_cid = [
            record["cid"]
            for record in self.test_data
            if record["last_updated_block"] < some_value
        ]

        # Call the get_records with the new condition
        records = self.lookup_table.get_records(
            "last_updated_block", "", f"< {some_value}"
        )
        received_cid = [record["cid"] for record in records]

        # Assert that the returned records match the expected condition
        self.assertEqual(expected_cid, received_cid)


if __name__ == "__main__":
    unittest.main()
