import json
import logging
import os
import time
from typing import List, Any, Tuple, Hashable

import brownie
import click
import pandas as pd
from dotenv import load_dotenv
from joblib import Parallel, delayed

from fastlane_bot.bot import CarbonBot
from fastlane_bot.config import Config
from fastlane_bot.data_fetcher.interface import QueryInterface
from fastlane_bot.data_fetcher.manager import Manager
from fastlane_bot.data_fetcher.utils import complex_handler, filter_latest_events

load_dotenv()


@click.command()
@click.option(
    "--cache_latest_only",
    default=True,
    type=bool,
    help="Set to True for production. Set to False for " "testing / debugging",
)
@click.option(
    "--backdate_pools",
    default=True,
    type=bool,
    help="Set to False for faster testing / debugging",
)
@click.option(
    "--static_pool_data_filename",
    default="static_pool_data",
    help="Filename of the static pool data.",
)
@click.option("--arb_mode", default="single", type=str, help="See arb_mode in bot.py")
@click.option(
    "--flashloan_tokens", default=None, type=str, help="See flashloan_tokens in bot.py"
)
@click.option("--config", default=None, type=str, help="See config in config/*")
@click.option("--n_jobs", default=-1, help="Number of parallel jobs to run")
@click.option(
    "--exchanges",
    default="uniswap_v3,carbon_v1,bancor_v3",
    # default="uniswap_v3,uniswap_v2,bancor_v3,carbon_v1",
    help="Comma separated external exchanges",
)
@click.option(
    "--polling_interval",
    default=12,
    help="Polling interval in seconds",
)
@click.option(
    "--alchemy_max_block_fetch",
    default=2000,
    help="Max number of blocks to fetch from alchemy",
)
@click.option(
    "--reorg_delay",
    default=2,
    help="Number of blocks delayed to avoid reorgs",
)
def main(
        cache_latest_only: bool,
        backdate_pools: bool,
        arb_mode: str,
        flashloan_tokens: str,
        config: str,
        n_jobs: int,
        exchanges: str,
        polling_interval: int,
        alchemy_max_block_fetch: int,
        static_pool_data_filename: str,
        reorg_delay: int,
):
    """
    The main entry point of the program. It sets up the configuration, initializes the web3 and Manager objects,
    adds initial pools to the Manager and then calls the `run` function.

    Args:
        cache_latest_only (bool): Whether to cache only the latest events or not.
        backdate_pools (bool): Whether to backdate pools or not. Set to False for quicker testing runs.
        arb_mode (str): The arbitrage mode to use.
        flashloan_tokens (str): Tokens that the bot can use for flash loans.
        config (str): The name of the configuration to use.
        n_jobs (int): The number of jobs to run in parallel.
        exchanges (str): A comma-separated string of exchanges to include.
        polling_interval (int): The time interval at which the bot polls for new events.
        alchemy_max_block_fetch (int): The maximum number of blocks to fetch in a single request.
        static_pool_data_filename (str): The filename of the static pool data to read from.
        reorg_delay (int): The number of blocks to wait to avoid reorgs.
    """
    # Set config
    if config and config == "tenderly":
        cfg = Config.new(config=Config.CONFIG_TENDERLY)
        cfg.logger.info("Using Tenderly config")
    else:
        cfg = Config.new(config=Config.CONFIG_MAINNET)
        cfg.logger.info("Using mainnet config")

    # Set external exchanges
    exchanges = exchanges.split(",")
    cfg.logger.info(f"Running data fetching for exchanges: {exchanges}")

    # Check if CSV file exists
    if not os.path.isfile(f"fastlane_bot/data/{static_pool_data_filename}.csv"):
        cfg.logger.error("CSV file does not exist")
        raise FileNotFoundError("CSV file does not exist")

    # Read static pool data from CSV
    try:
        static_pool_data = pd.read_csv(
            f"fastlane_bot/data/{static_pool_data_filename}.csv", low_memory=False
        )
        static_pool_data = static_pool_data[
            static_pool_data["exchange_name"].isin(exchanges)
        ]
    except pd.errors.ParserError:
        cfg.logger.error("Error parsing the CSV file")
        raise

    # Initialize web3
    static_pool_data["cid"] = [
        cfg.w3.keccak(text=f"{row['descr']}").hex()
        for index, row in static_pool_data.iterrows()
    ]

    # Initialize data fetch manager
    mgr = Manager(
        web3=cfg.w3,
        cfg=cfg,
        pool_data=static_pool_data.to_dict(orient="records"),
        SUPPORTED_EXCHANGES=exchanges,
        alchemy_max_block_fetch=alchemy_max_block_fetch,
    )

    # Add initial pools for each row in the static_pool_data
    start_time = time.time()
    Parallel(n_jobs=n_jobs, backend="threading")(
        delayed(mgr.add_pool_to_exchange)(row) for row in mgr.pool_data
    )
    cfg.logger.info(f"Time taken to add initial pools: {time.time() - start_time}")

    # Run the main loop
    run(
        cache_latest_only,
        backdate_pools,
        mgr,
        n_jobs,
        polling_interval,
        alchemy_max_block_fetch,
        arb_mode,
        flashloan_tokens,
        reorg_delay,
    )


