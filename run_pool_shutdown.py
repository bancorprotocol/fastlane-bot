# coding=utf-8
"""
Runs the fastlane bot in pool shutdown mode.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import os

import pandas as pd

from fastlane_bot.tools.pool_shutdown import AutomaticPoolShutdown

try:
    env_var = "TENDERLY_FORK_ID"
    with open(".env", "r") as file:
        lines = file.readlines()

    with open(".env", "w") as file:
        for line in lines:
            if line.startswith(f"{env_var}=") or line.startswith(f"export {env_var}="):
                line = f"{env_var}="
            file.write(line)
except:
    pass

import click
from dotenv import load_dotenv

from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.events.utils import (
    get_static_data,
    handle_exchanges,
    handle_target_tokens,
    handle_flashloan_tokens,
    get_config,
    get_loglevel,
    handle_target_token_addresses,
    read_csv_file,
)
from fastlane_bot.utils import find_latest_timestamped_folder

load_dotenv()


@click.command()
@click.option("--config", default=None, type=str, help="See config in config/*")
@click.option("--n_jobs", default=-1, help="Number of parallel jobs to run")
@click.option(
    "--polling_interval",
    default=12,
    help="Polling interval in seconds",
)
@click.option(
    "--logging_path",
    default="",
    help="The logging path.",
)
@click.option(
    "--loglevel",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="The logging level.",
)
def main(
    logging_path: str,
    loglevel: str,
    polling_interval: int,
    config: str,
    n_jobs: int,
    flashloan_tokens: str = "ETH",
    exchanges: str = "bancor_v3",
    alchemy_max_block_fetch: int = 20,
    static_pool_data_filename: str = "static_pool_data",
    static_pool_data_sample_sz: str = "max",
    limit_bancor3_flashloan_tokens: bool = False,
    default_min_profit_gas_token: int = 0,
    timeout: int = 0,
    target_tokens: str = None,
    replay_from_block: int = None,
    blockchain: str = "ethereum",
):
    """
    The main entry point of the program. It sets up the configuration, initializes the web3 and Base objects,
    adds initial pools to the Base and then calls the `run` function.

    Args:
        flashloan_tokens (str): Comma seperated list of tokens that the bot can use for flash loans.
        config (str): The name of the configuration to use.
        n_jobs (int): The number of jobs to run in parallel.
        exchanges (str): A comma-separated string of exchanges to include.
        polling_interval (int): The time interval at which the bot polls for new events.
        alchemy_max_block_fetch (int): The maximum number of blocks to fetch in a single request.
        static_pool_data_filename (str): The filename of the static pool data to read from.
        logging_path (str): The logging path.
        loglevel (str): The logging level.
        static_pool_data_sample_sz (str): The sample size of the static pool data.
        limit_bancor3_flashloan_tokens (bool): Whether to limit the flashloan tokens to the ones supported by Bancor v3 or not.
        default_min_profit_gas_token (int): The default minimum profit in BNT.
        timeout (int): The timeout in seconds.
        target_tokens (str): A comma-separated string of tokens to target. Use None to target all tokens. Use `flashloan_tokens` to target only the flashloan tokens.
        replay_from_block (int): The block number to replay from. (For debugging / testing)

    """

    # Set config
    loglevel = get_loglevel(loglevel)
    base_path = os.path.normpath(f"fastlane_bot/data/blockchain_data/ethereum/")
    tokens_filepath = os.path.join(base_path, "tokens.csv")
    if not os.path.exists(tokens_filepath):
        df = pd.DataFrame(
            columns=["key", "symbol", "name", "address", "decimals", "blockchain"]
        )
        df.to_csv(tokens_filepath)
    tokens = read_csv_file(tokens_filepath)

    # Initialize the config object
    cfg = get_config(
        default_min_profit_gas_token="0",
        limit_bancor3_flashloan_tokens=limit_bancor3_flashloan_tokens,
        loglevel=loglevel,
        logging_path=logging_path,
        blockchain="ethereum",
    )

    base_path = os.path.normpath(f"fastlane_bot/data/blockchain_data/{blockchain}/")
    tokens_filepath = os.path.join(base_path, "tokens.csv")
    if not os.path.exists(tokens_filepath):
        df = pd.DataFrame(
            columns=["key", "symbol", "name", "address", "decimals", "blockchain"]
        )
        df.to_csv(tokens_filepath)
    tokens = read_csv_file(tokens_filepath)

    # Format the flashloan tokens
    flashloan_tokens = handle_flashloan_tokens(cfg, flashloan_tokens, tokens)

    # Search the logging directory for the latest timestamped folder
    logging_path = find_latest_timestamped_folder(logging_path)

    # Format the target tokens
    target_tokens = handle_target_tokens(cfg, flashloan_tokens, target_tokens)

    # Format the exchanges
    exchanges = handle_exchanges(cfg, exchanges)

    # Log the run configuration
    cfg.logger.info(
        f"""
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        Starting fastlane bot with the following configuration:
        
        
        ---Pool Shutdown Mode---
        
        ***** WARNING: This mode shuts down Bancor V3 liquidity pools without considering profit *****
        
     o                                              
                              ___..                       ,
                      __..--''__ (                      .';
  o      __.-------.-'            `--..__             .'  ;
    _.--'   0)         .--._             ``--...____.'   .'
   (     _.      )).   .__.-''                          <
    `````---....._____.....-   -..___       _____...--'-.'.
                        `-.___.'     ```````             `.;
                                                           `
        
        config: {config}
        n_jobs: {n_jobs}
        polling_interval: {polling_interval}
        loglevel: {loglevel}
        
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        """
    )

    # Get the static pool data, tokens and uniswap v2 event mappings
    (
        static_pool_data,
        tokens,
        uniswap_v2_event_mappings,
        uniswap_v3_event_mappings,
    ) = get_static_data(
        cfg=cfg,
        exchanges=exchanges,
        blockchain=blockchain,
        static_pool_data_filename=static_pool_data_filename,
    )

    target_token_addresses = handle_target_token_addresses(
        static_pool_data, target_tokens
    )

    # Break if timeout is hit to test the bot flags
    if timeout == 1:
        cfg.logger.info("Timeout to test the bot flags")
        return

    # Initialize data fetch manager
    mgr = Manager(
        web3=cfg.w3,
        cfg=cfg,
        pool_data=static_pool_data.to_dict(orient="records"),
        SUPPORTED_EXCHANGES=exchanges,
        alchemy_max_block_fetch=alchemy_max_block_fetch,
        uniswap_v2_event_mappings=uniswap_v2_event_mappings,
        tokens=tokens.to_dict(orient="records"),
        replay_from_block=replay_from_block,
        target_tokens=target_token_addresses,
    )

    pool_shutdown = AutomaticPoolShutdown(mgr=mgr, polling_interval=polling_interval)
    pool_shutdown.main_loop()


if __name__ == "__main__":
    main()

# %%
