import contextlib
import os
from brownie import network
from dotenv import load_dotenv

if network.is_connected():
    network.disconnect()

load_dotenv()

# Common environment variables
WEB3_ALCHEMY_PROJECT_ID = os.environ.get('WEB3_ALCHEMY_PROJECT_ID')
DEFAULT_MIN_PROFIT_BNT = os.environ.get('DEFAULT_MIN_PROFIT_BNT')
TENDERLY_FORK_ID = os.environ.get('TENDERLY_FORK_ID')

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

if network.is_connected():
    network.disconnect()

# network.connect(cfg)

