import asyncio
import os
import time
from glob import glob
from typing import Any

import pandas as pd

from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.events.exchanges import exchange_factory
from fastlane_bot.events.utils import update_pools_from_events, parse_non_multicall_rows_to_update


async def get_missing_tkn(contract, tkn):
    try:
        # contract = async_w3.eth.contract(address=tkn, abi=ERC20_ABI)
        symbol = await contract.functions.symbol().call()
        decimals = await contract.functions.decimals().call()
        blockchain = "ethereum"
        df = pd.DataFrame([{
            "address": tkn,
            "key": symbol,
            "symbol": symbol,
            "decimals": decimals,
            "blockchain": blockchain
        }])
    except Exception as e:
        print(e)
        df = pd.DataFrame([{
            "address": tkn,
            "key": None,
            "symbol": None,
            "decimals": None,
            "blockchain": None
        }])
    return df

async def main_get_missing_tkn(c):
    vals = await asyncio.gather(
        *[
            get_missing_tkn(**args)
            for args in c
        ]
    )
    return pd.concat(vals)



async def get_token_and_fee(exchange_name, ex, address, contract, event, key, value):
    try:
        tkn0 = await ex.get_tkn0(
            address, contract, event=None
        )
        tkn1 = await ex.get_tkn1(
            address, contract, event=None
        )
        fee = await ex.get_fee(address, contract)
        return exchange_name, address, tkn0, tkn1, fee
    except Exception as e:
        print(e)
        return exchange_name, address, None, None, None


async def main_get_tokens_and_fee(c):
    vals = await asyncio.gather(
        *[
            get_token_and_fee(**args)
            for args in c
        ]
    )
    return pd.DataFrame(vals, columns=["exchange_name", "address", "tkn0_address", "tkn1_address", "fee"])


