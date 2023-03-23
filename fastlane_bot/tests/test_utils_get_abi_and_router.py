# test_utils.py

import pytest
from unittest.mock import MagicMock
from fastlane_bot.constants import ec
from fastlane_bot.utils import get_abi_and_router

"""
Code Analysis:
-- Function takes in a string parameter, 'exchange', which is the name of the exchange to get the ABI and POOL_INFO_FOR_EXCHANGE for
- Function returns a tuple of the ABI and POOL_INFO_FOR_EXCHANGE
- If the exchange is Uniswap V3, the ABI is set to the Uniswap V3 Pool ABI and the POOL_INFO_FOR_EXCHANGE is set to the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Uniswap V3
- If the exchange is Uniswap V2, the POOL_INFO_FOR_EXCHANGE is set to the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Uniswap V2 and the ABI is set to the Uniswap V2 Pool ABI
- If the exchange is Sushiswap, the POOL_INFO_FOR_EXCHANGE is set to the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Sushiswap and the ABI is set to the Sushiswap Pools ABI
- If the exchange is Bancor V2, the POOL_INFO_FOR_EXCHANGE is set to the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Bancor V2 and the ABI is set to the Bancor V2 Converter ABI
- If the exchange is Bancor V3, the POOL_INFO_FOR_EXCHANGE is set to the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Bancor V3 and the ABI is set to the Bancor V3 Pool ABI
- Function returns the ABI and POOL_INFO_FOR_EXCHANGE
"""

"""
Test Plan:
- test_uniswap_v3_abi_and_router(): tests that passing Uniswap V3 as the exchange parameter returns the Uniswap V3 Pool ABI and the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Uniswap V3
- test_uniswap_v2_abi_and_router(): tests that passing Uniswap V2 as the exchange parameter returns the Uniswap V2 Pool ABI and the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Uniswap V2
- test_sushiswap_abi_and_router(): tests that passing Sushiswap as the exchange parameter returns the Sushiswap Pools ABI and the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Sushiswap
- test_bancor_v2_abi_and_router(): tests that passing Bancor V2 as the exchange parameter returns the Bancor V2 Converter ABI and the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Bancor V2
- test_no_exchange_param(): tests the edge case where passing no exchange parameter leads to an error
- test_bancor_v3_abi_and_router(): tests that passing Bancor V3 as the exchange parameter returns the Bancor V3 Pool ABI and the POOL_INFO_FOR_EXCHANGE from the DB where the exchange is Bancor V3

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestGetAbiAndRouter:
    def test_uniswap_v3_abi_and_router(self):
        abi, pool_info = get_abi_and_router("uniswap_v3")
        assert abi == ec.UNISWAP_V3_POOL_ABI

    def test_uniswap_v2_abi_and_router(self):
        abi, pool_info = get_abi_and_router("uniswap_v2")
        assert abi == ec.UNISWAP_V2_POOL_ABI

    def test_sushiswap_abi_and_router(self):
        abi, pool_info = get_abi_and_router("sushiswap_v2")
        assert abi == ec.SUSHISWAP_POOLS_ABI

    def test_bancor_v2_abi_and_router(self):
        abi, pool_info = get_abi_and_router("bancor_v2")
        assert abi == ec.BANCOR_V2_CONVERTER_ABI

    def test_no_exchange_param(self):
        with pytest.raises(TypeError):
            get_abi_and_router()
