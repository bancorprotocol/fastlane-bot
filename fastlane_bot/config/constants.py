"""
This file constains the constants used in the fastlane_bot package.
(c) Copyright Bprotocol foundation 2023.
Licensed under MIT License.
"""
import os

FLASHLOAN_FEE_MAP = {
    # should be in the form of {network: fee * 1e6}
    "ethereum": 0,
    "coinbase_base": 0,
    "fantom": 0,
}
WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")
WEB3_ALCHEMY_POLYGON = os.environ.get("WEB3_ALCHEMY_POLYGON")
WEB3_ALCHEMY_POLYGON_ZKEVM = os.environ.get("WEB3_ALCHEMY_POLYGON_ZKEVM")
WEB3_ALCHEMY_OPTIMISM = os.environ.get("WEB3_ALCHEMY_OPTIMISM")
WEB3_ALCHEMY_BASE = os.environ.get("WEB3_ALCHEMY_BASE")
WEB3_ALCHEMY_ARBITRUM = os.environ.get("WEB3_ALCHEMY_ARBITRUM")

# Supported Blockchain Networks
ETHEREUM_NETWORK = "ethereum"
POLYGON_NETWORK = "polygon"
POLYGON_ZKEVM_NETWORK = "polygon_zkevm"
OPTIMISM_NETWORK = "optimism"
COINBASE_BASE_NETWORK = "coinbase_base"
ARBITRUM_ONE_NETWORK = "arbitrum_one"
