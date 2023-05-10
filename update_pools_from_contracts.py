# Databricks notebook source
# ! python /Workspace/Repos/carbonbot/carbonbot/run_db_update_w_heartbeat.py

# COMMAND ----------

# MAGIC %pip install -r requirements.txt

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

# MAGIC %reload_ext autoreload

# COMMAND ----------

# dbutils.widgets.text("bypairs", "None")
# dbutils.widgets.text("TENDERLY_FORK", "058b12b9-c69e-4676-a7bd-2ba09c9b23c7")


# COMMAND ----------

bypairs = dbutils.widgets.get("bypairs")
TENDERLY_FORK = dbutils.widgets.get("TENDERLY_FORK")
only_carbon = dbutils.widgets.get("only_carbon")

if str(only_carbon) == 'True':
    only_carbon = True

elif str(only_carbon) == 'False':
    only_carbon = False

if str(TENDERLY_FORK) == 'None':
    TENDERLY_FORK = None

if str(bypairs) == 'None':
    bypairs = None
    
cfg = 'tenderly' if TENDERLY_FORK else 'mainnet'
POSTGRES_DB = "defaultdb" if not TENDERLY_FORK else TENDERLY_FORK
bypairs

# COMMAND ----------

bot_path = '/Workspace/Repos/mike@bancor.network/carbonbot'

# COMMAND ----------

import os
ETH_PRIVATE_KEY = dbutils.secrets.get(scope="fastlane", key=f"ETH_PRIVATE_KEY_BE_CAREFUL")
WEB3_ALCHEMY_PROJECT_ID = os.environ.get('WEB3_ALCHEMY_PROJECT_ID')
POSTGRES_PASSWORD = dbutils.secrets.get(scope="fastlane", key=f"POSTGRES_PASSWORD")
POSTGRES_USER = dbutils.secrets.get(scope="fastlane", key=f"POSTGRES_USER")
POSTGRES_HOST = dbutils.secrets.get(scope="fastlane", key=f"POSTGRES_HOST")
POSTGRES_PORT = "27140"


#!/bin/bash
! export ETH_PRIVATE_KEY_BE_CAREFUL={ETH_PRIVATE_KEY}
! export WEB3_ALCHEMY_PROJECT_ID={WEB3_ALCHEMY_PROJECT_ID}
! export POSTGRES_PASSWORD={POSTGRES_PASSWORD}
! export POSTGRES_USER={POSTGRES_USER}
! export POSTGRES_HOST={POSTGRES_HOST}
! export POSTGRES_PORT={POSTGRES_PORT}
! export POSTGRES_DB={POSTGRES_DB}


with open(f'{bot_path}/.env', 'w') as f:
    f.write(f'ETH_PRIVATE_KEY_BE_CAREFUL={ETH_PRIVATE_KEY} \n')
    f.write(f'WEB3_ALCHEMY_PROJECT_ID={WEB3_ALCHEMY_PROJECT_ID} \n')
    f.write(f'POSTGRES_PASSWORD={POSTGRES_PASSWORD} \n')
    f.write(f'POSTGRES_USER={POSTGRES_USER} \n')
    f.write(f'POSTGRES_HOST={POSTGRES_HOST} \n')
    f.write(f'POSTGRES_PORT={POSTGRES_PORT} \n')
    f.write(f'POSTGRES_DB={POSTGRES_DB} \n')
    f.close()

# COMMAND ----------

! rm /root/.brownie/network-config.yaml

# COMMAND ----------

MAINNET_URL = 'https://eth-mainnet.alchemyapi.io/v2/'
TENDERLY_URL = 'https://rpc.tenderly.co/fork/'

if not TENDERLY_FORK:
    RPC_URL = f"{MAINNET_URL}{WEB3_ALCHEMY_PROJECT_ID}" 
    
else:
    RPC_URL = f"{TENDERLY_URL}{TENDERLY_FORK}"


RPC_URL

# COMMAND ----------

del_network = f"cd {bot_path}; brownie networks delete {cfg}"

add_network = f'cd {bot_path}; brownie networks add "Ethereum" "{cfg}" host="{RPC_URL}" chainid=1'

set_network = f'cd {bot_path}; brownie networks set_provider alchemy'

! {del_network}
! {add_network}
! {set_network}

# COMMAND ----------

cmd = f"cd {bot_path}; python run_db_update_w_heartbeat.py"

if bypairs:
    cmd += f" --bypairs={bypairs}"

if only_carbon:
    cmd += f" --only_carbon={only_carbon}"

if cfg == 'tenderly':
    cmd += ' --config=tenderly'

cmd

# COMMAND ----------

from fastlane_bot import Config
from fastlane_bot.bot import CarbonBot

cfg = Config.new(config=Config.CONFIG_TENDERLY)
cfg.w3.provider.endpoint_uri

# COMMAND ----------

import subprocess

p = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stdin=subprocess.PIPE,
    shell=True,
)

stdout, stderr = p.communicate()

print((f'{stdout.decode("utf-8")}'))

raise Exception(f'{stderr.decode("utf-8")}')
