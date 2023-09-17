# coding=utf-8
"""
This is the main file for configuring the bot and running the fastlane bot.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from web3 import Web3, HTTPProvider

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

import time
from typing import List

import click
from dotenv import load_dotenv

from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.events.utils import (
    add_initial_pool_data,
    get_static_data,
    handle_exchanges,
    handle_target_tokens,
    handle_flashloan_tokens,
    get_config,
    get_loglevel,
    update_pools_from_events,
    write_pool_data_to_disk,
    init_bot,
    get_cached_events,
    handle_subsequent_iterations,
    verify_state_changed,
    handle_duplicates,
    handle_initial_iteration,
    get_latest_events,
    get_start_block,
    set_network_to_mainnet_if_replay,
    set_network_to_tenderly_if_replay,
    verify_min_bnt_is_respected,
    handle_target_token_addresses,
    multicall_every_iteration,
    handle_replay_from_block,
    update_pools_from_contracts,
)
from fastlane_bot.tools.cpc import T
from fastlane_bot.utils import find_latest_timestamped_folder

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
    default=False,
    type=bool,
    help="Set to False for faster testing / debugging",
)
@click.option(
    "--static_pool_data_filename",
    default="static_pool_data",
    help="Filename of the static pool data.",
)
@click.option(
    "--arb_mode",
    default="multi",
    help="See arb_mode in bot.py",
    type=click.Choice(
        [
            "single",
            "multi",
            "triangle",
            "multi_triangle",
            "bancor_v3",
            "b3_two_hop",
            "multi_pairwise_pol",
        ]
    ),
)
@click.option(
    "--flashloan_tokens",
    default=f"{T.WBTC},{T.BNT},{T.NATIVE_ETH},{T.USDC},{T.USDT},{T.WETH},{T.LINK}",
    type=str,
    help="The --flashloan_tokens flag refers to those token denominations which the bot can take a flash loan in. By "
    "default, these are [WETH, DAI, USDC, USDT, WBTC, BNT, NATIVE_ETH]. If you override the default to TKN, "
    "the search space is decreased for all modes, including the b3_two_hop mode (assuming that "
    "--limit_bancor3_flashloan_tokens=True).",
)
@click.option("--n_jobs", default=-1, help="Number of parallel jobs to run")
@click.option(
    "--exchanges",
    default="carbon_v1,bancor_v3,uniswap_v3,uniswap_v2,sushiswap_v2,bancor_pol",
    help="Comma separated external exchanges. Note that carbon_v1 and bancor_v3 must be included.",
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
@click.option(
    "--static_pool_data_sample_sz",
    default="max",
    type=str,
    help="The sample size of the static pool data. Set to 'max' for production.",
)
@click.option(
    "--use_cached_events",
    default=False,
    type=bool,
    help="Set to True for debugging / testing. Set to False for production.",
)
@click.option(
    "--run_data_validator",
    default=False,
    type=bool,
    help="Set to True for debugging / testing. Set to False for production.",
)
@click.option(
    "--randomizer",
    default=3,
    type=int,
    help="Set to the number of arb opportunities to pick from.",
)
@click.option(
    "--limit_bancor3_flashloan_tokens",
    default=True,
    type=bool,
    help="Only applies if arb_mode is `bancor_v3` or `b3_two_hop`. Set to False to allow the flashloan_tokens "
    "parameter to be overwritten as all tokens supported by Bancor v3.",
)
@click.option(
    "--default_min_profit_bnt",
    default=80,
    type=int,
    help="Set to the default minimum profit in BNT. This should be reasonably high to avoid losses from gas fees.",
)
@click.option(
    "--timeout",
    default=None,
    type=int,
    help="Set to the timeout in seconds. Set to None for no timeout.",
)
@click.option(
    "--target_tokens",
    default=None,
    type=str,
    help="A comma-separated string of tokens to target. Use None to target all tokens. Use `flashloan_tokens` to "
    "target only the flashloan tokens.",
)
@click.option(
    "--replay_from_block",
    default=None,
    type=int,
    help="Set to a block number to replay from that block. (For debugging / testing). A valid Tenderly account and "
    "configuration is required.",
)
@click.option(
    "--tenderly_fork_id",
    default=None,
    type=str,
    help="Set to a Tenderly fork id. (For debugging / testing). A valid Tenderly account and configuration is required.",
)
@click.option(
    "--tenderly_event_exchanges",
    default="",
    type=str,
    help="A comma-separated string of exchanges to include for the Tenderly event fetcher.",
)
@click.option(
    "--increment_time",
    default=1,
    type=int,
    help="If tenderly_fork_id is set, this is the number of seconds to increment the fork time by for each iteration.",
)
@click.option(
    "--increment_blocks",
    default=1,
    type=int,
    help="If tenderly_fork_id is set, this is the number of blocks to increment the block number by for each iteration.",
)
def main(
    cache_latest_only: bool,
    backdate_pools: bool,
    arb_mode: str,
    flashloan_tokens: str,
    n_jobs: int,
    exchanges: str,
    polling_interval: int,
    alchemy_max_block_fetch: int,
    static_pool_data_filename: str,
    reorg_delay: int,
    logging_path: str,
    loglevel: str,
    static_pool_data_sample_sz: str,
    use_cached_events: bool,
    run_data_validator: bool,
    randomizer: int,
    limit_bancor3_flashloan_tokens: bool,
    default_min_profit_bnt: int,
    timeout: int,
    target_tokens: str,
    replay_from_block: int,
    tenderly_fork_id: str,
    tenderly_event_exchanges: str,
    increment_time: int,
    increment_blocks: int,
):
    """
    The main entry point of the program. It sets up the configuration, initializes the web3 and Base objects,
    adds initial pools to the Base and then calls the `run` function.

    Args:
        cache_latest_only (bool): Whether to cache only the latest events or not.
        backdate_pools (bool): Whether to backdate pools or not. Set to False for quicker testing runs.
        arb_mode (str): The arbitrage mode to use.
        flashloan_tokens (str): Comma seperated list of tokens that the bot can use for flash loans.
        n_jobs (int): The number of jobs to run in parallel.
        exchanges (str): A comma-separated string of exchanges to include.
        polling_interval (int): The time interval at which the bot polls for new events.
        alchemy_max_block_fetch (int): The maximum number of blocks to fetch in a single request.
        static_pool_data_filename (str): The filename of the static pool data to read from.
        reorg_delay (int): The number of blocks to wait to avoid reorgs.
        logging_path (str): The logging path.
        loglevel (str): The logging level.
        static_pool_data_sample_sz (str): The sample size of the static pool data.
        use_cached_events (bool): Whether to use cached events or not.
        run_data_validator (bool): Whether to run the data validator or not.
        randomizer (int): The number of arb opportunities to randomly pick from, sorted by expected profit.
        limit_bancor3_flashloan_tokens (bool): Whether to limit the flashloan tokens to the ones supported by Bancor v3 or not.
        default_min_profit_bnt (int): The default minimum profit in BNT.
        timeout (int): The timeout in seconds.
        target_tokens (str): A comma-separated string of tokens to target. Use None to target all tokens. Use `flashloan_tokens` to target only the flashloan tokens.
        replay_from_block (int): The block number to replay from. (For debugging / testing)
        tenderly_fork_id (str): The Tenderly fork id. (For debugging / testing)
        tenderly_event_exchanges (str): A comma-separated string of exchanges to include for the Tenderly event fetcher.
        increment_time (int): If tenderly_fork_id is set, this is the number of seconds to increment the fork time by for each iteration.
        increment_blocks (int): If tenderly_fork_id is set, this is the number of blocks to increment the block number by for each iteration.

    """

    if replay_from_block or tenderly_fork_id:
        polling_interval, reorg_delay, use_cached_events = handle_replay_from_block(
            polling_interval
        )

    # Set config
    loglevel = get_loglevel(loglevel)

    # Initialize the config object
    cfg = get_config(
        default_min_profit_bnt,
        limit_bancor3_flashloan_tokens,
        loglevel,
        logging_path,
        tenderly_fork_id,
    )

    # Format the flashloan tokens
    flashloan_tokens = handle_flashloan_tokens(cfg, flashloan_tokens)

    # Search the logging directory for the latest timestamped folder
    logging_path = find_latest_timestamped_folder(logging_path)

    # Format the target tokens
    target_tokens = handle_target_tokens(cfg, flashloan_tokens, target_tokens)

    # Format the exchanges
    exchanges = handle_exchanges(cfg, exchanges)

    # Format the tenderly event exchanges
    tenderly_event_exchanges = handle_exchanges(cfg, tenderly_event_exchanges)

    # Log the run configuration
    cfg.logger.info(
        f"""
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        Starting fastlane bot with the following configuration:
        
        cache_latest_only: {cache_latest_only}
        backdate_pools: {backdate_pools}
        arb_mode: {arb_mode}
        flashloan_tokens: {flashloan_tokens}
        n_jobs: {n_jobs}
        exchanges: {exchanges}
        polling_interval: {polling_interval}
        alchemy_max_block_fetch: {alchemy_max_block_fetch}
        static_pool_data_filename: {static_pool_data_filename}
        reorg_delay: {reorg_delay}
        logging_path: {logging_path}
        loglevel: {loglevel}
        static_pool_data_sample_sz: {static_pool_data_sample_sz}
        use_cached_events: {use_cached_events}
        run_data_validator: {run_data_validator}
        randomizer: {randomizer}
        limit_bancor3_flashloan_tokens: {limit_bancor3_flashloan_tokens}
        default_min_profit_bnt: {default_min_profit_bnt}
        timeout: {timeout}
        target_tokens: {target_tokens}
        replay_from_block: {replay_from_block}
        tenderly_fork_id: {tenderly_fork_id}
        tenderly_event_exchanges: {tenderly_event_exchanges}
        increment_time: {increment_time}
        increment_blocks: {increment_blocks}
        
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        """
    )

    # Get the static pool data, tokens and uniswap v2 event mappings
    static_pool_data, tokens, uniswap_v2_event_mappings = get_static_data(
        cfg, exchanges, static_pool_data_filename, static_pool_data_sample_sz
    )

    target_token_addresses = handle_target_token_addresses(
        static_pool_data, target_tokens
    )

    # Break if timeout is hit to test the bot flags
    if timeout == 1:
        cfg.logger.info("Timeout to test the bot flags")
        return

    if tenderly_fork_id:
        w3_tenderly = Web3(
            HTTPProvider(f"https://rpc.tenderly.co/fork/{tenderly_fork_id}")
        )
    else:
        w3_tenderly = None

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
        tenderly_fork_id=tenderly_fork_id,
        tenderly_event_exchanges=tenderly_event_exchanges,
        w3_tenderly=w3_tenderly,
    )

    # Add initial pool data to the manager
    add_initial_pool_data(cfg, mgr, n_jobs)

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
        logging_path,
        use_cached_events,
        run_data_validator,
        randomizer,
        timeout,
        target_tokens,
        replay_from_block,
        tenderly_fork_id,
        increment_time,
        increment_blocks,
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
    logging_path: str,
    use_cached_events: bool,
    run_data_validator: bool,
    randomizer: int,
    timeout: int,
    target_tokens: List[str] or None,
    replay_from_block: int or None,
    tenderly_fork_id: str or None,
    increment_time: int,
    increment_blocks: int,
) -> None:
    """
    The main function that drives the logic of the program. It uses helper functions to handle specific tasks.

    Args:
        cache_latest_only (bool): Whether to cache only the latest events or not.
        backdate_pools (bool): Whether to backdate pools or not. Set to False for quicker testing runs.
        mgr (Base): The manager object that is responsible for handling events and updating pools.
        n_jobs (int): The number of jobs to run in parallel.
        polling_interval (int): The time interval at which the bot polls for new events.
        alchemy_max_block_fetch (int): The maximum number of blocks to fetch in a single request.
        arb_mode (str): The arbitrage mode to use.
        flashloan_tokens (List[str]): List of tokens that the bot can use for flash loans.
        reorg_delay (int): The number of blocks to wait to avoid reorgs.
        logging_path (str): The path to the DBFS directory.
        use_cached_events (bool): Whether to use cached events or not.
        run_data_validator (bool): Whether to run the data validator or not.
        randomizer (bool): Whether to randomize the polling interval or not.
        timeout (int): The timeout for the polling interval.
        target_tokens (List[str]): List of tokens that the bot will target for arbitrage.
        replay_from_block (int): The block number to replay from. (For debugging / testing)
        tenderly_fork_id (str): The Tenderly fork id. (For debugging / testing)
        increment_time (int): If tenderly_fork_id is set, this is the number of seconds to increment the fork time by for each iteration.
        increment_blocks (int): If tenderly_fork_id is set, this is the number of blocks to increment the block number by for each iteration.
    """

    bot = tenderly_uri = forked_from_block = None
    loop_idx = last_block = 0
    start_timeout = time.time()
    mainnet_uri = mgr.cfg.w3.provider.endpoint_uri
    forks_to_cleanup = []
    while True:
        # try:

        # Save initial state of pool data to assert whether it has changed
        initial_state = mgr.pool_data.copy()

        # Get current block number, then adjust to the block number reorg_delay blocks ago to avoid reorgs
        start_block, replay_from_block = get_start_block(
            alchemy_max_block_fetch, last_block, mgr, reorg_delay, replay_from_block
        )

        # Get all events from the last block to the current block
        if not replay_from_block and not tenderly_fork_id:
            current_block = mgr.web3.eth.blockNumber - reorg_delay
        elif last_block == 0 and replay_from_block:
            current_block = replay_from_block - reorg_delay
        elif tenderly_fork_id:
            current_block = mgr.w3_tenderly.eth.blockNumber
        else:
            current_block = last_block + 1

        # Log the current start, end and last block
        mgr.cfg.logger.info(
            f"Fetching events from {start_block} to {current_block}... {last_block}"
        )

        # Set the network connection to Mainnet if replaying from a block
        mgr = set_network_to_mainnet_if_replay(
            last_block,
            loop_idx,
            mainnet_uri,
            mgr,
            replay_from_block,
            use_cached_events,
        )

        # Get the events
        latest_events = (
            get_cached_events(mgr, logging_path)
            if use_cached_events
            else get_latest_events(
                current_block,
                mgr,
                n_jobs,
                start_block,
                cache_latest_only,
                logging_path,
            )
        )

        if mgr.cfg.BANCOR_POL_NAME in mgr.exchanges:
            update_pools_from_contracts(
                mgr,
                n_jobs=n_jobs,
                rows_to_update=[
                    i
                    for i, pool_info in enumerate(mgr.pool_data)
                    if pool_info["exchange_name"] == mgr.cfg.BANCOR_POL_NAME
                ],
                current_block=current_block,
                token_address=True,
            )

        # Update the pools from the latest events
        update_pools_from_events(n_jobs, mgr, latest_events)

        # Set the network connection to Tenderly if replaying from a block
        mgr, tenderly_uri, forked_from_block = set_network_to_tenderly_if_replay(
            last_block,
            loop_idx,
            mgr,
            replay_from_block,
            tenderly_uri,
            use_cached_events,
            current_block,
            tenderly_fork_id,
        )

        # Handle the initial iteration (backdate pools, update pools from contracts, etc.)
        handle_initial_iteration(
            backdate_pools, current_block, last_block, mgr, n_jobs, start_block
        )

        multicall_every_iteration(current_block, mgr, n_jobs)

        # Update the last block number
        last_block = current_block

        # Write the pool data to disk
        write_pool_data_to_disk(cache_latest_only, logging_path, mgr, current_block)

        # Handle/remove duplicates in the pool data
        handle_duplicates(mgr)

        # Delete the bot (if it exists) to avoid memory leaks
        del bot

        # Re-initialize the bot
        bot = init_bot(mgr)

        # Verify that the state has changed
        verify_state_changed(bot, initial_state, mgr)

        # Verify that the minimum profit in BNT is respected
        verify_min_bnt_is_respected(bot, mgr)

        # Handle subsequent iterations
        handle_subsequent_iterations(
            arb_mode,
            bot,
            flashloan_tokens,
            polling_interval,
            randomizer,
            run_data_validator,
            target_tokens,
            loop_idx,
            logging_path,
            replay_from_block,
            tenderly_uri,
            forks_to_cleanup,
            mgr,
            forked_from_block,
        )

        # Increment the loop index
        loop_idx += 1

        # Sleep for the polling interval
        if not replay_from_block:
            time.sleep(polling_interval)

        # Check if timeout has been hit, and if so, break the loop for tests
        if timeout is not None and time.time() - start_timeout > timeout:
            mgr.cfg.logger.info("Timeout hit... stopping bot")
            break

        # Delete all Tenderly forks except the most recent one
        if replay_from_block and not tenderly_fork_id:
            break

        if loop_idx == 1:
            mgr.cfg.logger.info(
                """
                +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
                Finished first iteration of data sync. Now starting main loop arbitrage search.
                
                +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                """
            )

        if tenderly_fork_id:
            w3 = Web3(HTTPProvider(tenderly_uri))

            # Increase time and blocks
            params = [w3.toHex(increment_time)]  # number of seconds
            w3.provider.make_request(method="evm_increaseTime", params=params)

            params = [w3.toHex(increment_blocks)]  # number of blocks
            w3.provider.make_request(method="evm_increaseBlocks", params=params)

        # except Exception as e:
        #     mgr.cfg.logger.error(f"Error in main loop: {e}")
        #     time.sleep(polling_interval)


if __name__ == "__main__":
    main()

# %%
