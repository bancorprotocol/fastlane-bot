import os
import platform

import click
import numpy as np
import pandas as pd

from fastlane_bot import Config
from fastlane_bot.data import abi as abis
from fastlane_bot.bot import CarbonBot
from fastlane_bot.config.connect import EthereumNetwork

# Detect the current operating system
current_os = platform.system()

# Define the project's root directory
project_root = os.path.dirname(os.path.abspath(__file__))


def construct_file_path(data_dir, file_name):
    """
    Constructs a file path for the given data directory and file name, based on the current operating system.
    """
    if current_os == 'Windows':
        file_path = os.path.join(project_root, data_dir, file_name).replace('/', '\\')
    else:
        file_path = os.path.join(project_root, data_dir, file_name).replace('\\', '/')
    return file_path


@click.command()
@click.option('--bypairs', default=None, help='The pairs to update')
@click.option('--update_interval_seconds', default=12, help='The update interval in seconds')
@click.option('--config', default=None, help='The config to use')
def main(
        bypairs: any = None,
        update_interval_seconds: int = None,
        config: str = None
):
    """
    Main function for the update_pools_heartbeat.py script.

    Parameters
    ----------
    bypairs : list[str]
        The pairs to update.
    update_interval_seconds : int
        The update interval in seconds.
    config : str
        The config to use.

    """
    if bypairs:
        bypairs = bypairs.split(',') if bypairs else []

    if config and config == 'tenderly':
        cfg = Config.new(config=Config.CONFIG_TENDERLY)
    else:
        cfg = Config.new(config=Config.CONFIG_MAINNET)

    # Load data from CSV file
    pools_and_token_table_columns = ['cid', 'last_updated', 'last_updated_block', 'descr', 'pair_name', 'exchange_name',
                                     'fee', 'fee_float', 'address', 'anchor', 'tkn0_address', 'tkn1_address',
                                     'tkn0_key', 'tkn1_key', 'tkn0_decimals', 'tkn1_decimals', 'exchange_id',
                                     'tkn0_symbol', 'tkn1_symbol']

    filepath = construct_file_path('fastlane_bot/data', 'combined_tables.csv')
    pools_and_token_table = pd.read_csv(filepath, low_memory=False).sample(10)
    print(f"pools_and_token_table: {pools_and_token_table.columns}")
    pools_and_token_table = pools_and_token_table.rename({'anchor_address': 'anchor'}, axis=1)
    # for col in pools_and_token_table_columns:
    #     if col not in pools_and_token_table.columns:
    #         pools_and_token_table[col] = [np.NaN for _ in range(len(pools_and_token_table))]

    pools_and_token_table = pools_and_token_table[pools_and_token_table_columns]

    bot = CarbonBot(ConfigObj=cfg)
    print(f"bot endpoint_uri: {bot.c.w3.provider.endpoint_uri}")
    bot.db.c = bot.c
    print(f"db endpoint_uri: {bot.db.c.w3.provider.endpoint_uri}")
    #
    # carbon_controller = bot.c.w3.eth.contract(address=bot.db.c.CARBON_CONTROLLER_ADDRESS, abi=abis.CARBON_CONTROLLER_ABI)
    # bot.db.carbon_controller = carbon_controller

    # bot.db.drop_all_tables()
    bot.db.update_pools_heartbeat(bypairs=bypairs, pools_and_token_table=pools_and_token_table, update_interval_seconds=update_interval_seconds)


if __name__ == "__main__":
    main()
