"""
[DOC-TODO-short description of what the file does, max 80 chars]

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import asyncio
import os
import time

from glob import glob
from typing import Any, List, Dict, Tuple, Type, Callable

import nest_asyncio
import numpy as np
import pandas as pd
from pandas import DataFrame
from web3 import Web3
from web3.contract import AsyncContract

from fastlane_bot.config.constants import CARBON_V1_NAME
from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.events.async_utils import get_contract_chunks
from fastlane_bot.events.utils import update_pools_from_events
from fastlane_bot.events.pools.utils import get_pool_cid
from .interfaces.event import Event

nest_asyncio.apply()


async def _get_missing_tkn(mgr: Any, contract: AsyncContract, tkn: str) -> pd.DataFrame:
    """
    This function uses the contract object to get the token info for a given token.

    Args:
        contract(AsyncContract): The contract object
        tkn(str): The token address

    Returns:
        pd.DataFrame: The token info

    """
    try:
        symbol = await contract.functions.symbol().call()
    except Exception:
        symbol = None
    try:
        decimals = await contract.functions.decimals().call()
    except Exception:
        decimals = None
    try:
        df = pd.DataFrame(
            [
                {
                    "address": tkn,
                    "symbol": symbol,
                    "decimals": decimals,
                }
            ]
        )
    except Exception as e:
        mgr.cfg.logger.error(f"Failed to get token info for {tkn} {e}")
        df = pd.DataFrame(
            [
                {
                    "address": tkn,
                    "symbol": None,
                    "decimals": decimals,
                }
            ]
        )
    return df


async def _get_missing_tkns(mgr: Any, c: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    This function uses the contract object to get the token info for a given token.

    Args:
        c(List[Dict[str, Any]]): The contract object and token address

    Returns:
        pd.DataFrame: The token info
    """
    vals = await asyncio.wait_for(asyncio.gather(*[_get_missing_tkn(mgr, **args) for args in c]), timeout = 20 * 60)
    return pd.concat(vals)


async def _get_token_and_fee(mgr: Any, exchange_name: str, ex: Any, address: str, contract: AsyncContract, event: Event):
    """
    This function uses the exchange object to get the tokens and fee for a given pool.

    Args:
        ex(Any): The exchange object
        address(str): The pool address
        contract(AsyncContract): The contract object
        event(Event): The event object

    Returns:
        The tokens and fee info for the pool
    """
    try:
        anchor = None
        tkn0 = await ex.get_tkn0(address, contract, event=event)
        tkn1 = await ex.get_tkn1(address, contract, event=event)
        fee = await ex.get_fee(address, contract)
        if exchange_name == "bancor_v2":
            anchor = await ex.get_anchor(contract)
            for i in [0, 1]:
                connector_token = await ex.get_connector_tokens(contract, i)
                if connector_token != mgr.cfg.BNT_ADDRESS:
                    break

            if tkn0 == mgr.cfg.BNT_ADDRESS:
                tkn1 = connector_token
            elif tkn1 == mgr.cfg.BNT_ADDRESS:
                tkn0 = connector_token

        strategy_id = 0 if not ex.is_carbon_v1_fork else str(event.args["id"])
        pool_info = {
            "exchange_name": exchange_name,
            "address": address,
            "tkn0_address": tkn0,
            "tkn1_address": tkn1,
            "pair_name": f"{tkn0}/{tkn1}",
            "fee": fee,
            "strategy_id": strategy_id
        }
        carbon_v1_forks = [exchange_name] if (ex.is_carbon_v1_fork or exchange_name == CARBON_V1_NAME) else []
        cid = get_pool_cid(pool_info, carbon_v1_forks=carbon_v1_forks)
        return exchange_name, address, tkn0, tkn1, fee, cid, strategy_id, anchor
    except Exception as e:
        mgr.cfg.logger.info(f"Failed to get tokens and fee for {address} {exchange_name} {e}")
        return exchange_name, address, None, None, None, None, None, anchor