def async_update_pools_from_contracts(mgr):
    start_time = time.time()
    mgr.cfg.logger.info("Async Updating pools from contracts")
    key_digits = 4
    abis = {}
    exchanges = {}
    for exchange in mgr.exchanges:
        exchanges[exchange] = exchange_factory.get_exchange(exchange)
        abis[exchange] = exchanges[exchange].get_abi()

    all_events = [
        event
        for address, exchange_name, event, key, value in mgr.pools_to_add_from_contracts
    ]

    contracts = [
        {
            'exchange_name': exchange_name,
            'ex': exchange_factory.get_exchange(exchange_name),
            'address': address,
            'contract': mgr.async_w3.eth.contract(address=address, abi=abis[exchange_name]),
            'event': event,
            'key': key,
            'value': value
        }
        for address, exchange_name, event, key, value in mgr.pools_to_add_from_contracts
    ]

    # split contracts into chunks of 1000
    chunks = [contracts[i:i + 1000] for i in range(0, len(contracts), 1000)]
    dirname = 'temp'
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    for idx, chunk in enumerate(chunks):
        print(idx, len(chunk))
        loop = asyncio.get_event_loop()
        tokens_and_fee_df = loop.run_until_complete(main_get_tokens_and_fee(chunk))
        tokens_and_fee_df.to_csv(f"{dirname}/tokens_and_fee_df_{idx}.csv")
        loop.close()

    filepaths = glob(f"{dirname}/*.csv")
    pool_tokens_and_fee_df = pd.concat([pd.read_csv(filepath) for filepath in filepaths])
    pool_tokens_and_fee_df = pool_tokens_and_fee_df.drop_duplicates(subset=["exchange_name", "address"])
    pool_tokens_and_fee_df.to_csv("pool_tokens_and_fee_df.csv")

    # clear temp dir
    for filepath in filepaths:
        os.remove(filepath)

    # for each token in the pools, check whether we have the token info in the tokens.csv static data, and ifr not,
    # add it
    tokens = pool_tokens_and_fee_df["tkn0_address"].tolist() + pool_tokens_and_fee_df["tkn1_address"].tolist()
    tokens = list(set(tokens))
    tokens_df = pd.read_csv(f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv")
    missing_tokens = [tkn for tkn in tokens if tkn not in tokens_df["address"].unique()]
    contracts = [
        {
            'contract': mgr.async_w3.eth.contract(address=str(tkn), abi=ERC20_ABI),
            'tkn': tkn,
        }
        for tkn in missing_tokens
        if tkn is not None
        and str(tkn) != 'nan'

    ]

    chunks = [contracts[i:i + 1000] for i in range(0, len(contracts), 1000)]

    for idx, chunk in enumerate(chunks):
        print(idx, len(chunk))
        loop = asyncio.get_event_loop()
        missing_tokens_df = loop.run_until_complete(main_get_missing_tkn(chunk))
        loop.close()
        missing_tokens_df.to_csv(f"{dirname}/missing_tokens_df_{idx}.csv")

    filepaths = glob(f"{dirname}/*.csv")
    if filepaths:
        missing_tokens_df = pd.concat([pd.read_csv(filepath) for filepath in filepaths])
        missing_tokens_df = missing_tokens_df.drop_duplicates(subset=["address"])
        missing_tokens_df.to_csv("missing_tokens_df.csv")

        # add missing tokens to tokens.csv
        tokens_df = pd.concat([tokens_df, missing_tokens_df])
        tokens_df = tokens_df.drop_duplicates(subset=["address"])
        tokens_df.to_csv(f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv", index=False)

    # create pool_data entry for each pool_tokens_and_fee_df by combining the tokens_df info with the
    # tokens_and_fee_df info
    pool_data_keys = mgr.pool_data[0].keys()
    new_pool_data = []

    for idx, pool in pool_tokens_and_fee_df.iterrows():
        tkn0 = tokens_df[tokens_df["address"] == pool["tkn0_address"]].to_dict(orient="records")
        tkn1 = tokens_df[tokens_df["address"] == pool["tkn1_address"]].to_dict(orient="records")
        if not tkn0 or not tkn1:
            continue
        mgr.cfg.logger.info(f"pool: {pool}, {pool['tkn0_address']}")
        mgr.cfg.logger.info(f"tkn0: {tkn0}")
        def get_tkn_key(t0_symbol, tkn0_address, key_digits):
            return f"{t0_symbol}-{tkn0_address[-key_digits:]}"

        def pair_name(t0_symbol, tkn0_address, t1_symbol, tkn1_address, key_digits):
            return f"{t0_symbol}-{tkn0_address[-key_digits:]}/{t1_symbol}-{tkn1_address[-key_digits:]}"

        pool_info = {
            "exchange_name": pool["exchange_name"],
            "address": pool["address"],
            "tkn0_address": pool["tkn0_address"],
            "tkn1_address": pool["tkn1_address"],
            "fee": pool["fee"],
            "fee_float": float(pool["fee"] / 1e6),
            "tkn0_symbol": tkn0["symbol"],
            "tkn0_decimals": tkn0["decimals"],
            "tkn0_key": get_tkn_key(tkn0["symbol"], tkn0["address"], key_digits),
            "tkn1_symbol": tkn1["symbol"],
            "tkn1_decimals": tkn1["decimals"],
            "tkn1_key": get_tkn_key(tkn1["symbol"], tkn1["address"], key_digits),
            "pair_name": pair_name(tkn0["symbol"], tkn0["address"], tkn1["symbol"], tkn1["address"], key_digits),
            "blockchain": mgr.blockchain,
            "anchor": None,
        }
        pool_info["descr"] = mgr.pool_descr_from_info(pool_info)
        pool_info["cid"] = mgr.cfg.w3.keccak(text=f"{pool_info['descr']}").hex()

        # add missing keys to dicts
        for key in pool_data_keys:
            if key not in pool_info:
                pool_info[key] = None
        new_pool_data.append(pool_info)

    # add new_pool_data to pool_data
    mgr.pool_data = new_pool_data + mgr.pool_data

    # update the pool_data from events
    update_pools_from_events(-1, mgr, all_events)

    mgr.cfg.logger.info(f"Async Updating pools from contracts took {time.time() - start_time} seconds")


async def async_handle_main_backdate_from_contracts(mgr, pool_info, contract):
    pool = mgr.get_or_init_pool(pool_info)
    params = await pool.update_from_contract(
        contract,
        tenderly_fork_id=mgr.tenderly_fork_id,
        w3_tenderly=mgr.w3_tenderly,
        w3=mgr.async_w3,
    )
    for key, value in params.items():
        pool_info[key] = value
    return pool_info


async def async_main_backdate_from_contracts(c):
    return await asyncio.gather(*[get_token_and_fee(**args) for args in c])


def async_backdate_from_contracts(mgr, rows, current_block, last_block, start_block):
    abis = {}
    exchanges = {}
    for exchange in mgr.exchanges:
        exchanges[exchange] = exchange_factory.get_exchange(exchange)
        abis[exchange] = exchanges[exchange].get_abi()

    contracts = [
        {
            'exchange_name': mgr.pool_data[idx]['exchange_name'],
            'ex': exchange_factory.get_exchange(mgr.pool_data[idx]['exchange_name']),
            'address': mgr.pool_data[idx]['address'],
            'contract': mgr.async_w3.eth.contract(address=mgr.pool_data[idx]['address'],
                                                  abi=abis[mgr.pool_data[idx]['exchange_name']]),
            'pool_info': mgr.pool_data[idx],
            'block_number': current_block,
        }
        for idx in rows
    ]

    loop = asyncio.get_event_loop()
    updated_pool_info = loop.run_until_complete(async_main_backdate_from_contracts(contracts))
    loop.close()

    for idx in rows:
        pool_data = mgr.pool_data[idx]
        updated_pool_data = [pool for pool in updated_pool_info if pool["address"] == pool_data["address"]][0]
        mgr.pool_data[idx] = updated_pool_data


def async_handle_initial_iteration(
        backdate_pools: bool,
        last_block: int,
        mgr: Any,
        start_block: int,
        current_block: int,
):
    if last_block == 0:
        non_multicall_rows_to_update = mgr.get_rows_to_update(start_block)

        if backdate_pools:
            # Remove duplicates
            non_multicall_rows_to_update = list(set(non_multicall_rows_to_update))

            # Parse the rows to update
            other_pool_rows = parse_non_multicall_rows_to_update(
                mgr, non_multicall_rows_to_update
            )

            for rows in [other_pool_rows]:
                mgr.cfg.logger.info(
                    f"Backdating {len(rows)} pools from {start_block} to {current_block}"
                )
                start_time = time.time()
                async_backdate_from_contracts(
                    mgr,
                    rows,
                    current_block=current_block,
                    last_block=last_block,
                    start_block=start_block,
                )
                mgr.cfg.logger.info(
                    f"Backdating {len(rows)} pools took {time.time() - start_time} seconds"
                )
