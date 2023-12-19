# coding=utf-8
"""
This is the main file for configuring the bot and running the fastlane bot.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from fastlane_bot.events.version_utils import check_version_requirements
from fastlane_bot.tools.cpc import T

check_version_requirements(required_version="6.11.0", package_name="web3")

import os, sys
import time
from typing import List

import click
import pandas as pd
from dotenv import load_dotenv
from web3 import Web3, HTTPProvider

from fastlane_bot import __version__ as bot_version
from fastlane_bot.events.async_backdate_utils import (
    async_handle_initial_iteration,
)
from fastlane_bot.events.async_event_update_utils import (
    async_update_pools_from_contracts,
)
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.events.multicall_utils import multicall_every_iteration
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
    get_latest_events,
    get_start_block,
    set_network_to_mainnet_if_replay,
    set_network_to_tenderly_if_replay,
    verify_min_bnt_is_respected,
    handle_target_token_addresses,
    handle_replay_from_block,
    get_current_block,
    handle_tenderly_event_exchanges,
    handle_static_pools_update,
    read_csv_file,
    handle_tokens_csv,
    get_tkn_symbols,
    check_and_approve_tokens,
)
from fastlane_bot.utils import find_latest_timestamped_folder
from run_blockchain_terraformer import terraform_blockchain


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
    default="multi_pairwise_all",
    help="See arb_mode in bot.py",
    type=click.Choice(
        [
            "single",
            "multi",
            "triangle",
            "multi_triangle",
            "b3_two_hop",
            "multi_pairwise_pol",
            "multi_pairwise_bal",
            "multi_pairwise_all",
        ]
    ),
)
@click.option(
    "--flashloan_tokens",
    default=f"{T.LINK},{T.ETH},{T.BNT},{T.WBTC}",
    type=str,
    help="The --flashloan_tokens flag refers to those token denominations which the bot can take a flash loan in. By "
    "default, these are [WETH, DAI, USDC, USDT, WBTC, BNT, NATIVE_ETH]. If you override the default to TKN, "
    "the search space is decreased for all modes, including the b3_two_hop mode (assuming that "
    "--limit_bancor3_flashloan_tokens=True).",
)
@click.option("--n_jobs", default=-1, help="Number of parallel jobs to run")
@click.option(
    "--exchanges",
    default="carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3",
    help="Comma separated external exchanges. Note that carbon_v1 and bancor_v3 must be included on Ethereum. To include known forks for Uniswap V2/3, use uniswap_v2_forks or uniswap_v3_forks",
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
    "--default_min_profit_gas_token",
    default="0.01",
    type=str,
    help="Set to the default minimum profit in gas token. This should be reasonably high to avoid losses from gas fees.",
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
    default="pancakeswap_v2,pancakeswap_v3",
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
@click.option(
    "--blockchain",
    default="ethereum",
    help="""A blockchain from the list. Blockchains not in this list do not have a deployed Fast Lane contract and 
    are not supported.""",
    type=click.Choice(["ethereum", "coinbase_base"]),
)
@click.option(
    "--pool_data_update_frequency",
    default=-1,
    type=int,
    help="How frequently pool data should be updated, in main loop iterations.",
)
@click.option(
    "--use_specific_exchange_for_target_tokens",
    default=None,
    type=str,
    help="If an exchange is specified, this will limit the scope of tokens to the tokens found on the exchange",
)
@click.option(
    "--prefix_path",
    default="",
    type=str,
    help="Prefixes the path to the write folders (used for deployment)",
)
@click.option(
    "--version_check_frequency",
    default=1,
    type=int,
    help="How frequently pool data should be updated, in main loop iterations.",
)
@click.option(
    "--self_fund",
    default=False,
    type=bool,
    help="If True, the bot will attempt to submit arbitrage transactions using funds in your wallet when possible.",
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
    use_cached_events: bool,
    run_data_validator: bool,
    randomizer: int,
    limit_bancor3_flashloan_tokens: bool,
    default_min_profit_gas_token: str,
    timeout: int,
    target_tokens: str,
    replay_from_block: int,
    tenderly_fork_id: str,
    tenderly_event_exchanges: str,
    increment_time: int,
    increment_blocks: int,
    blockchain: str,
    pool_data_update_frequency: int,
    use_specific_exchange_for_target_tokens: str,
    prefix_path: str,
    version_check_frequency: int,
    self_fund: bool,
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
        use_cached_events (bool): Whether to use cached events or not.
        run_data_validator (bool): Whether to run the data validator or not.
        randomizer (int): The number of arb opportunities to randomly pick from, sorted by expected profit.
        limit_bancor3_flashloan_tokens (bool): Whether to limit the flashloan tokens to the ones supported by Bancor v3 or not.
        default_min_profit_gas_token (str): The default minimum profit in the native gas token.
        timeout (int): The timeout in seconds.
        target_tokens (str): A comma-separated string of tokens to target. Use None to target all tokens. Use `flashloan_tokens` to target only the flashloan tokens.
        replay_from_block (int): The block number to replay from. (For debugging / testing)
        tenderly_fork_id (str): The Tenderly fork id. (For debugging / testing)
        tenderly_event_exchanges (str): A comma-separated string of exchanges to include for the Tenderly event fetcher.
        increment_time (int): If tenderly_fork_id is set, this is the number of seconds to increment the fork time by for each iteration.
        increment_blocks (int): If tenderly_fork_id is set, this is the number of blocks to increment the block number by for each iteration.
        blockchain (str): the name of the blockchain for which to run
        pool_data_update_frequency (int): the frequency to update static pool data, defined as the number of main loop cycles
        use_specific_exchange_for_target_tokens (str): use only the tokens that exist on a specific exchange
        prefix_path (str): prefixes the path to the write folders (used for deployment)
        version_check_frequency (int): how frequently the bot should check the version of the arb contract. 1 = every loop
        self_fund (bool): If False, the bot will use Flashloans to fund arbitrage trades. If True, the bot will use funds in the wallet to perform arbitrage trades.
    """

    if replay_from_block or tenderly_fork_id:
        polling_interval, reorg_delay, use_cached_events = handle_replay_from_block(
            replay_from_block
        )

    # Set config
    loglevel = get_loglevel(loglevel)

    # Initialize the config object
    cfg = get_config(
        default_min_profit_gas_token,
        limit_bancor3_flashloan_tokens,
        loglevel,
        logging_path,
        blockchain,
        flashloan_tokens,
        tenderly_fork_id,
        self_fund,
    )
    base_path = os.path.normpath(f"fastlane_bot/data/blockchain_data/{blockchain}/")
    tokens_filepath = os.path.join(base_path, "tokens.csv")
    if not os.path.exists(tokens_filepath):
        df = pd.DataFrame(
            columns=["address", "decimals"]
        )
        df.to_csv(tokens_filepath)
    tokens = read_csv_file(tokens_filepath)

    cfg.logger.info(f"tokens: {len(tokens)}, {tokens['address'].tolist()[0]}")

    flt_symbols = get_tkn_symbols(flashloan_tokens=flashloan_tokens, tokens=tokens)

    # Format the flashloan tokens
    flashloan_tokens = handle_flashloan_tokens(cfg, flashloan_tokens, tokens)

    if self_fund:
        check_and_approve_tokens(tokens=flashloan_tokens, cfg=cfg)

    # Search the logging directory for the latest timestamped folder
    logging_path = find_latest_timestamped_folder(logging_path)

    # Format the target tokens
    target_tokens = handle_target_tokens(cfg, flashloan_tokens, target_tokens)

    # Format the exchanges
    exchanges = handle_exchanges(cfg, exchanges)

    # Format the tenderly event exchanges
    tenderly_event_exchanges = handle_tenderly_event_exchanges(
        cfg, tenderly_event_exchanges, tenderly_fork_id
    )

    # Get the current python version used
    python_version = sys.version
    python_info = sys.version_info

    import platform

    os_system = platform.system()

    # Log the run configuration
    logging_header = f"""
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            Starting fastlane bot with the following configuration:
            bot_version: {bot_version}
            os_system: {os_system}
            python_version: {python_version}
            python_info: {python_info}

            logging_path: {logging_path}
            arb_mode: {arb_mode}
            blockchain: {blockchain}
            default_min_profit_gas_token: {default_min_profit_gas_token}
            exchanges: {exchanges}
            flashloan_tokens: {flashloan_tokens}
            target_tokens: {target_tokens}
            use_specific_exchange_for_target_tokens: {use_specific_exchange_for_target_tokens}
            loglevel: {loglevel}
            backdate_pools: {backdate_pools}
            alchemy_max_block_fetch: {alchemy_max_block_fetch}
            static_pool_data_filename: {static_pool_data_filename}
            cache_latest_only: {cache_latest_only}
            n_jobs: {n_jobs}
            polling_interval: {polling_interval}
            reorg_delay: {reorg_delay}
            use_cached_events: {use_cached_events}
            run_data_validator: {run_data_validator}
            randomizer: {randomizer}
            limit_bancor3_flashloan_tokens: {limit_bancor3_flashloan_tokens}
            timeout: {timeout}
            replay_from_block: {replay_from_block}
            tenderly_fork_id: {tenderly_fork_id}
            tenderly_event_exchanges: {tenderly_event_exchanges}
            increment_time: {increment_time}
            increment_blocks: {increment_blocks}
            pool_data_update_frequency: {pool_data_update_frequency}
            prefix_path: {prefix_path}
            version_check_frequency: {version_check_frequency}
            use_flashloans: {self_fund}

            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            Copy and paste the above configuration when reporting a bug. Please also include the error message and stack trace below:

            <INSERT ERROR MESSAGE AND STACK TRACE HERE>

            Please direct all questions/reporting to the Fastlane Telegram channel: https://t.me/BancorDevelopers

            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            """

    cfg.logging_header = logging_header
    cfg.logger.info(logging_header)

    # Get the static pool data, tokens and uniswap v2 event mappings
    (
        static_pool_data,
        tokens,
        uniswap_v2_event_mappings,
        uniswap_v3_event_mappings,
    ) = get_static_data(
        cfg,
        exchanges,
        blockchain,
        static_pool_data_filename,
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
        w3_async=cfg.w3_async,
        cfg=cfg,
        pool_data=static_pool_data.to_dict(orient="records"),
        SUPPORTED_EXCHANGES=exchanges,
        alchemy_max_block_fetch=alchemy_max_block_fetch,
        uniswap_v2_event_mappings=uniswap_v2_event_mappings,
        uniswap_v3_event_mappings=uniswap_v3_event_mappings,
        tokens=tokens.to_dict(orient="records"),
        replay_from_block=replay_from_block,
        target_tokens=target_token_addresses,
        tenderly_fork_id=tenderly_fork_id,
        tenderly_event_exchanges=tenderly_event_exchanges,
        w3_tenderly=w3_tenderly,
        forked_exchanges=cfg.UNI_V2_FORKS + cfg.UNI_V3_FORKS,
        blockchain=blockchain,
        prefix_path=prefix_path,
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
        blockchain,
        pool_data_update_frequency,
        use_specific_exchange_for_target_tokens,
        version_check_frequency
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
    blockchain: str,
    pool_data_update_frequency: int,
    use_specific_exchange_for_target_tokens: str,
    version_check_frequency: int,
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
        blockchain (str): the name of the blockchain for which to run
        pool_data_update_frequency (int): the frequency to update static pool data, defined as the number of main loop cycles
        use_specific_exchange_for_target_tokens (str): use only the tokens that exist on a specific exchange
        version_check_frequency (int): how frequently the bot should check the version of the arb contract. 1 = every loop

    """

    bot = tenderly_uri = forked_from_block = None
    loop_idx = last_block = 0
    start_timeout = time.time()
    mainnet_uri = mgr.cfg.w3.provider.endpoint_uri
    forks_to_cleanup = []
    last_block_queried = 0
    handle_static_pools_update(mgr)
    total_iteration_time = 0
    while True:

        try:

            # Save initial state of pool data to assert whether it has changed
            initial_state = mgr.pool_data.copy()

            # ensure 'last_updated_block' is in pool_data for all pools
            for idx, pool in enumerate(mgr.pool_data):
                if "last_updated_block" not in pool:
                    # print(f"pool missing 'last_updated_block` {pool}")
                    pool["last_updated_block"] = last_block_queried
                    mgr.pool_data[idx] = pool
                if not pool["last_updated_block"]:
                    # print(f"pool missing 'last_updated_block` {pool}")
                    pool["last_updated_block"] = last_block_queried
                    mgr.pool_data[idx] = pool

            # Get current block number, then adjust to the block number reorg_delay blocks ago to avoid reorgs
            start_block, replay_from_block = get_start_block(
                alchemy_max_block_fetch, last_block, mgr, reorg_delay, replay_from_block
            )

            # Get all events from the last block to the current block
            current_block = get_current_block(
                last_block, mgr, reorg_delay, replay_from_block, tenderly_fork_id
            )

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

            iteration_start_time = time.time()

            # Update the pools from the latest events
            update_pools_from_events(n_jobs, mgr, latest_events)

            # Update new pool events from contracts
            if len(mgr.pools_to_add_from_contracts) > 0:
                mgr.cfg.logger.info(
                    f"Adding {len(mgr.pools_to_add_from_contracts)} new pools from contracts,"
                    f"{len(mgr.pool_data)} total pools currently exist. Current block: {current_block}."
                )
                async_update_pools_from_contracts(mgr, current_block, logging_path)
                mgr.pools_to_add_from_contracts = []

            
            # Increment the loop index
            loop_idx += 1

            # Set the network connection to Tenderly if replaying from a block
            mgr, tenderly_uri, forked_from_block = set_network_to_tenderly_if_replay(
                last_block=last_block,
                loop_idx=loop_idx,
                mgr=mgr,
                replay_from_block=replay_from_block,
                tenderly_uri=tenderly_uri,
                use_cached_events=use_cached_events,
                tenderly_fork_id=tenderly_fork_id,
            )

            # Handle the initial iteration (backdate pools, update pools from contracts, etc.)
            async_handle_initial_iteration(
                backdate_pools=backdate_pools,
                current_block=current_block,
                last_block=last_block,
                mgr=mgr,
                start_block=start_block,
            )

            # Run multicall every iteration
            multicall_every_iteration(current_block=current_block, mgr=mgr)

            # Update the last block number
            last_block = current_block

            # Write the pool data to disk
            write_pool_data_to_disk(
                cache_latest_only=cache_latest_only,
                logging_path=logging_path,
                mgr=mgr,
                current_block=current_block,
            )

            # Handle/remove duplicates in the pool data
            handle_duplicates(mgr)

            # Delete the bot (if it exists) to avoid memory leaks
            del bot

            # Re-initialize the bot
            bot = init_bot(mgr)

            # Verify that the state has changed
            verify_state_changed(bot=bot, initial_state=initial_state, mgr=mgr)

            # Verify that the minimum profit in BNT is respected
            verify_min_bnt_is_respected(bot=bot, mgr=mgr)

            if use_specific_exchange_for_target_tokens is not None:
                target_tokens = bot.get_tokens_in_exchange(
                    exchange_name=use_specific_exchange_for_target_tokens
                )
                mgr.cfg.logger.info(
                    f"[main] Using only tokens in: {use_specific_exchange_for_target_tokens}, found {len(target_tokens)} tokens"
                )

            handle_tokens_csv(mgr, mgr.prefix_path)

            # Handle subsequent iterations
            handle_subsequent_iterations(
                arb_mode=arb_mode,
                bot=bot,
                flashloan_tokens=flashloan_tokens,
                polling_interval=polling_interval,
                randomizer=randomizer,
                run_data_validator=run_data_validator,
                target_tokens=target_tokens,
                loop_idx=loop_idx,
                logging_path=logging_path,
                replay_from_block=replay_from_block,
                tenderly_uri=tenderly_uri,
                mgr=mgr,
                forked_from_block=forked_from_block,
            )


            # Sleep for the polling interval
            if not replay_from_block and polling_interval > 0:
                mgr.cfg.logger.info(
                    f"[main] Sleeping for polling_interval={polling_interval} seconds..."
                )
                time.sleep(polling_interval)

            # Check if timeout has been hit, and if so, break the loop for tests
            if timeout is not None and time.time() - start_timeout > timeout:
                mgr.cfg.logger.info("[main] Timeout hit... stopping bot")
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
                params = [w3.to_hex(increment_time)]  # number of seconds
                w3.provider.make_request(method="evm_increaseTime", params=params)

                params = [w3.to_hex(increment_blocks)]  # number of blocks
                w3.provider.make_request(method="evm_increaseBlocks", params=params)
            if (
                    loop_idx % version_check_frequency == 0
                    and version_check_frequency != -1 and blockchain in "ethereum"
            ):
                # Check the version of the deployed arbitrage contract
                mgr.cfg.provider.check_version_of_arb_contract()
                mgr.cfg.logger.info(
                    f"[main] Checking latest version of Arbitrage Contract. Found version: {mgr.cfg.ARB_CONTRACT_VERSION}"
                )
            if (
                    loop_idx % pool_data_update_frequency == 0
                    and pool_data_update_frequency != -1
            ):

                mgr.cfg.logger.info(f"[main] Terraforming {blockchain}. Standby for oxygen levels.")
                sblock = (
                    (current_block - (current_block - last_block_queried))
                    if loop_idx > 1
                    else None
                )
                (
                    uniswap_v2_event_mappings,
                    uniswap_v3_event_mappings,
                ) = terraform_blockchain(
                    network_name=blockchain,
                    web3=mgr.web3,
                    start_block=sblock,
                )
                mgr.uniswap_v2_event_mappings = dict(
                    uniswap_v2_event_mappings[["address", "exchange"]].values
                )
                mgr.uniswap_v3_event_mappings = dict(
                    uniswap_v3_event_mappings[["address", "exchange"]].values
                )
                last_block_queried = current_block

                total_iteration_time += time.time() - iteration_start_time
                mgr.cfg.logger.info(
                    f"\n\n********************************************\n"
                    f"Average Total iteration time for loop {loop_idx}: {total_iteration_time / loop_idx}"
                    f"\n********************************************\n\n"
                )

        except Exception as e:
            mgr.cfg.logger.error(f"Error in main loop: {e}")
            mgr.cfg.logger.error(
                f"[main] Error in main loop: {e}. Continuing... "
                f"Please report this error to the Fastlane Telegram channel if it persists."
                f"{mgr.cfg.logging_header}"
            )
            time.sleep(polling_interval)
            if timeout is not None and time.time() - start_timeout > timeout:
                mgr.cfg.logger.info("Timeout hit... stopping bot")
                mgr.cfg.logger.info("[main] Timeout hit... stopping bot")
                break


if __name__ == "__main__":
    main()

# %%
