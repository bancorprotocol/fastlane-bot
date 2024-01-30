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

from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.events.async_utils import get_contract_chunks
from fastlane_bot.events.utils import update_pools_from_events

nest_asyncio.apply()


async def get_missing_tkn(contract: AsyncContract, tkn: str) -> pd.DataFrame:
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
        cfg.logger.error(f"Failed to get token info for {tkn} {e}")
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


async def main_get_missing_tkn(c: List[Dict[str, Any]]) -> pd.DataFrame:
    vals = await asyncio.wait_for(
        asyncio.gather(*[get_missing_tkn(**args) for args in c]), timeout=20 * 60
    )
    return pd.concat(vals)


async def get_token_and_fee(
        exchange_name: str, ex: Any, address: str, contract: AsyncContract, event: Any
) -> Tuple[str, str, str, str, str, int or None, str or None] or Tuple[
    str, str, None, None, None, None, None
]:
    try:
        anchor = None
        tkn0 = await ex.get_tkn0(address, contract, event=event)
        tkn1 = await ex.get_tkn1(address, contract, event=event)
        fee = await ex.get_fee(address, contract)
        if exchange_name == "bancor_v2":
            anchor = await ex.get_anchor(contract)
            for i in [0, 1]:
                connector_token = await ex.get_connector_tokens(contract, i)
                if connector_token != "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C":
                    break

            if tkn0 == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C":
                tkn1 = connector_token
            elif tkn1 == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C":
                tkn0 = connector_token
            # tkn0 = (
            #     connector_token
            #     if tkn0 != "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
            #     and connector_token != "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
            #     else tkn0
            # )
            # tkn1 = (
            #     connector_token
            #     if tkn1 != "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
            #     and connector_token != "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
            #     else tkn1
            # )
            # if address in [
            #     "0x8df51A9714aE6357a5B829CC8d677b43D7e8BD53",
            #     "0x8df51A9714aE6357a5B829CC8d677b43D7e8BD53",
            #     "0x079cA3f710599739a22673c2856202F90D3A8806",
            # ]:
            #     print(
            #         f"\n#2 connector_token: {connector_token}, anchor: {anchor}, tkn0: {tkn0}, tkn1: {tkn1}"
            #     )
            #     raise Exception("test")
        cid = str(event["args"]["id"]) if exchange_name == "carbon_v1" else None

        return exchange_name, address, tkn0, tkn1, fee, cid, anchor
    except Exception as e:
        cfg.logger.info(
            f"Failed to get tokens and fee for {address} {exchange_name} {e}"
        )
        return exchange_name, address, None, None, None, None, anchor


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
            "anchor",
        ],
    )


# def get_tkn_key(t0_symbol: str, tkn0_address: str, key_digits: int = 4) -> str:
#     return f"{t0_symbol}-{tkn0_address[-key_digits:]}"


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
        "pair_name": tkn0["address"] + "/" + tkn1["address"]
    }
    if len(pool_info["pair_name"].split("/")) != 2:
        raise Exception(f"pair_name is not valid for {pool_info}")
    pool_info["descr"] = mgr.pool_descr_from_info(pool_info)
    pool_info["cid"] = (
        mgr.cfg.w3.keccak(text=f"{pool_info['descr']}").hex()
        if pool_info["exchange_name"] != "carbon_v1"
        else str(pool["cid"])
    )

    # timestamp
    pool_info["last_updated"] = time.time()

    for key in pool_data_keys:
        if key not in pool_info.keys():
            pool_info[key] = np.nan

    return pool_info


def sanitize_token_symbol(token_symbol: str, token_address: str, read_only: bool) -> str:
    """
    This function ensures token symbols are compatible with the bot's data structures.
    If a symbol is not compatible with Dataframes or CSVs, this function will return the token's address.

    :param token_symbol: the token's symbol
    :param token_address: the token's address
    :param read_only: bool indicating whether the bot is running in read_only mode

    returns: str
    """
    sanitization_path = os.path.normpath("fastlane_bot/data/data_sanitization_center/sanitary_data.csv")
    try:
        if not read_only:
            token_pd = pd.DataFrame([{"symbol": token_symbol}], columns=["symbol"])
            token_pd.to_csv(sanitization_path)
        return token_symbol
    except Exception:
        return token_address


