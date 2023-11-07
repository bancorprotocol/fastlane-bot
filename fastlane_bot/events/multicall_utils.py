# coding=utf-8
"""
This is the multicaller utils module.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from decimal import Decimal
from typing import Dict, Any
from typing import List, Tuple

import pandas as pd

from fastlane_bot.config.multicaller import MultiCaller
from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.events.pools import CarbonV1Pool
from fastlane_bot.events.pools.base import Pool

ONE = 2**48


def bit_length(value: int) -> int:
    """
    Get the bit length of a value.

    Parameters
    ----------
    value: int
        The value to get the bit length of.

    Returns
    -------
    int
        The bit length of the value.

    """

    return len(bin(value).lstrip("0b")) if value > 0 else 0


def encode_float(value: int) -> int:
    """
    Encode a float value.

    Parameters
    ----------
    value: int
        The value to encode.

    Returns
    -------
    int
        The encoded value.

    """
    exponent = bit_length(value // ONE)
    mantissa = value >> exponent
    return mantissa | (exponent * ONE)


def encode_rate(value: int) -> int:
    """
    Encode a rate value.

    Parameters
    ----------
    value: int
        The value to encode.

    Returns
    -------
    int
        The encoded value.

    """
    data = int(value.sqrt() * ONE)
    length = bit_length(data // ONE)
    return (data >> length) << length


def encode_token_price(price: Decimal) -> int:
    """
    Encode a token price.

    Parameters
    ----------
    price: Decimal
        The price to encode.

    Returns
    -------
    int
        The encoded price.

    """
    return encode_float(encode_rate((price)))


def get_pools_for_exchange(exchange: str, mgr: Any) -> [Any]:
    """
    Handles the initial iteration of the bot.

    Parameters
    ----------
    mgr : Any
        The manager object.
    exchange : str
        The exchange for which to get pools

    Returns
    -------
    List[Any]
        A list of pools for the specified exchange.
    """
    return mgr.pool_data[
        mgr.pool_data.index.get_level_values("exchange_name") == exchange
    ].index.tolist()


def multicall_helper(
    exchange: str,
    rows_to_update: List,
    multicall_contract: Any,
    mgr: Any,
    current_block: int,
):
    """
    Helper function for multicall.

    Parameters
    ----------
    exchange : str
        Name of the exchange.
    rows_to_update : List
        List of rows to update.
    multicall_contract : Any
        The multicall contract.
    mgr : Any
        Manager object containing configuration and pool data.
    current_block : int
        The current block.

    """
    multicaller = MultiCaller(
        contract=multicall_contract,
        block_identifier=current_block,
        multicall_address=mgr.cfg.MULTICALL_CONTRACT_ADDRESS,
    )
    with multicaller as mc:
        for row in rows_to_update:
            pool_info = (
                mgr.pool_data[mgr.pool_data.index == row]
                .reset_index()
                .to_dict("records")[0]
            )
            pool_info["last_updated_block"] = current_block
            # Function to be defined elsewhere based on what each exchange type needs
            multicall_fn(exchange, mc, multicall_contract, pool_info)
        result_list = mc.multicall()
    process_results_for_multicall(exchange, rows_to_update, result_list, mgr)


def multicall_fn(
    exchange: str, mc: Any, multicall_contract: Any, pool_info: Dict[str, Any]
) -> None:
    """
    Function to be defined elsewhere based on what each exchange type needs.

    Parameters
    ----------
    exchange : str
        Name of the exchange.
    mc : Any
        The multicaller.
    multicall_contract : Any
        The multicall contract.
    pool_info : Dict
        The pool info.

    """
    if exchange == "bancor_v3":
        mc.add_call(
            multicall_contract.functions.tradingLiquidity, pool_info["tkn1_address"]
        )
    elif exchange == "bancor_pol":
        mc.add_call(multicall_contract.functions.tokenPrice, pool_info["tkn0_address"])
    elif exchange == "carbon_v1":
        mc.add_call(multicall_contract.functions.strategy, pool_info["cid"])
    elif exchange == "balancer":
        mc.add_call(multicall_contract.functions.getPoolTokens, pool_info["anchor"])
    else:
        raise ValueError(f"Exchange {exchange} not supported.")


def process_results_for_multicall(
    exchange: str, rows_to_update: List, result_list: List, mgr: Any
) -> None:
    """
    Process the results for multicall.

    Parameters
    ----------
    exchange : str
        Name of the exchange.
    rows_to_update : List
        List of rows to update.
    result_list : List
        List of results.
    mgr : Any
        Manager object containing configuration and pool data.


    """
    mgr.pool_data.sort_index(inplace=True)
    indexes = [
        "exchange_name",
        "tkn0_address",
        "tkn1_address",
        "cid",
        "address",
        "last_updated_block",
    ]
    for row, result in zip(rows_to_update, result_list):
        pool_info = mgr.pool_data[mgr.pool_data.index == row]
        pool_info_dic = pool_info.reset_index().to_dict("records")[0]
        pool_info_dic["state"] = pool_info_dic
        params = extract_params_for_multicall(exchange, result, pool_info_dic, mgr)
        pool = mgr.get_or_init_pool(pool_info)
        if len(pool.state) == 0:
            pool.state = pool_info
        state_cp = pool.state.copy()
        update_params = {row: params}
        state_cp.update(update_params)
        pool.state = state_cp

        # update the mgr.pool_data row with the new state
        mgr.pool_data.update(update_params)
        update_mgr_exchanges_for_multicall(
            mgr, exchange, pool, pool.state.reset_index().to_dict("records")[0]
        )


def extract_params_for_multicall(
    exchange: str, result: Any, pool_info: Dict, mgr: Any
) -> Dict[str, Any]:
    """
    Extract the parameters for multicall.

    Parameters
    ----------
    exchange : str
        Name of the exchange.
    result : Any
        The result.
    pool_info : Dict
        The pool info.
    mgr : Any
        Manager object containing configuration and pool data.

    """
    params = {}
    if exchange == "carbon_v1":
        strategy = result
        fake_event = {
            "args": {
                "id": strategy[0],
                "order0": strategy[3][0],
                "order1": strategy[3][1],
            }
        }
        params = CarbonV1Pool.parse_event(pool_info["state"], fake_event, "None")
        params["exchange_name"] = exchange
    elif exchange == "bancor_pol":
        params = _extract_pol_params_for_multicall(result, pool_info, mgr)
    elif exchange == "bancor_v3":
        pool_balances = result
        params = {
            "fee": "0.000",
            "fee_float": 0.000,
            "tkn0_balance": pool_balances[0],
            "tkn1_balance": pool_balances[1],
            "exchange_name": exchange,
            "address": pool_info["address"],
        }
    elif exchange == "balancer":
        pool_balances = result

        params = {
            "exchange_name": exchange,
            "address": pool_info["address"],
        }

        for idx, bal in enumerate(pool_balances):
            params[f"tkn{str(idx)}_balance"] = int(bal)

    else:
        raise ValueError(f"Exchange {exchange} not supported.")

    return params


def _extract_pol_params_for_multicall(
    result: Any, pool_info: Dict, mgr: Any
) -> Dict[str, Any]:
    """
    Extract the Bancor POL params for multicall.

    Parameters
    ----------
    result : Any
        The result.
    pool_info : Dict
        The pool info.
    mgr : Any
        Manager object containing configuration and pool data.

    Returns
    -------
    Dict[str, Any]
        The extracted params.

    """
    prices = result
    p0, p1 = prices
    token_price = Decimal(p1) / Decimal(p0)
    tkn0_address = pool_info["tkn0_address"]
    tkn_contract = mgr.token_contracts.get(
        tkn0_address, mgr.web3.eth.contract(abi=ERC20_ABI, address=tkn0_address)
    )
    if tkn0_address not in mgr.token_contracts:
        mgr.token_contracts[tkn0_address] = tkn_contract
    tkn_balance = tkn_contract.functions.balanceOf(mgr.cfg.BANCOR_POL_ADDRESS).call()
    result = {
        "fee": "0.000",
        "fee_float": 0.000,
        "tkn0_balance": 0,
        "tkn1_balance": 0,
        "exchange_name": pool_info["exchange_name"],
        "address": pool_info["address"],
        "y_0": tkn_balance,
        "z_0": tkn_balance,
        "A_0": 0,
        "B_0": int(str(encode_token_price(token_price))),
    }
    return result


def update_pool_for_multicall(
    params: Dict[str, Any], pool_info: Dict, pool: Any
) -> Tuple[Pool, Dict]:
    """
    Update the pool for multicall.

    Parameters
    ----------
    params : Dict
        The parameters.
    pool_info : Dict
        The pool info.
    pool : Any
        The pool.

    Returns
    -------
    Tuple[Pool, Dict]
        The updated pool and pool info.

    """
    for key, value in params.items():
        pool_info[key] = value
        pool.state[key] = value
    return pool, pool_info


def update_mgr_exchanges_for_multicall(
    mgr: Any, exchange: str, pool: Any, pool_info: Dict[str, Any]
):
    """
    Update the manager exchanges for multicall.

    Parameters
    ----------
    mgr : Any
        Manager object containing configuration and pool data.
    exchange : str
        Name of the exchange.
    pool : Any
        The pool.
    pool_info : Dict
        The pool info.

    """
    unique_key = pool.unique_key()
    if unique_key == "token":
        # Handles the bancor POL case
        unique_key = "tkn0_address"

    unique_key_value = pool_info[unique_key]
    # p = mgr.exchanges[exchange].pools[unique_key_value]
    # print(f"ppppp {p.state.index.names}")
    # if unique_key_value in [
    #     "exchange_name",
    #     "tkn0_address",
    #     "tkn1_address",
    #     "cid",
    #     "address",
    #     "last_updated_block",
    # ]:
    #     exchange_pool_idx = [
    #         idx
    #         for idx in range(len(mgr.exchanges[exchange].pools))
    #         if mgr.exchanges[exchange]
    #         .pools[unique_key_value]
    #         .state.index.get_level_values(unique_key)
    #         .tolist()[0]
    #         == pool_info[unique_key]
    #     ][0]
    # else:
    #     exchange_pool_idx = [
    #         idx
    #         for idx in range(len(mgr.exchanges[exchange].pools))
    #         if mgr.exchanges[exchange].pools[unique_key_value].state[unique_key]
    #         == pool_info[unique_key]
    #     ][0]
    mgr.exchanges[exchange].pools[unique_key_value] = pool


def get_multicall_contract_for_exchange(mgr: Any, exchange: str) -> str:
    """
    Get the multicall contract for the exchange.

    Parameters
    ----------
    mgr : Any
        Manager object containing configuration and pool data.
    exchange : str
        Name of the exchange.

    Returns
    -------
    str
        The multicall contract for the exchange.

    """
    if exchange == "bancor_v3":
        return mgr.pool_contracts[exchange][mgr.cfg.BANCOR_V3_NETWORK_INFO_ADDRESS]
    elif exchange == "bancor_pol":
        return mgr.pool_contracts[exchange][mgr.cfg.BANCOR_POL_ADDRESS]
    elif exchange == "carbon_v1":
        return mgr.pool_contracts[exchange][mgr.cfg.CARBON_CONTROLLER_ADDRESS]
    elif exchange == "balancer":
        return mgr.pool_contracts[exchange][mgr.cfg.BALANCER_VAULT_ADDRESS]
    else:
        raise ValueError(f"Exchange {exchange} not supported.")


def multicall_every_iteration(current_block: int, mgr: Any):
    """
    For each exchange that supports Multicall, use multicall to update the state of the pools on every search iteration.

    Parameters
    ----------
    current_block : int
        The current block.
    mgr : Any
        Manager object containing configuration and pool data.

    """
    multicallable_exchanges = [
        exchange
        for exchange in mgr.cfg.MULTICALLABLE_EXCHANGES
        if exchange in mgr.exchanges
    ]
    multicallable_pool_rows = [
        list(set(get_pools_for_exchange(mgr=mgr, exchange=ex_name)))
        for ex_name in multicallable_exchanges
        if ex_name in mgr.exchanges
    ]

    for idx, exchange in enumerate(multicallable_exchanges):
        multicall_contract = get_multicall_contract_for_exchange(mgr, exchange)
        rows_to_update = multicallable_pool_rows[idx]
        multicall_helper(
            exchange, rows_to_update, multicall_contract, mgr, current_block
        )
