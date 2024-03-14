"""
This file constains the constants used in the fastlane_bot package.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT License.
"""

FLASHLOAN_FEE_MAP = {
    "ethereum": 0,
    "coinbase_base": 0,
    "fantom": 0.0003
}
BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
LINK_ADDRESS = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
BANCOR_V3_FLASHLOAN_TOKENS = [BNT_ADDRESS, ETH_ADDRESS, WBTC_ADDRESS,
                              LINK_ADDRESS]
