import os
import platform

import click
import pandas as pd

from fastlane_bot.config import Config
from fastlane_bot.bot import CarbonBot

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
@click.option('--mode', default='continuous', help='The mode of the bot. Options are: continuous, single')
@click.option('--pairs_list_filepath', default=construct_file_path('fastlane_bot/data', 'pairs_list.csv'), help='The path to the pairs list CSV file')
def main(
        bypairs: any = None,
        update_interval_seconds: int = None,
        config: str = None,
        only_carbon: bool = False,
        mode: str = 'continuous',
        pairs_list_filepath: str = None,
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
    mode : str
        The mode of the bot. Options are: continuous, single
    pairs_list_filepath : str
        The path to the pairs list CSV file.

    """
    if bypairs:
        bypairs = bypairs.split(',') if bypairs else []

    if config and config == 'tenderly':
        cfg = Config.new(config=Config.CONFIG_TENDERLY)
    else:
        cfg = Config.new(config=Config.CONFIG_MAINNET)

    # Load data from CSV file
    pools_and_token_table = pd.read_csv(pairs_list_filepath, low_memory=False)

    # Create a CarbonBot instance
    bot = CarbonBot(ConfigObj=cfg)

    # Force set the DatabaseManager config
    bot.db.c = bot.c

    # Run the update
    bot.db.update_pools_heartbeat(mode=mode, bypairs=bypairs, pools_and_token_table=pools_and_token_table,
                                  update_interval_seconds=update_interval_seconds, only_carbon=only_carbon)


if __name__ == "__main__":
    main()
