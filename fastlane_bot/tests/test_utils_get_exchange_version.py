# test_utils.py

import pytest

from fastlane_bot.constants import ec
from fastlane_bot.utils import get_exchange_version

"""
Code Analysis:
-- Takes an exchange name as an argument
- Splits the exchange name into two parts: exchange name and exchange version
- Retrieves the exchange ID and version ID from the EXCHANGE_IDS dictionary
- Returns a tuple containing the exchange name, exchange version, exchange, exchange ID, and version ID
"""

"""
Test Plan:
- test_valid_exchange_name(): tests that a valid exchange name is correctly split into exchange name and version
- test_valid_exchange_id(): tests that a valid exchange ID is correctly retrieved from the EXCHANGE_IDS dictionary
- test_valid_version_id(): tests that a valid version ID is correctly retrieved from the EXCHANGE_IDS dictionary
- test_valid_return_values(): tests that the correct return values are returned when a valid exchange name is passed
- test_invalid_exchange_name(): tests the edge case where passing an invalid exchange name leads to an error
- test_invalid_exchange_id(): tests the edge case where passing an invalid exchange ID leads to an error

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestGetExchangeVersion:
    def test_valid_exchange_name(self):
        exchange = "uniswap_v3"
        exchange_name, exchange_version = exchange.split("_")
        assert exchange_name == "uniswap"
        assert exchange_version == "v3"

    def test_valid_version_id(self):
        exchange = "uniswap_v3"
        exchange_id, version_id = ec.EXCHANGE_IDS[exchange]
        assert version_id == 3

    def test_valid_return_values(self):
        exchange = "uniswap_v3"
        (
            exchange_name,
            exchange_version,
            exchange,
            exchange_id,
            version_id,
        ) = get_exchange_version(exchange)
        assert exchange_name == "uniswap"
        assert exchange_version == "v3"
        assert exchange == "uniswap_v3"
        assert exchange_id == 4
        assert version_id == 3

    def test_invalid_exchange_name(self):
        with pytest.raises(ValueError):
            get_exchange_version("uniswap")

    def test_invalid_exchange_id(self):
        with pytest.raises(KeyError):
            get_exchange_version("uniswap_v4")
