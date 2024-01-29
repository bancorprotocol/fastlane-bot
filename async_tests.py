# coding=utf-8
"""
Contains the exchange class for UniswapV2. This class is responsible for handling UniswapV2 exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio
import json
import logging
import os
from dataclasses import dataclass
from glob import glob
from typing import List, Type, Tuple, Any, Dict

import dotenv
import pandas as pd
import web3
from web3 import Web3, AsyncWeb3
from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import UNISWAP_V2_POOL_ABI
from fastlane_bot.events.exchanges import exchange_factory
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools import pool_factory
from fastlane_bot.events.pools.base import Pool

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

event_mappings = {}
# Read Uniswap v2 event mappings and tokens
uniswap_v2_filepath = "fastlane_bot/data/blockchain_data/ethereum/uniswap_v2_event_mappings.csv"
uniswap_v2_event_mappings_df = pd.read_csv(uniswap_v2_filepath)
event_mappings['uniswap_v2_pools'] = dict(
    uniswap_v2_event_mappings_df[["address", "exchange"]].values
)

# Read Uniswap v3 event mappings and tokens
uniswap_v3_filepath = "fastlane_bot/data/blockchain_data/ethereum/uniswap_v3_event_mappings.csv"
uniswap_v3_event_mappings_df = pd.read_csv(uniswap_v3_filepath)
event_mappings['uniswap_v3_pools'] = dict(
    uniswap_v3_event_mappings_df[["address", "exchange"]].values
)

event_mappings['pancakeswap_v2_pools'] = dict(
    uniswap_v2_event_mappings_df[["address", "exchange"]].values
)

event_mappings['pancakeswap_v3_pools'] = dict(
    uniswap_v3_event_mappings_df[["address", "exchange"]].values
)

event_mappings['sushiswap_v2_pools'] = dict(
    uniswap_v2_event_mappings_df[["address", "exchange"]].values
)


def exchange_name_from_event(event: Dict[str, Any]) -> str:
    return next(
        (
            exchange_name
            for exchange_name, pool_class in pool_factory._creators.items()
            if pool_class.event_matches_format(event, event_mappings)
        ),
        None,
    )

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
        logger.info(f"\n\n failed [get_token_and_fee]: {e}, {ex}, {exchange_name}, {address}, {contract}, {event}")
        return exchange_name, address, None, None, None


async def main_get_tokens_and_fee(c):
    vals = await asyncio.gather(
        *[
            get_token_and_fee(**args)
            for args in c
        ]
    )
    return pd.DataFrame(vals, columns=["exchange_name", "address", "tkn0_address", "tkn1_address", "fee"])

w3_async = AsyncWeb3(
    AsyncWeb3.AsyncHTTPProvider(f"https://eth-mainnet.alchemyapi.io/v2/{os.environ['WEB3_ALCHEMY_PROJECT_ID']}")
)

exchange_list = ('carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,'
             'pancakeswap_v3')
exchange_list = exchange_list.split(',')

static_pool_data = pd.read_csv('fastlane_bot/data/blockchain_data/ethereum/static_pool_data.csv')
static_pool_data["cid"] = [
    Web3.keccak(text=f"{row['descr']}").hex()
    for index, row in static_pool_data.iterrows()
]

with open('logs/20231106-013311/latest_event_data.json') as f:
    latest_events = json.loads(f.read())

abis = {}
exchanges = {}
for exchange in exchange_list:
    exchanges[exchange] = exchange_factory.get_exchange(exchange)
    abis[exchange] = exchanges[exchange].get_abi()


contracts = []
for event in latest_events:
    exchange_name = exchange_name_from_event(event)
    address = event['address']
    if exchange_name == 'uniswap_v2':
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
    print(idx, len(chunk))
    loop = asyncio.get_event_loop()
    tokens_and_fee_df = loop.run_until_complete(main_get_tokens_and_fee(chunk))
    tokens_and_fee_df.to_csv(f"{dirname}/tokens_and_fee_df_{idx}.csv")

### Above is working

filepaths = glob(f"{dirname}/*.csv")
pool_tokens_and_fee_df = pd.concat([pd.read_csv(filepath) for filepath in filepaths])
pool_tokens_and_fee_df = pool_tokens_and_fee_df.drop_duplicates(subset=["exchange_name", "address"])
pool_tokens_and_fee_df.to_csv("pool_tokens_and_fee_df.csv")
#
#
# # clear temp dir
# for filepath in filepaths:
#     os.remove(filepath)
#
# # for each token in the pools, check whether we have the token info in the tokens.csv static data, and ifr not,
# # add it
# tokens = pool_tokens_and_fee_df["tkn0_address"].tolist() + pool_tokens_and_fee_df["tkn1_address"].tolist()
# tokens = list(set(tokens))
# print(f"tokens: {tokens[0]}")
# tokens_df = pd.read_csv(f"fastlane_bot/data/blockchain_data/{mgr.blockchain}/tokens.csv")