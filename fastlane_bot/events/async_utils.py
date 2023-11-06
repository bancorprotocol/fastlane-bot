import asyncio
import logging
import os
import time
from glob import glob
from typing import Any

import pandas as pd
from web3 import AsyncWeb3

from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.events.exchanges import exchange_factory, UniswapV2
from fastlane_bot.events.utils import update_pools_from_events, parse_non_multicall_rows_to_update

w3_async = AsyncWeb3(
    AsyncWeb3.AsyncHTTPProvider(f"https://eth-mainnet.alchemyapi.io/v2/{os.environ['WEB3_ALCHEMY_PROJECT_ID']}")
)


async def get_missing_tkn(contract, tkn):
    try:
        symbol = await contract.functions.symbol().call()
        name = symbol
        decimals = await contract.functions.decimals().call()
        blockchain = "ethereum"
        key = f"{name}-{tkn[-4:]}"
        df = pd.DataFrame([{
            "address": tkn,
            "name": symbol,
            "symbol": symbol,
            "decimals": decimals,
            "blockchain": blockchain,
            "key": key
        }])
    except Exception as e:
        print(e)
        df = pd.DataFrame([{
            "address": tkn,
            "name": None,
            "symbol": None,
            "decimals": None,
            "blockchain": None,
            "key": None
        }])
    return df


async def main_get_missing_tkn(c):
    vals = await asyncio.wait_for(asyncio.gather(
        *[
            get_missing_tkn(**args)
            for args in c
        ]
    ), timeout=20 * 60)
    return pd.concat(vals)


async def get_token_and_fee(exchange_name, ex, address, contract, event):
    try:
        tkn0 = await ex.get_tkn0(
            address, contract, event=event
        )
        tkn1 = await ex.get_tkn1(
            address, contract, event=event
        )
        fee = await ex.get_fee(address, contract)
        return exchange_name, address, tkn0, tkn1, fee
    except Exception as e:
        cfg.logger.info(f"Failed to get tokens and fee for {address} {exchange_name} {e}")
        return exchange_name, address, None, None, None


async def main_get_tokens_and_fee(c):
    vals = await asyncio.wait_for(asyncio.gather(
        *[
            get_token_and_fee(**args)
            for args in c
        ]
    ), timeout=20 * 60)
    return pd.DataFrame(vals, columns=["exchange_name", "address", "tkn0_address", "tkn1_address", "fee"])