async def _get_tokens_and_fees(mgr: Any, c: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    This function uses the asyncio gather function to call the _get_token_and_fee function for a list of pools.
    """
    vals = await asyncio.wait_for(asyncio.gather(*[_get_token_and_fee(mgr, **args) for args in c]), timeout = 20 * 60)
    return pd.DataFrame(
        vals,
        columns=[
            "exchange_name",
            "address",
            "tkn0_address",
            "tkn1_address",
            "fee",
            "cid",
            "strategy_id",
            "anchor",
        ],
    )


def _get_pool_info(
        mgr: Any,
        pool: pd.Series,
        current_block: int,
        tkn0: Dict[str, Any],
        tkn1: Dict[str, Any],
        pool_data_keys: frozenset,
) -> Dict[str, Any]:
    fee_raw = eval(str(pool["fee"]))
    pool_info = {
        "exchange_name": pool["exchange_name"],
        "address": pool["address"],
        "tkn0_address": pool["tkn0_address"],
        "tkn1_address": pool["tkn1_address"],
        "fee": fee_raw[0],
        "fee_float": fee_raw[1],
        "blockchain": mgr.blockchain,
        "anchor": pool["anchor"],
        "exchange_id": mgr.cfg.EXCHANGE_IDS[pool["exchange_name"]],
        "last_updated_block": current_block,
        "tkn0_symbol": tkn0["symbol"],
        "tkn0_decimals": tkn0["decimals"],
        "tkn1_symbol": tkn1["symbol"],
        "tkn1_decimals": tkn1["decimals"],
        "pair_name": tkn0["address"] + "/" + tkn1["address"],
        "strategy_id": pool["strategy_id"],
    }
    if len(pool_info["pair_name"].split("/")) != 2:
        raise Exception(f"pair_name is not valid for {pool_info}")

    pool_info["cid"] = get_pool_cid(pool_info, carbon_v1_forks=mgr.cfg.CARBON_V1_FORKS)

    # timestamp
    pool_info["last_updated"] = time.time()

    for key in pool_data_keys:
        if key not in pool_info.keys():
            pool_info[key] = np.nan

    return pool_info


def _get_new_pool_data(
        mgr: Any,
        current_block: int,
        tokens_and_fee_df: pd.DataFrame,
        tokens_df: pd.DataFrame,
) -> List[Dict]:
    # Convert tokens_df to a dictionary keyed by address for faster access
    tokens_dict = tokens_df.set_index("address").to_dict(orient="index")

    # Convert pool_data_keys to a frozenset for faster containment checks
    all_keys = set()
    for pool in mgr.pool_data:
        all_keys.update(pool.keys())
    pool_data_keys: frozenset = frozenset(all_keys)
    new_pool_data: List[Dict] = []
    for idx, pool in tokens_and_fee_df.iterrows():
        tkn0 = tokens_dict.get(pool["tkn0_address"])
        tkn1 = tokens_dict.get(pool["tkn1_address"])
        if not tkn0 or not tkn1:
            mgr.cfg.logger.info(
                f"tkn0 or tkn1 not found: {pool['tkn0_address']}, {pool['tkn1_address']}, {pool['address']} "
            )
            continue
        tkn0["address"] = pool["tkn0_address"]
        tkn1["address"] = pool["tkn1_address"]
        pool_info = _get_pool_info(mgr, pool, current_block, tkn0, tkn1, pool_data_keys)
        new_pool_data.append(pool_info)
    return new_pool_data


def _get_token_contracts(
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
            "contract": mgr.w3_async.eth.contract(address=tkn, abi=ERC20_ABI),
            "tkn": tkn,
        }
        for tkn in missing_tokens
        if tkn is not None and str(tkn) != "nan"
    )
    mgr.cfg.logger.debug(
        f"[async_event_update_utils._get_token_contracts] successful token contracts: {len(contracts) - len(failed_contracts)} of {len(contracts)} "
    )
    return contracts, tokens_df


def _process_contract_chunks(
        mgr: Any,
        base_filename: str,
        chunks: List[Any],
        dirname: str,
        filename: str,
        subset: List[str],
        func: Callable,
        df_combined: pd.DataFrame = None
) -> pd.DataFrame:
    lst = []
    # write chunks to csv
    for idx, chunk in enumerate(chunks):
        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(func(mgr, chunk))
        if not mgr.read_only:
            df.to_csv(f"{dirname}/{base_filename}{idx}.csv", index=False)
        else:
            lst.append(df)

    filepaths = glob(f"{dirname}/*.csv")

    if not mgr.read_only:
        # concatenate and deduplicate

        if filepaths:
            df_orig = df_combined.copy() if df_combined is not None else None
            df_combined = pd.concat([pd.read_csv(filepath) for filepath in filepaths])
            df_combined = (
                pd.concat([df_orig, df_combined]) if df_orig is not None else df_combined
            )
            df_combined = df_combined.drop_duplicates(subset=subset)
            df_combined.to_csv(filename, index=False)
            # clear temp dir
            for filepath in filepaths:
                try:
                    os.remove(filepath)
                except Exception as e:
                    mgr.cfg.logger.error(f"Failed to remove {filepath} {e}??? This is spooky...")
    else:
        if lst:
            dfs = pd.concat(lst)
            dfs = dfs.drop_duplicates(subset=subset)
            if df_combined is not None:
                df_combined = pd.concat([df_combined, dfs])
            else:
                df_combined = dfs

    return df_combined


def _get_pool_contracts(mgr: Any) -> List[Dict[str, Any]]:
    contracts = []
    for add, en, event, key, value in mgr.pools_to_add_from_contracts:
        exchange_name = mgr.exchange_name_from_event(event)
        ex = mgr.exchanges[exchange_name]
        abi = ex.get_abi()
        address = event.address
        contracts.append(
            {
                "exchange_name": exchange_name,
                "ex": ex,
                "address": address,
                "contract": mgr.w3_async.eth.contract(address=address, abi=abi),
                "event": event,
            }
        )
    return contracts


def async_update_pools_from_contracts(mgr: Any, current_block: int):
    dirname = "temp"

    if not mgr.read_only:
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    start_time = time.time()
    # deplicate pool data

    orig_num_pools_in_data = len(mgr.pool_data)
    mgr.cfg.logger.info("Async process now updating pools from contracts...")

    all_events = [
        event
        for address, exchange_name, event, key, value in mgr.pools_to_add_from_contracts
    ]

    # split contracts into chunks of 1000
    contracts = _get_pool_contracts(mgr)
    chunks = get_contract_chunks(contracts)
    tokens_and_fee_df = _process_contract_chunks(
        mgr=mgr,
        base_filename="tokens_and_fee_df_",
        chunks=chunks,
        dirname=dirname,
        filename="tokens_and_fee_df.csv",
        subset=["exchange_name", "address", "cid", "strategy_id", "tkn0_address", "tkn1_address"],
        func=_get_tokens_and_fees
    )

    contracts, tokens_df = _get_token_contracts(mgr, tokens_and_fee_df)
    tokens_df = _process_contract_chunks(
        mgr=mgr,
        base_filename="missing_tokens_df_",
        chunks=get_contract_chunks(contracts),
        dirname=dirname,
        filename="missing_tokens_df.csv",
        subset=["address"],
        func=_get_missing_tkns,
        df_combined=pd.read_csv(f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv")
    )
    tokens_df["symbol"] = (
        tokens_df["symbol"]
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )
    if not mgr.read_only:
        tokens_df.to_csv(
            f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv", index=False
        )
    tokens_df["address"] = tokens_df["address"].apply(
        lambda x: Web3.to_checksum_address(x)
    )
    tokens_df = tokens_df.drop_duplicates(subset=["address"])

    new_pool_data = _get_new_pool_data(
        mgr, current_block, tokens_and_fee_df, tokens_df
    )

    if len(new_pool_data) == 0:
        mgr.cfg.logger.info("No pools found in contracts")
        return

    new_pool_data_df = pd.DataFrame(new_pool_data).sort_values(
        "last_updated_block", ascending=False
    )

    new_pool_data_df = new_pool_data_df.dropna(
        subset=[
            "pair_name",
            "exchange_name",
            "fee",
            "tkn0_symbol",
            "tkn1_symbol",
            "tkn0_decimals",
            "tkn1_decimals",
        ]
    )

    if new_pool_data_df.empty:
        mgr.cfg.logger.info("No valid pools found in contracts")
        return

    new_pool_data_df["descr"] = (
            new_pool_data_df["exchange_name"]
            + " "
            + new_pool_data_df["pair_name"]
            + " "
            + new_pool_data_df["fee"].astype(str)
    )

    new_pool_data_dict = new_pool_data_df.to_dict(orient="records")

    new_pool_data_df["cid"] = [
        get_pool_cid(row, carbon_v1_forks=mgr.cfg.CARBON_V1_FORKS)
        for row in new_pool_data_dict
    ]

    # print duplicate cid rows
    duplicate_cid_rows = new_pool_data_df[new_pool_data_df.duplicated(subset=["cid"])]

    new_pool_data_df = (
        new_pool_data_df.sort_values("last_updated_block", ascending=False)
        .drop_duplicates(subset=["cid"])
        .set_index("cid")
    )

    duplicate_new_pool_ct = len(duplicate_cid_rows)

    if len(mgr.pool_data) > 0:
        all_pools_df = (
            pd.DataFrame(mgr.pool_data)
            .sort_values("last_updated_block", ascending=False)
            .drop_duplicates(subset=["cid"])
            .set_index("cid")
        )

        new_pool_data_df = new_pool_data_df[all_pools_df.columns]

        # add new_pool_data to pool_data, ensuring no duplicates
        all_pools_df.update(new_pool_data_df, overwrite=True)

        new_pool_data_df = new_pool_data_df[
            ~new_pool_data_df.index.isin(all_pools_df.index)
        ]
        all_pools_df = pd.concat([all_pools_df, new_pool_data_df])
    else:
        all_pools_df = new_pool_data_df

    all_pools_df[["tkn0_decimals", "tkn1_decimals"]] = (
        all_pools_df[["tkn0_decimals", "tkn1_decimals"]].fillna(0).astype(int)
    )
    all_pools = (
        all_pools_df.sort_values("last_updated_block", ascending=False)
        .reset_index()
        .to_dict(orient="records")
    )

    mgr.pool_data = all_pools
    new_num_pools_in_data = len(mgr.pool_data)
    new_pools_added = new_num_pools_in_data - orig_num_pools_in_data

    mgr.cfg.logger.debug(
        f"[async_event_update_utils.async_update_pools_from_contracts] new_pools_added: {new_pools_added}")
    mgr.cfg.logger.debug(
        f"[async_event_update_utils.async_update_pools_from_contracts] orig_num_pools_in_data: {orig_num_pools_in_data}")
    mgr.cfg.logger.debug(
        f"[async_event_update_utils.async_update_pools_from_contracts] duplicate_new_pool_ct: {duplicate_new_pool_ct}")
    mgr.cfg.logger.debug(
        f"[async_event_update_utils.async_update_pools_from_contracts] pools_to_add_from_contracts: {len(mgr.pools_to_add_from_contracts)}"
    )
    mgr.cfg.logger.debug(
        f"[async_event_update_utils.async_update_pools_from_contracts] final pool_data ct: {len(mgr.pool_data)}")
    mgr.cfg.logger.debug(
        f"[async_event_update_utils.async_update_pools_from_contracts] compare {new_pools_added + duplicate_new_pool_ct},{len(mgr.pools_to_add_from_contracts)}"
    )

    # update the pool_data from events
    update_pools_from_events(-1, mgr, all_events)

    mgr.cfg.logger.info(
        f"Async Updating pools from contracts took {(time.time() - start_time):0.4f} seconds"
    )