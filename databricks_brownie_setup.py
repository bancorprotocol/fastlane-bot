# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC %reload_ext autoreload

# COMMAND ----------

import os

bot_path = '/Workspace/Repos/mike@bancor.network/carbonbot-refactor'
ETH_PRIVATE_KEY = dbutils.secrets.get(scope="fastlane", key=f"ETH_PRIVATE_KEY_BE_CAREFUL")
WEB3_ALCHEMY_PROJECT_ID = os.environ.get('WEB3_ALCHEMY_PROJECT_ID')
DEFAULT_MIN_PROFIT_BNT = os.environ.get('DEFAULT_MIN_PROFIT_BNT')
TENDERLY_FORK_ID = os.environ.get('TENDERLY_FORK_ID')

#!/bin/bash
! export ETH_PRIVATE_KEY_BE_CAREFUL={ETH_PRIVATE_KEY}
! export WEB3_ALCHEMY_PROJECT_ID={WEB3_ALCHEMY_PROJECT_ID}
! export DEFAULT_MIN_PROFIT_BNT={DEFAULT_MIN_PROFIT_BNT}
! export TENDERLY_FORK_ID={TENDERLY_FORK_ID}

with open(f'{bot_path}/.env', 'w') as f:
    f.write(f'ETH_PRIVATE_KEY_BE_CAREFUL={ETH_PRIVATE_KEY} \n')
    f.write(f'WEB3_ALCHEMY_PROJECT_ID={WEB3_ALCHEMY_PROJECT_ID} \n')
    f.write(f'DEFAULT_MIN_PROFIT_BNT={DEFAULT_MIN_PROFIT_BNT} \n')
    f.write(f'TENDERLY_FORK_ID={TENDERLY_FORK_ID} \n')
    f.close()

! rm /root/.brownie/network-config.yaml

TENDERLY_FORK = None
MAINNET_URL = 'https://eth-mainnet.alchemyapi.io/v2/'
TENDERLY_URL = 'https://rpc.tenderly.co/fork/'

if not TENDERLY_FORK:
    RPC_URL = f"{MAINNET_URL}{WEB3_ALCHEMY_PROJECT_ID}"
    
else:
    RPC_URL = f"{TENDERLY_URL}{TENDERLY_FORK}"

cfg = 'tenderly' if TENDERLY_FORK else 'mainnet'

del_network = f"cd {bot_path}; brownie networks delete {cfg}"

add_network = f'cd {bot_path}; brownie networks add "Ethereum" "{cfg}" host="{RPC_URL}" chainid=1'

set_network = f'cd {bot_path}; brownie networks set_provider alchemy'

! {del_network}
! {add_network}
! {set_network}