def add_token_info(
        pool_info: Dict[str, Any], tkn0: Dict[str, Any], tkn1: Dict[str, Any], read_only: bool
) -> Dict[str, Any]:
    print(f"called add_token_info")
    tkn0_symbol = tkn0["symbol"].replace("/", "_").replace("-", "_")
    tkn1_symbol = tkn1["symbol"].replace("/", "_").replace("-", "_")
    tkn0_symbol = sanitize_token_symbol(token_symbol=tkn0_symbol, token_address=tkn0["address"], read_only=read_only)
    tkn1_symbol = sanitize_token_symbol(token_symbol=tkn1_symbol, token_address=tkn1["address"], read_only=read_only)
    tkn0["symbol"] = tkn0_symbol
    tkn1["symbol"] = tkn1_symbol

    pool_info["tkn0_symbol"] = tkn0_symbol
    pool_info["tkn0_decimals"] = tkn0["decimals"]
    pool_info["tkn1_symbol"] = tkn1_symbol
    pool_info["tkn1_decimals"] = tkn1["decimals"]
    pool_info["pair_name"] = tkn0["address"] + "/" + tkn1["address"]

    if len(pool_info["pair_name"].split("/")) != 2:
        raise Exception(f"pair_name is not valid for {pool_info}")
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
    all_keys = set()
    for pool in mgr.pool_data:
        all_keys.update(pool.keys())
    if "last_updated_block" not in all_keys:
        all_keys.update("last_updated_block")
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
        pool_info = get_pool_info(pool, mgr, current_block, tkn0, tkn1, pool_data_keys)
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
            "contract": mgr.w3_async.eth.contract(address=tkn, abi=ERC20_ABI),
            "tkn": tkn,
        }
        for tkn in missing_tokens
        if tkn is not None and str(tkn) != "nan"
    )
    mgr.cfg.logger.debug(
        f"[async_event_update_utils.get_token_contracts] successful token contracts: {len(contracts) - len(failed_contracts)} of {len(contracts)} "
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
        read_only: bool = False,
) -> pd.DataFrame:
    lst = []
    # write chunks to csv
    for idx, chunk in enumerate(chunks):
        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(func(chunk))
        if not read_only:
            df.to_csv(f"{dirname}/{base_filename}{idx}.csv", index=False)
        else:
            lst.append(df)

    filepaths = glob(f"{dirname}/*.csv")

    if not read_only:
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
                    cfg.logger.error(f"Failed to remove {filepath} {e}??? This is spooky...")
    else:
        if lst:
            dfs = pd.concat(lst)
            dfs = dfs.drop_duplicates(subset=subset)
            if df_combined is not None:
                df_combined = pd.concat([df_combined, dfs])
            else:
                df_combined = dfs

    return df_combined


def get_pool_contracts(mgr: Any) -> List[Dict[str, Any]]:
    contracts = []
    for add, en, event, key, value in mgr.pools_to_add_from_contracts:
        exchange_name = mgr.exchange_name_from_event(event)
        ex = mgr.exchanges[exchange_name]
        abi = ex.get_abi()
        address = event["address"]
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
    contracts = get_pool_contracts(mgr)
    chunks = get_contract_chunks(contracts)
    tokens_and_fee_df = process_contract_chunks(
        base_filename="tokens_and_fee_df_",
        chunks=chunks,
        dirname=dirname,
        filename="tokens_and_fee_df.csv",
        subset=["exchange_name", "address", "cid", "tkn0_address", "tkn1_address"],
        func=main_get_tokens_and_fee,
        read_only=mgr.read_only,
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
        read_only=mgr.read_only,
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

    new_pool_data = get_new_pool_data(
        current_block, keys, mgr, tokens_and_fee_df, tokens_df
    )

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

    new_pool_data_df["descr"] = (
            new_pool_data_df["exchange_name"]
            + " "
            + new_pool_data_df["pair_name"]
            + " "
            + new_pool_data_df["fee"].astype(str)
    )

    # Initialize web3
    new_pool_data_df["cid"] = [
        cfg.w3.keccak(text=f"{row['descr']}").hex()
        if row["exchange_name"] not in mgr.cfg.CARBON_V1_FORKS
        else int(row['cid'])
        for index, row in new_pool_data_df.iterrows()
    ]

    # print duplicate cid rows
    duplicate_cid_rows = new_pool_data_df[new_pool_data_df.duplicated(subset=["cid"])]

    new_pool_data_df = (
        new_pool_data_df.sort_values("last_updated_block", ascending=False)
        .drop_duplicates(subset=["cid"])
        .set_index("cid")
    )

    duplicate_new_pool_ct = len(duplicate_cid_rows)

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
