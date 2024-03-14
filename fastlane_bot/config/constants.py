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

BANCOR_V2_NAME = "bancor_v2"
BANCOR_V3_NAME = "bancor_v3"
UNISWAP_V2_NAME = "uniswap_v2"
UNISWAP_V3_NAME = "uniswap_v3"
SUSHISWAP_V2_NAME = "sushiswap_v2"
SUSHISWAP_V3_NAME = "sushiswap_v3"
CARBON_V1_NAME = "carbon_v1"
BANCOR_POL_NAME = "bancor_pol"
BALANCER_NAME = "balancer"
PANCAKESWAP_V2_NAME = "pancakeswap_v2"
PANCAKESWAP_V3_NAME = "pancakeswap_v3"
AERODROME_V2_NAME = "aerodrome_v2"
VELOCIMETER_V2_NAME = "velocimeter_v2"
CARBON_POL_NAME = "bancor_pol"
SHIBA_V2_NAME = "shiba_v2"
SCALE_V2_NAME = "scale_v2"
EQUALIZER_V2_NAME = "equalizer_v2"
SOLIDLY_V2_NAME = "solidly_v2"
VELODROME_V2_NAME = "velodrome_v2"

SOLIDLY_FORKS = [AERODROME_V2_NAME, VELOCIMETER_V2_NAME, SCALE_V2_NAME, VELODROME_V2_NAME]


EXCHANGE_IDS = {
    BANCOR_V2_NAME: 1,
    BANCOR_V3_NAME: 2,
    UNISWAP_V2_NAME: 3,
    UNISWAP_V3_NAME: 4,
    SUSHISWAP_V2_NAME: 3,
    SUSHISWAP_V3_NAME: 4,
    CARBON_V1_NAME: 6,
    BALANCER_NAME: 7,
    CARBON_POL_NAME: 8,
    PANCAKESWAP_V2_NAME: 3,
    PANCAKESWAP_V3_NAME: 4,
    SOLIDLY_V2_NAME: 11,
    VELOCIMETER_V2_NAME: 11,
    SCALE_V2_NAME: 11,
    EQUALIZER_V2_NAME: 11,
    VELODROME_V2_NAME: 12,
    AERODROME_V2_NAME: 12,
}