def run(
        cache_latest_only: bool,
        backdate_pools: bool,
        mgr: Manager,
        n_jobs: int,
        polling_interval: int,
        alchemy_max_block_fetch: int,
        arb_mode: str,
        flashloan_tokens: List[str] or None,
        reorg_delay: int,
) -> None:
    """
    The main function that drives the logic of the program. It uses helper functions to handle specific tasks.

    Args:
        cache_latest_only (bool): Whether to cache only the latest events or not.
        backdate_pools (bool): Whether to backdate pools or not. Set to False for quicker testing runs.
        mgr (Manager): The manager object that is responsible for handling events and updating pools.
        n_jobs (int): The number of jobs to run in parallel.
        polling_interval (int): The time interval at which the bot polls for new events.
        alchemy_max_block_fetch (int): The maximum number of blocks to fetch in a single request.
        arb_mode (str): The arbitrage mode to use.
        flashloan_tokens (List[str]): List of tokens that the bot can use for flash loans.
        reorg_delay (int): The number of blocks to wait to avoid reorgs.
    """

    def get_event_filters(start_block: int, current_block: int) -> Any:
        """
        Creates event filters for the specified block range.

        Args:
            start_block (int): The starting block number for the event filters.
            current_block (int): The current block number for the event filters.

        Returns:
            Any: A list of event filters.
        """
        return Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(event.createFilter)(fromBlock=start_block, toBlock=current_block)
            for event in mgr.events
        )

    def get_all_events(event_filters: Any) -> List[Any]:
        """
        Fetches all events using the given event filters.

        Args:
            event_filters (Any): A list of event filters to use.

        Returns:
            List[Any]: A nested list of all fetched events.
        """
        return Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(event_filter.get_all_entries)() for event_filter in event_filters
        )

    def save_events_to_json(
            latest_events: List[Any], start_block: int, current_block: int
    ) -> None:
        """
        Saves the given events to a JSON file.

        Args:
            latest_events (List[Any]): A list of the latest events to save.
            start_block (int): The starting block number of the events.
            current_block (int): The current block number of the events.
        """
        if cache_latest_only:
            path = "latest_event_data.json"
        else:
            path = f"{mgr.SUPPORTED_EXCHANGES}_{start_block}_{current_block}.json"
        with open(path, "w") as f:
            latest_events = [_['args'].pop('contextId', None) for _ in latest_events] and latest_events
            f.write(json.dumps(latest_events))

    def update_pools_from_events(latest_events: List[Any]) -> None:
        """
        Updates the pools with the given events.

        Args:
            latest_events (List[Any]): A list of the latest events.
        """
        Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(mgr.update)(event=event) for event in latest_events
        )

    def update_pools_directly_from_contracts(rows_to_update: List[int]) -> None:
        """
        Updates the pools directly from the contracts.

        Args:
            rows_to_update (List[int]): A list of indices of rows to update.
        """
        with brownie.multicall(address=mgr.cfg.MULTICALL_CONTRACT_ADDRESS):
            Parallel(n_jobs=n_jobs, backend="threading")(
                delayed(mgr.update)(pool_info=mgr.pool_data[idx])
                for idx in rows_to_update
            )

    def write_pool_data_to_disk(current_block: int) -> None:
        """
        Writes the pool data to disk.

        Args:
            current_block (int): The current block number.
        """
        if cache_latest_only:
            path = "latest_pool_data.json"
        else:
            path = f"{mgr.SUPPORTED_EXCHANGES}_{current_block}.json"
        with open(path, "w") as f:
            f.write(json.dumps(mgr.pool_data))

    def parse_bancor3_rows_to_update(rows_to_update: List[Hashable]) -> Tuple[List[Hashable], List[Hashable]]:
        """
        Parses the rows to update for Bancor v3 pools.

        Args:
            rows_to_update (List[int]): A list of indices of rows to update.

        Returns:
            Tuple[List[str], List[str]]: A tuple of lists of Bancor v3 pool addresses and other pool addresses.
        """
        bancor3_pool_rows = [
            idx for idx in rows_to_update if
            mgr.pool_data[idx]["exchange_name"] == "bancor_v3"
        ]
        other_pool_rows = [
            idx for idx in rows_to_update if
            mgr.pool_data[idx]["exchange_name"] != "bancor_v3"
        ]
        return bancor3_pool_rows, other_pool_rows

    def init_bot():
        mgr.cfg.logger.info("Initializing the bot...")
        db = QueryInterface(ConfigObj=mgr.cfg, state=mgr.pool_data)
        bot = CarbonBot(ConfigObj=mgr.cfg)
        bot.db = db
        assert isinstance(
            bot.db, QueryInterface
        ), "QueryInterface not initialized correctly"
        return bot

    last_block = 0
    bot = None
    loop_idx = 0
    while True:
        try:

            # Save initial state of pool data to assert whether it has changed
            initial_state = mgr.pool_data.copy()

            # Get current block number, then adjust to the block number reorg_delay blocks ago to avoid reorgs
            current_block = mgr.web3.eth.blockNumber - reorg_delay

            # Get all events from the last block to the current block
            start_block = (
                max(0, current_block - alchemy_max_block_fetch)
                if last_block == 0
                else last_block + 1
            )

            # Get all event filters, events, and flatten them
            events = [
                complex_handler(event)
                for event in [
                    complex_handler(event)
                    for event in get_all_events(
                        get_event_filters(start_block, current_block)
                    )
                ]
            ]

            # Filter out the latest events per pool, save them to disk, and update the pools
            latest_events = filter_latest_events(mgr, events)
            save_events_to_json(latest_events, start_block, current_block)
            update_pools_from_events(latest_events)

            # Assert that all the pools in the event data have been updated
            unique_pools_in_events = {event["address"] for event in latest_events}
            unique_pools_in_pool_data = {pool["address"] for pool in mgr.pool_data}
            assert (
                all(pool_address in unique_pools_in_pool_data for pool_address in unique_pools_in_events)
            ), f"Not all pools in the event data have been updated {mgr.pool_data}"

            # If this is the first iteration, update all pools without a recent event from the contracts
            if last_block == 0 and backdate_pools:
                rows_to_update = mgr.get_rows_to_update(start_block)
                bancor3_pool_rows, other_pool_rows = parse_bancor3_rows_to_update(rows_to_update)
                for rows_to_update in [bancor3_pool_rows, other_pool_rows]:
                    update_pools_directly_from_contracts(rows_to_update)

            # Update the last block and write the pool data to disk for debugging, and to backup the state
            last_block = current_block
            write_pool_data_to_disk(current_block)

            # Initialize the bot if it hasn't been initialized yet
            if bot is None:
                bot = init_bot()

            # Compare the initial state to the final state, and update the state if it has changed
            final_state = mgr.pool_data.copy()
            if initial_state != final_state:
                mgr.cfg.logger.info("State has changed...")
                bot.db.update_state(final_state)
                bot.db.handle_token_key_cleanup()

            if loop_idx > 0:
                bot.db.remove_zero_liquidity_pools()

            # Increment the loop index
            loop_idx += 1

            bot.run(
                polling_interval=polling_interval,
                flashloan_tokens=flashloan_tokens,
                mode="single",
                arb_mode=arb_mode,
            )
            time.sleep(polling_interval)

        except Exception as e:
            mgr.cfg.logger.error(f"Error in main loop: {e}")
            time.sleep(polling_interval)


if __name__ == "__main__":
    main()
