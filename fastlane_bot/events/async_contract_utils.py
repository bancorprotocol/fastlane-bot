import asyncio
import os
import time
from glob import glob
from typing import Any, List, Dict, Tuple, Type, Callable

import pandas as pd
from pandas import DataFrame
from web3.contract import AsyncContract

from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.events.async_utils import get_contract_chunks, w3_async
from fastlane_bot.events.exchanges import exchange_factory
from fastlane_bot.events.utils import update_pools_from_events, write_pool_data_to_disk


async def get_missing_tkn(contract: AsyncContract, tkn: str) -> pd.DataFrame:
    try:
        symbol = await contract.functions.symbol().call()
        name = symbol
        decimals = await contract.functions.decimals().call()
        blockchain = "ethereum"
        key = f"{name}-{tkn[-4:]}"
        df = pd.DataFrame(
            [
                {
                    "address": tkn,
                    "name": symbol,
                    "symbol": symbol,
                    "decimals": decimals,
                    "blockchain": blockchain,
                    "key": key,
                }
            ]
        )
    except Exception as e:
        cfg.logger.error(f"Failed to get token info for {tkn} {e}")
        df = pd.DataFrame(
            [
                {
                    "address": tkn,
                    "name": None,
                    "symbol": None,
                    "decimals": None,
                    "blockchain": None,
                    "key": None,
                }
            ]
        )
    return df


async def main_get_missing_tkn(c: List[Dict[str, Any]]) -> pd.DataFrame:
    vals = await asyncio.wait_for(
        asyncio.gather(*[get_missing_tkn(**args) for args in c]), timeout=20 * 60
    )
    return pd.concat(vals)


async def get_token_and_fee(
    exchange_name: str, ex: Any, address: str, contract: AsyncContract, event: Any
) -> Tuple[str, str, str, str, str, int or None] or Tuple[
    str, str, None, None, None, None
]:
    try:
        tkn0 = await ex.get_tkn0(address, contract, event=event)
        tkn1 = await ex.get_tkn1(address, contract, event=event)
        fee = await ex.get_fee(address, contract)
        cid = str(event["args"]["id"]) if exchange_name == "carbon_v1" else None
        return exchange_name, address, tkn0, tkn1, fee, cid
    except Exception as e:
        cfg.logger.info(
            f"Failed to get tokens and fee for {address} {exchange_name} {e}"
        )
        return exchange_name, address, None, None, None, None


async def main_get_tokens_and_fee(c: List[Dict[str, Any]]) -> pd.DataFrame:
    vals = await asyncio.wait_for(
        asyncio.gather(*[get_token_and_fee(**args) for args in c]), timeout=20 * 60
    )
    return pd.DataFrame(
        vals,
        columns=[
            "exchange_name",
            "address",
            "tkn0_address",
            "tkn1_address",
            "fee",
            "cid",
        ],
    )


def get_tkn_key(t0_symbol: str, tkn0_address: str, key_digits: int = 4) -> str:
    return f"{t0_symbol}-{tkn0_address[-key_digits:]}"


def pair_name(
    t0_symbol: str,
    tkn0_address: str,
    t1_symbol: str,
    tkn1_address: str,
    key_digits: int = 4,
) -> str:
    return f"{t0_symbol}-{tkn0_address[-key_digits:]}/{t1_symbol}-{tkn1_address[-key_digits:]}"


def get_pool_info(
    pool: pd.Series,
    mgr: Any,
    current_block: int,
    tkn0: Dict[str, Any],
    tkn1: Dict[str, Any],
) -> Dict[str, Any]:
    fee_raw = eval(pool["fee"])
    pool_info = {
        "exchange_name": pool["exchange_name"],
        "address": pool["address"],
        "tkn0_address": pool["tkn0_address"],
        "tkn1_address": pool["tkn1_address"],
        "tkn0_balance": pool["tkn0_balance"] if "tkn0_balance" in pool else None,
        "tkn1_balance": pool["tkn1_balance"] if "tkn1_balance" in pool else None,
        "fee": fee_raw[0],
        "fee_float": fee_raw[1],
        "blockchain": mgr.blockchain,
        "anchor": None,
        "exchange_id": mgr.cfg.EXCHANGE_IDS[pool["exchange_name"]],
        "last_updated_block": current_block,
    }
    pool_info = add_token_info(pool_info, tkn0, tkn1)
    pool_info["descr"] = mgr.pool_descr_from_info(pool_info)
    pool_info["cid"] = (
        mgr.cfg.w3.keccak(text=f"{pool_info['descr']}").hex()
        if pool_info["exchange_name"] != "carbon_v1"
        else str(pool["cid"])
    )
    return pool_info


