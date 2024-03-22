"""
Submit handler for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
__VERSION__ = "1.0"
__DATE__ = "01/May/2023"

from typing import List, Any, Dict
from .routehandler import RouteStruct
from ..data.abi import FAST_LANE_CONTRACT_ABI
from fastlane_bot.config import Config

def submit_transaction_tenderly(
    cfg: Config,
    route_struct: List[RouteStruct],
    src_address: str,
    src_amount: int,
    flashloan_struct: List[Dict[str, int or str]],
) -> Any:
    """
    Submits a transaction to the network.

    Parameters
    ----------
    route_struct: the list of RouteStruct objects
    flashloan_struct: The list of objects containing Flashloan instructions
    src_amount: DEPRECATED. Source amount used in function flashloanAndArb
    src_address: DEPRECATED Source token address used in function flashloanAndArb

    Returns
    -------
    str
        The transaction hash.
    """

    arb_contract = cfg.w3.eth.contract(
        address=cfg.w3.to_checksum_address(cfg.network.FASTLANE_CONTRACT_ADDRESS),
        abi=FAST_LANE_CONTRACT_ABI
    )

    address = cfg.w3.to_checksum_address(cfg.BINANCE14_WALLET_ADDRESS)

    if cfg.SELF_FUND:
        return arb_contract.functions.fundAndArb(route_struct, src_address, src_amount).transact(
            {
                "gas": cfg.DEFAULT_GAS,
                "from": address,
                "nonce": cfg.w3.eth.get_transaction_count(address),
                "gasPrice": 0,
                "value": src_amount if src_address in cfg.NATIVE_GAS_TOKEN_ADDRESS else 0
            }
        )

    elif flashloan_struct is None:
        return arb_contract.functions.flashloanAndArb(route_struct, src_address, src_amount).transact(
            {
                "gas": cfg.DEFAULT_GAS,
                "from": address,
                "nonce": cfg.w3.eth.get_transaction_count(address),
                "gasPrice": 0,
            }
        )

    else:
        return arb_contract.functions.flashloanAndArbV2(flashloan_struct, route_struct).transact(
            {
                "gas": cfg.DEFAULT_GAS,
                "from": address,
                "nonce": cfg.w3.eth.get_transaction_count(address),
                "gasPrice": 0,
            }
        )
