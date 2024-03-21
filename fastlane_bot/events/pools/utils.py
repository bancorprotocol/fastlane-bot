from typing import Any, Dict, List

from web3 import Web3


def get_pool_cid(args: Dict[str, Any], carbon_v1_forks: List[str]) -> str:
    """
    Get the pool CID from the event args

    Args:
        args : Dict[str, Any]
            The event args
        carbon_v1_forks : List[str]
            The list of Carbon v1 forks

    Returns:
        str
            The pool CID
    """

    unique_key = get_cid_base(args, carbon_v1_forks)
    return Web3.keccak(text=unique_key).hex()


def get_cid_base(args: Dict[str, Any], carbon_v1_forks: List[str]) -> str:
    """
    Get the base key for the pool CID from the event args

    Args:
        args : Dict[str, Any]
            The event args
        carbon_v1_forks : List[str]
            The list of Carbon v1 forks

    Returns:
        str
            The base key for the pool CID
    """
    return (
            args["exchange_name"]
            + " "
            + str(args["strategy_id"])
    ) if args["exchange_name"] in carbon_v1_forks else (
            args["exchange_name"]
            + " "
            + args["pair_name"]
            + " "
            + str(args["fee"])
    )
