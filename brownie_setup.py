# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC %reload_ext autoreload

# COMMAND ----------

import contextlib
import os

from dotenv import load_dotenv

load_dotenv()

# Common environment variables
WEB3_ALCHEMY_PROJECT_ID = os.environ.get('WEB3_ALCHEMY_PROJECT_ID')
DEFAULT_MIN_PROFIT_BNT = os.environ.get('DEFAULT_MIN_PROFIT_BNT')
TENDERLY_FORK_ID = os.environ.get('TENDERLY_FORK_ID')

try:
    # Get secrets
    ETH_PRIVATE_KEY = dbutils.secrets.get(scope="fastlane", key=f"ETH_PRIVATE_KEY_BE_CAREFUL")
    USER_EMAIL = os.environ.get('USER_EMAIL')
    bot_path = f'/Workspace/Repos/{USER_EMAIL}/carbonbot-refactor'
    env_path = f'{bot_path}/.env'

    # Set environment variables
    os.environ["ETH_PRIVATE_KEY_BE_CAREFUL"] = ETH_PRIVATE_KEY
    os.environ["WEB3_ALCHEMY_PROJECT_ID"] = WEB3_ALCHEMY_PROJECT_ID
    os.environ["DEFAULT_MIN_PROFIT_BNT"] = DEFAULT_MIN_PROFIT_BNT
    os.environ["TENDERLY_FORK_ID"] = TENDERLY_FORK_ID

    # Write environment variables to .env file
    with open(f'{bot_path}/.env', 'w') as f:
        f.write(f'ETH_PRIVATE_KEY_BE_CAREFUL={ETH_PRIVATE_KEY} \n')
        f.write(f'WEB3_ALCHEMY_PROJECT_ID={WEB3_ALCHEMY_PROJECT_ID} \n')
        f.write(f'DEFAULT_MIN_PROFIT_BNT={DEFAULT_MIN_PROFIT_BNT} \n')
        f.write(f'TENDERLY_FORK_ID={TENDERLY_FORK_ID} \n')

    with contextlib.suppress(FileNotFoundError):
        os.remove('/root/.brownie/network-config.yaml')

except NameError:
    # If not running on Databricks, then get from local env
    ETH_PRIVATE_KEY = os.environ.get("ETH_PRIVATE_KEY_BE_CAREFUL")

    # Current working directory
    bot_path = os.getcwd()
    env_path = '.env'

MAINNET_URL = 'https://eth-mainnet.alchemyapi.io/v2/'
TENDERLY_URL = 'https://rpc.tenderly.co/fork/'

if not TENDERLY_FORK_ID:
    RPC_URL = f"{MAINNET_URL}{WEB3_ALCHEMY_PROJECT_ID}"
else:
    RPC_URL = f"{TENDERLY_URL}{TENDERLY_FORK_ID}"

cfg = 'tenderly' if TENDERLY_FORK_ID else 'mainnet'

del_network = f"cd {bot_path}; brownie networks delete {cfg}"

add_network = f'cd {bot_path}; brownie networks add "Ethereum" "{cfg}" host="{RPC_URL}" chainid=1'

set_network = f'cd {bot_path}; brownie networks set_provider alchemy'

# Execute commands using os.system instead of ! in Jupyter notebooks
os.system(del_network)
os.system(add_network)
os.system(set_network)

