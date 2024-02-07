import pytest

from fastlane_bot.config.connect import NetworkBase
from fastlane_bot.config.constants import ARBITRUM_ONE_NETWORK, COINBASE_BASE_NETWORK, ETHEREUM_NETWORK, \
    OPTIMISM_NETWORK, POLYGON_NETWORK, \
    POLYGON_ZKEVM_NETWORK, WEB3_ALCHEMY_BASE, WEB3_ALCHEMY_PROJECT_ID


@pytest.mark.parametrize("network_name,expected_url", [
    (ETHEREUM_NETWORK, f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}"),
    # (COINBASE_BASE_NETWORK, f"https://base-mainnet.g.alchemy.com/v2/{WEB3_ALCHEMY_BASE}"),
])
def test_get_rpc_url_for_networks_without_rpc_url(network_name, expected_url):
    assert NetworkBase.get_rpc_url(network_name, rpc_url="") == expected_url


def test_get_rpc_url_with_explicit_rpc_url():
    custom_rpc_url = "https://custom-rpc.com"
    assert NetworkBase.get_rpc_url("AnyNetwork", rpc_url=custom_rpc_url) == custom_rpc_url
