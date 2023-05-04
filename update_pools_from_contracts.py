# Databricks notebook source
# ! python /Workspace/Repos/carbonbot/carbonbot/run_db_update_w_heartbeat.py

# COMMAND ----------

# MAGIC %pip install -r requirements.txt

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

bot_path = '/Workspace/Repos/mike@bancor.network/carbonbot'

# COMMAND ----------

ETH_PRIVATE_KEY = dbutils.secrets.get(scope="fastlane", key=f"ETH_PRIVATE_KEY_BE_CAREFUL")
WEB3_ALCHEMY_PROJECT_ID = dbutils.secrets.get(scope="fastlane", key=f"WEB3_ALCHEMY_PROJECT_ID")
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


with open(f'{bot_path}/.env', 'w') as f:
    f.write(f'ETH_PRIVATE_KEY_BE_CAREFUL={ETH_PRIVATE_KEY} \n')
    f.write(f'WEB3_ALCHEMY_PROJECT_ID={WEB3_ALCHEMY_PROJECT_ID} \n')
    f.write(f'POSTGRES_PASSWORD={POSTGRES_PASSWORD} \n')
    f.write(f'POSTGRES_USER={POSTGRES_USER} \n')
    f.write(f'POSTGRES_HOST={POSTGRES_HOST} \n')
    f.write(f'POSTGRES_PORT={POSTGRES_PORT} \n')
    f.close()

# COMMAND ----------

RPC_URL = f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}"

# COMMAND ----------

del_network = f"cd {bot_path}; brownie networks delete alchemy"

add_network = f'cd {bot_path}; brownie networks import ./brownie-config.yaml true; brownie networks add "Ethereum" "alchemy" host="{RPC_URL}" chainid=1'

mod_network = f'cd {bot_path}; brownie networks modify "alchemy" host="{RPC_URL}" name="mainnet" chainid=1'

set_network = f'cd {bot_path}; brownie networks set_provider alchemy'

! {del_network}
! {add_network}
! {set_network}

# COMMAND ----------

import subprocess

cmd = f"cd {bot_path}; python run_db_update_w_heartbeat.py"

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
