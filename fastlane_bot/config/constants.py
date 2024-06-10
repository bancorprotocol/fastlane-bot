"""
Hosts a number of constants used throughout the project.

TODO: this seems to be a pretty small and random collection of constants. Either
many more should move here, or they should move elsewhere (note that they probably
would feel right at home in the Config class).

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""

FLASHLOAN_FEE_MAP = {
    "ethereum": 0,
    "coinbase_base": 0,
    "fantom": 0.0003,
    "mantle": 0,
}

ETHEREUM = "ethereum"
UNISWAP_V2_NAME = "uniswap_v2"
UNISWAP_V3_NAME = "uniswap_v3"
PANCAKESWAP_V2_NAME = "pancakeswap_v2"
PANCAKESWAP_V3_NAME = "pancakeswap_v3"
BUTTER_V3_NAME = "butter_v3"
AGNI_V3_NAME = "agni_v3"
FUSIONX_V3_NAME = "fusionx_v3"
CLEOPATRA_V3_NAME = "cleopatra_v3"
CARBON_V1_NAME = "carbon_v1"
VELOCIMETER_V2_NAME = "velocimeter_v2"
SOLIDLY_V2_NAME = "solidly_v2"
ECHODEX_V3_NAME = "echodex_v3"
SECTA_V3_NAME = "secta_v3"
METAVAULT_V3_NAME = "metavault_v3"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

BLOCK_CHUNK_SIZE_MAP = {
    "ethereum": 0,
    "polygon": 0,
    "polygon_zkevm": 0,
    "arbitrum_one": 0,
    "optimism": 0,
    "coinbase_base": 0,
    "fantom": 5000,
    "mantle": 0,
    "linea": 0,
    "sei": 2000,
}
