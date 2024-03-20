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
PANCAKESWAP_V3_NAME = "pancakeswap_v3"
BUTTER_V3_NAME = "butter_v3"
AGNI_V3_NAME = "agni_v3"
CLEOPATRA_V3_NAME = "cleopatra_v3"