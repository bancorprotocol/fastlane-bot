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
@click.option('--only_carbon', default=False, help='Only update carbon pools')
def main(
        bypairs: any = None,
        update_interval_seconds: int = None,
        config: str = None,
        only_carbon: bool = False
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
    only_carbon : bool
        Only update carbon pools.

    """
    if bypairs:
        bypairs = bypairs.split(',') if bypairs else []

    if config and config == 'tenderly':
        cfg = Config.new(config=Config.CONFIG_TENDERLY)
    else:
        cfg = Config.new(config=Config.CONFIG_MAINNET)

    # Load data from CSV file
    filepath = construct_file_path('fastlane_bot/data', 'pairs_list3.csv')
    pools_and_token_table = pd.read_csv(filepath, low_memory=False)

    # Create a CarbonBot instance
    bot = CarbonBot(ConfigObj=cfg)

    # Force set the DatabaseManager config
    bot.db.c = bot.c

    # Run the update
    bot.db.update_pools_heartbeat(bypairs=bypairs, pools_and_token_table=pools_and_token_table, update_interval_seconds=update_interval_seconds, only_carbon=only_carbon)


if __name__ == "__main__":
    main()