def async_update_pools_from_contracts(mgr, current_block):
    global cfg
    cfg = mgr.cfg
    start_time = time.time()
    mgr.cfg.logger.info("Async process now updating pools from contracts...")
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

    contracts = []
    for add, en, event, key, value in mgr.pools_to_add_from_contracts:
        exchange_name = mgr.exchange_name_from_event(event)
        address = event['address']
        contracts.append({
            'exchange_name': exchange_name,
            'ex': exchange_factory.get_exchange(exchange_name),
            'address': address,
            'contract': w3_async.eth.contract(address=address, abi=abis[exchange_name]),
            'event': event
        })

    # split contracts into chunks of 1000
    chunks = [contracts[i:i + 1000] for i in range(0, len(contracts), 1000)]
    dirname = 'temp'
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    for idx, chunk in enumerate(chunks):
        print(f"Getting tokens and fee for chunk {idx} of {len(chunks)}")
        loop = asyncio.get_event_loop()
        tokens_and_fee_df = loop.run_until_complete(main_get_tokens_and_fee(chunk))
        tokens_and_fee_df.to_csv(f"{dirname}/tokens_and_fee_df_{idx}.csv")

    filepaths = glob(f"{dirname}/*.csv")
    if filepaths:
        print(f"Concatenating {len(filepaths)} tokens_and_fee_df_ files")
        tokens_and_fee_df = pd.concat([pd.read_csv(filepath) for filepath in filepaths])
        tokens_and_fee_df = tokens_and_fee_df.drop_duplicates(subset=["exchange_name", "address"])
        tokens_and_fee_df.to_csv("tokens_and_fee_df.csv")

    # clear temp dir
    for filepath in filepaths:
        os.remove(filepath)

    # for each token in the pools, check whether we have the token info in the tokens.csv static data, and ifr not,
    # add it
    tokens = tokens_and_fee_df["tkn0_address"].tolist() + tokens_and_fee_df["tkn1_address"].tolist()
    tokens = list(set(tokens))
    tokens_df = pd.read_csv(f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv")
    missing_tokens = [tkn for tkn in tokens if tkn not in tokens_df["address"].tolist()]
    contracts = []
    failed_contracts = []
    for tkn in missing_tokens:
        if tkn is None or str(tkn) == 'nan':
            continue

        contracts.append(
            {
                'contract': w3_async.eth.contract(address=tkn, abi=ERC20_ABI),
                'tkn': tkn,
            }
        )

    mgr.cfg.logger.info(f"\n\n failed token contracts:{len(failed_contracts)}/{len(contracts)} ")

    chunks = [contracts[i:i + 1000] for i in range(0, len(contracts), 1000)]

    for idx, chunk in enumerate(chunks):
        print(f"Getting missing tokens for chunk {idx} of {len(chunks)}")
        loop = asyncio.get_event_loop()
        missing_tokens_df = loop.run_until_complete(main_get_missing_tkn(chunk))
        missing_tokens_df.to_csv(f"{dirname}/missing_tokens_df_{idx}.csv")

    filepaths = glob(f"{dirname}/*.csv")
    if filepaths:
        print(f"Concatenating {len(filepaths)} missing_tokens_df_ files")
        missing_tokens_df = pd.concat([pd.read_csv(filepath) for filepath in filepaths])
        missing_tokens_df = missing_tokens_df.drop_duplicates(subset=["address"])
        missing_tokens_df.to_csv("missing_tokens_df.csv")

        # add missing tokens to tokens.csv
        tokens_df = pd.concat([tokens_df, missing_tokens_df])
        tokens_df = tokens_df.drop_duplicates(subset=["address"])
        tokens_df.to_csv(f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv", index=False)

    # clear temp dir
    for filepath in filepaths:
        os.remove(filepath)

    # create pool_data entry for each pool_tokens_and_fee_df by combining the tokens_df info with the
    # tokens_and_fee_df info
    pool_data_keys = mgr.pool_data[0].keys()
    new_pool_data = []

    for idx, pool in tokens_and_fee_df.iterrows():
        tkn0 = tokens_df[tokens_df["address"] == pool["tkn0_address"]].to_dict(orient="records")
        tkn1 = tokens_df[tokens_df["address"] == pool["tkn1_address"]].to_dict(orient="records")
        if not tkn0 or not tkn1:
            mgr.cfg.logger.info(
                f"tkn0 or tkn1 not found: {pool['tkn0_address']}, {pool['tkn1_address']}, {pool['address']} ")
            continue
        tkn0 = tkn0[0]
        tkn1 = tkn1[0]

        def get_tkn_key(t0_symbol, tkn0_address, key_digits):
            return f"{t0_symbol}-{tkn0_address[-key_digits:]}"

        def pair_name(t0_symbol, tkn0_address, t1_symbol, tkn1_address, key_digits):
            return f"{t0_symbol}-{tkn0_address[-key_digits:]}/{t1_symbol}-{tkn1_address[-key_digits:]}"

        fee_raw = eval(pool["fee"])
        pool_info = {
            "exchange_name": pool["exchange_name"],
            "address": pool["address"],
            "tkn0_address": pool["tkn0_address"],
            "tkn1_address": pool["tkn1_address"],
            "fee": fee_raw[0],
            "fee_float": fee_raw[1],
            "tkn0_symbol": tkn0["symbol"],
            "tkn0_decimals": tkn0["decimals"],
            "tkn0_key": get_tkn_key(tkn0["symbol"], tkn0["address"], key_digits),
            "tkn1_symbol": tkn1["symbol"],
            "tkn1_decimals": tkn1["decimals"],
            "tkn1_key": get_tkn_key(tkn1["symbol"], tkn1["address"], key_digits),
            "pair_name": pair_name(tkn0["symbol"], tkn0["address"], tkn1["symbol"], tkn1["address"], key_digits),
            "blockchain": mgr.blockchain,
            "anchor": None,
            "exchange_id": mgr.cfg.EXCHANGE_IDS[pool["exchange_name"]],
            "last_updated_block": current_block,
        }
        pool_info["descr"] = mgr.pool_descr_from_info(pool_info)
        pool_info["cid"] = mgr.cfg.w3.keccak(text=f"{pool_info['descr']}").hex()
        keys = [
            "liquidity",
            "tkn0_balance",
            "tkn0_balance",
            "tkn0_balance",
            "tkn0_balance",
            "y_0",
            "y_1",
            "tkn0_balance",
            "liquidity",
            "tkn0_balance",
        ]
        # add missing keys to dicts
        for key in pool_data_keys:
            if key not in pool_info:
                pool_info[key] = 0 if key in keys else None
        new_pool_data.append(pool_info)

    # add new_pool_data to pool_data
    mgr.pool_data = new_pool_data + mgr.pool_data

    # update the pool_data from events
    update_pools_from_events(-1, mgr, all_events)

    mgr.cfg.logger.info(f"Async Updating pools from contracts took {time.time() - start_time} seconds")


async def async_handle_main_backdate_from_contracts(idx, pool, w3_tenderly, tenderly_fork_id, pool_info, contract):

    params = await pool.update_from_contract(
        contract,
        tenderly_fork_id=tenderly_fork_id,
        w3_tenderly=w3_tenderly,
        w3=w3_async,
    )
    for key, value in params.items():
        pool_info[key] = value
    return idx, pool_info


async def async_main_backdate_from_contracts(c):
    return await asyncio.wait_for(
        asyncio.gather(*[async_handle_main_backdate_from_contracts(**args) for args in c]),
        timeout=20 * 60
    )


def async_backdate_from_contracts(mgr, rows, current_block, last_block, start_block):
    abis = {}
    exchanges = {}
    for exchange in mgr.exchanges:
        exchanges[exchange] = exchange_factory.get_exchange(exchange)
        abis[exchange] = exchanges[exchange].get_abi()
    contracts = []
    for idx in rows:
        pool_info = mgr.pool_data[idx]
        contracts.append({
            'idx': idx,
            'pool': mgr.get_or_init_pool(pool_info),
            'w3_tenderly': mgr.w3_tenderly,
            'tenderly_fork_id': mgr.tenderly_fork_id,
            'pool_info': pool_info,
            'contract': w3_async.eth.contract(address=mgr.pool_data[idx]['address'],
                                              abi=abis[mgr.pool_data[idx]['exchange_name']]),
        })

    chunks = [contracts[i:i + 1000] for i in range(0, len(contracts), 1000)]
    for idx2, chunk in enumerate(chunks):
        mgr.cfg.logger.info(f"Backdating {idx2} of {len(chunks)} chunked pools from {start_block} to {current_block}")
        loop = asyncio.get_event_loop()
        vals = loop.run_until_complete(async_main_backdate_from_contracts(chunk))
        idxes = [val[0] for val in vals]
        updated_pool_info = [val[1] for val in vals]
        for i, idx in enumerate(idxes):
            updated_pool_data = updated_pool_info[i]
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

            mgr.cfg.logger.info(
                f"Backdating {len(other_pool_rows)} pools from {start_block} to {current_block}"
            )
            start_time = time.time()
            async_backdate_from_contracts(
                mgr,
                other_pool_rows,
                current_block=current_block,
                last_block=last_block,
                start_block=start_block,
            )
            mgr.cfg.logger.info(
                f"Backdating {len(other_pool_rows)} pools took {time.time() - start_time} seconds"
            )