def add_token_info(
    pool_info: Dict[str, Any], tkn0: Dict[str, Any], tkn1: Dict[str, Any]
) -> Dict[str, Any]:
    pool_info["tkn0_symbol"] = tkn0["symbol"]
    pool_info["tkn0_decimals"] = tkn0["decimals"]
    pool_info["tkn0_key"] = get_tkn_key(tkn0["symbol"], tkn0["address"])
    pool_info["tkn1_symbol"] = tkn1["symbol"]
    pool_info["tkn1_decimals"] = tkn1["decimals"]
    pool_info["tkn1_key"] = get_tkn_key(tkn1["symbol"], tkn1["address"])
    pool_info["pair_name"] = pair_name(
        tkn0["symbol"], tkn0["address"], tkn1["symbol"], tkn1["address"]
    )
    return pool_info


def add_missing_keys(
    pool_info: Dict[str, Any], pool_data_keys: frozenset, keys: List[str]
) -> Dict[str, Any]:
    for key in pool_data_keys:
        if key in pool_info:
            if key in keys and (pool_info[key] is None or str(pool_info[key]) == "nan"):
                pool_info[key] = 0
        else:
            pool_info[key] = 0 if key in keys else None
    return pool_info


def get_new_pool_data(
    current_block: int,
    keys: List[str],
    mgr: Any,
    tokens_and_fee_df: pd.DataFrame,
    tokens_df: pd.DataFrame,
) -> List[Dict]:
    # Convert tokens_df to a dictionary keyed by address for faster access
    tokens_dict = tokens_df.set_index("address").to_dict(orient="index")
    # Convert pool_data_keys to a frozenset for faster containment checks
    pool_data_keys: frozenset = frozenset(mgr.pool_data[0].keys())
    new_pool_data: List[Dict] = []
    for idx, pool in tokens_and_fee_df.iterrows():
        tkn0 = tokens_dict.get(pool["tkn0_address"])
        tkn0["address"] = pool["tkn0_address"]
        tkn1 = tokens_dict.get(pool["tkn1_address"])
        tkn1["address"] = pool["tkn1_address"]
        if not tkn0 or not tkn1:
            mgr.cfg.logger.info(
                f"tkn0 or tkn1 not found: {pool['tkn0_address']}, {pool['tkn1_address']}, {pool['address']} "
            )
            continue

        pool_info = add_missing_keys(
            get_pool_info(pool, mgr, current_block, tkn0, tkn1),
            pool_data_keys,
            keys,
        )
        new_pool_data.append(pool_info)
    return new_pool_data


def get_token_contracts(
    mgr: Any, tokens_and_fee_df: pd.DataFrame
) -> Tuple[
    List[Dict[str, Type[AsyncContract] or AsyncContract or Any] or None or Any],
    DataFrame,
]:
    # for each token in the pools, check whether we have the token info in the tokens.csv static data, and ifr not,
    # add it
    tokens = (
        tokens_and_fee_df["tkn0_address"].tolist()
        + tokens_and_fee_df["tkn1_address"].tolist()
    )
    tokens = list(set(tokens))
    tokens_df = pd.read_csv(
        f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv"
    )
    missing_tokens = [tkn for tkn in tokens if tkn not in tokens_df["address"].tolist()]
    contracts = []
    failed_contracts = []
    contracts.extend(
        {
            "contract": w3_async.eth.contract(address=tkn, abi=ERC20_ABI),
            "tkn": tkn,
        }
        for tkn in missing_tokens
        if tkn is not None and str(tkn) != "nan"
    )
    mgr.cfg.logger.info(
        f"\n\n failed token contracts:{len(failed_contracts)}/{len(contracts)} "
    )
    return contracts, tokens_df


def process_contract_chunks(
    base_filename: str,
    chunks: List[Any],
    dirname: str,
    filename: str,
    subset: List[str],
    func: Callable,
    df_combined: pd.DataFrame = None,
) -> pd.DataFrame:
    # write chunks to csv
    for idx, chunk in enumerate(chunks):
        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(func(chunk))
        df.to_csv(f"{dirname}/{base_filename}{idx}.csv")

    # concatenate and deduplicate
    filepaths = glob(f"{dirname}/*.csv")
    if filepaths:
        df_orig = df_combined.copy() if df_combined is not None else None
        df_combined = pd.concat([pd.read_csv(filepath) for filepath in filepaths])
        df_combined = (
            pd.concat([df_orig, df_combined]) if df_orig is not None else df_combined
        )
        df_combined = df_combined.drop_duplicates(subset=subset)
        df_combined.to_csv(filename)

    # clear temp dir
    for filepath in filepaths:
        try:
            os.remove(filepath)
        except Exception as e:
            cfg.logger.error(f"Failed to remove {filepath} {e}??? This is spooky...")

    return df_combined


def get_pool_contracts(mgr: Any) -> List[Dict[str, Any]]:
    contracts = []
    for add, en, event, key, value in mgr.pools_to_add_from_contracts:
        exchange_name = mgr.exchange_name_from_event(event)
        ex = exchange_factory.get_exchange(exchange_name)
        abi = ex.get_abi()
        address = event["address"]
        contracts.append(
            {
                "exchange_name": exchange_name,
                "ex": exchange_factory.get_exchange(exchange_name),
                "address": address,
                "contract": w3_async.eth.contract(address=address, abi=abi),
                "event": event,
            }
        )
    return contracts


def async_update_pools_from_contracts(mgr: Any, current_block: int, logging_path):
    global cfg
    cfg = mgr.cfg
    dirname = "temp"
    keys = [
        "liquidity",
        "tkn0_balance",
        "tkn1_balance",
        "y_0",
        "y_1",
        "liquidity",
    ]
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    start_time = time.time()
    orig_num_pools_in_data = len(mgr.pool_data)
    mgr.cfg.logger.info("Async process now updating pools from contracts...")

    all_events = [
        event
        for address, exchange_name, event, key, value in mgr.pools_to_add_from_contracts
    ]

    # split contracts into chunks of 1000
    contracts = get_pool_contracts(mgr)
    chunks = get_contract_chunks(contracts)
    tokens_and_fee_df = process_contract_chunks(
        base_filename="tokens_and_fee_df_",
        chunks=chunks,
        dirname=dirname,
        filename="tokens_and_fee_df.csv",
        subset=["exchange_name", "address", "cid", "tkn0_address", "tkn1_address"],
        func=main_get_tokens_and_fee,
    )

    contracts, tokens_df = get_token_contracts(mgr, tokens_and_fee_df)
    tokens_df = process_contract_chunks(
        base_filename="missing_tokens_df_",
        chunks=get_contract_chunks(contracts),
        dirname=dirname,
        filename="missing_tokens_df.csv",
        subset=["address"],
        func=main_get_missing_tkn,
        df_combined=pd.read_csv(
            f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv"
        ),
    )

    new_pool_data = get_new_pool_data(
        current_block, keys, mgr, tokens_and_fee_df, tokens_df
    )

    # add new_pool_data to pool_data
    mgr.pool_data = new_pool_data + mgr.pool_data

    new_num_pools_in_data = len(mgr.pool_data)
    new_pools_added = new_num_pools_in_data - orig_num_pools_in_data
    if new_pools_added < len(mgr.pools_to_add_from_contracts):
        write_pool_data_to_disk(
            cache_latest_only=True,
            logging_path=logging_path,
            mgr=mgr,
            current_block=current_block,
        )
        mgr.cfg.logger.info(
            f"Failed. {len(mgr.pools_to_add_from_contracts) - new_pools_added} pools failed to update from events, "
            f"{len(mgr.pool_data)} total pools currently exist. "
            f"added {new_pools_added} pools from contracts."
        )

        # find the failed pools
        failed_pools = []
        for (
            address,
            exchange_name,
            event,
            key,
            value,
        ) in mgr.pools_to_add_from_contracts:
            # print(f"key: {key}, value: {value}")
            data_vals = (
                [pool["tkn0_address"] for pool in mgr.pool_data]
                + [pool["tkn1_address"] for pool in mgr.pool_data]
                + [pool["address"] for pool in mgr.pool_data]
                + [pool["anchor"] for pool in mgr.pool_data if pool["anchor"]]
                + [pool["cid"] for pool in mgr.pool_data]
            )
            if str(value) not in data_vals or exchange_name in [
                "sushiswap_v2",
                "pancakeswap_v2",
            ]:
                failed_pools.append((address, exchange_name, event, key, value))

        for pool in failed_pools:
            mgr.cfg.logger.info(f"\n\nFailed to update pool {pool}")

        raise Exception("Failed to update pools from contracts")

    # for address, exchange_name, event, key, value in mgr.pools_to_add_from_contracts:
    #     if exchange_name in ["sushiswap_v2", "pancakeswap_v2"]:
    #         mgr.cfg.logger.info(
    #             f"Skipping {exchange_name} pool {address} because it's not supported yet"
    #         )
    #         # update the pool_data from events
    #         update_pools_from_events(-1, mgr, [event])
    #         vals = [
    #             pool
    #             for pool in mgr.pool_data
    #             if pool["address"] == address and pool["exchange_name"] == exchange_name
    #         ]
    #         print(f"vals: {vals}")
    #         raise Exception("Not supported yet")

    # update the pool_data from events
    update_pools_from_events(-1, mgr, all_events)

    mgr.cfg.logger.info(
        f"Async Updating pools from contracts took {time.time() - start_time} seconds"
    )
