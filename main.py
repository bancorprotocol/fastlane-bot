# coding=utf-8
"""
This is the main file for configuring the bot and running the fastlane bot.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from fastlane_bot.events.event_gatherer import EventGatherer
from fastlane_bot.exceptions import ReadOnlyException, FlashloanUnavailableException
from fastlane_bot.events.version_utils import check_version_requirements
from fastlane_bot.pool_finder import PoolFinder
from fastlane_bot.tools.cpc import T

check_version_requirements(required_version="6.11.0", package_name="web3")

import os, sys
import time
from traceback import format_exc

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
    process_new_events,
    write_pool_data_to_disk,
    init_bot,
    get_cached_events,
    handle_subsequent_iterations,
    handle_duplicates,
    get_latest_events,
    get_start_block,
    set_network_to_mainnet_if_replay,
    set_network_to_tenderly_if_replay,
    get_current_block,
    handle_tenderly_event_exchanges,
    handle_static_pools_update,
    read_csv_file,
    handle_tokens_csv,
    check_and_approve_tokens,
)
from fastlane_bot.utils import find_latest_timestamped_folder
from run_blockchain_terraformer import terraform_blockchain
import argparse

load_dotenv()


def process_arguments(args):
    """
    Process and transform command line arguments.

    :param args: Namespace object containing command line arguments.
    :return: Processed arguments.
    """
    def is_true(x):
        return x.lower() == "true"

    def int_or_none(x):
        return int(x) if x else None

    # Define the transformations for each argument
    transformations = {
        "backdate_pools": is_true,
        "n_jobs": int,
        "polling_interval": int,
        "alchemy_max_block_fetch": int,
        "reorg_delay": int,
        "use_cached_events": is_true,
        "randomizer": int,
        "limit_bancor3_flashloan_tokens": is_true,
        "timeout": int_or_none,
        "replay_from_block": int_or_none,
        "increment_time": int,
        "increment_blocks": int,
        "pool_data_update_frequency": int,
        "self_fund": is_true,
        "read_only": is_true,
        "is_args_test": is_true,
        "pool_finder_period": int,
    }

    # Apply the transformations
    for arg, transform in transformations.items():
        if hasattr(args, arg):
            setattr(args, arg, transform(getattr(args, arg)))

    return args


def main(args: argparse.Namespace) -> None:
    """
    Main function for running the fastlane bot.

    Args:
        args: Command line arguments. See the argparse.ArgumentParser in the __main__ block for details.
    """
    args = process_arguments(args)

    if args.replay_from_block or args.tenderly_fork_id:
        if args.replay_from_block:
            assert args.replay_from_block > 0, "The block number to replay from must be greater than 0."
        args.polling_interval = 0
        args.reorg_delay = 0
        args.use_cached_events = False

    # Set config
    loglevel = get_loglevel(args.loglevel)

    # Initialize the config object
    cfg = get_config(
        args.default_min_profit_gas_token,
        args.limit_bancor3_flashloan_tokens,
        loglevel,
        args.logging_path,
        args.blockchain,
        args.flashloan_tokens,
        args.tenderly_fork_id,
        args.self_fund,
        args.rpc_url,
    )

    if not cfg.SELF_FUND and cfg.network.IS_NO_FLASHLOAN_AVAILABLE:
        raise FlashloanUnavailableException(f"Network: {cfg.NETWORK} does not support flashloans. "
                                            f"This network requires the use of your own funds by setting the configuration self_fund to True."
                                            f"Read the description of self_fund in the README before proceeding.")

    base_path = os.path.normpath(
        f"fastlane_bot/data/blockchain_data/{args.blockchain}/"
    )
    tokens_filepath = os.path.join(base_path, "tokens.csv")

    if not os.path.exists(tokens_filepath) and not args.read_only:
        df = pd.DataFrame(columns=["address", "decimals"])
        df.to_csv(tokens_filepath)
    elif not os.path.exists(tokens_filepath) and args.read_only:
        raise ReadOnlyException(tokens_filepath)

    tokens = read_csv_file(tokens_filepath)

    cfg.logger.info(f"tokens: {len(tokens)}, {tokens['address'].tolist()[0]}")

    # Format the flashloan tokens
    args.flashloan_tokens = handle_flashloan_tokens(cfg, args.flashloan_tokens, tokens)

    if args.self_fund:
        check_and_approve_tokens(cfg=cfg, tokens=args.flashloan_tokens)

    # Search the logging directory for the latest timestamped folder
    args.logging_path = find_latest_timestamped_folder(args.logging_path)

    # Format the target tokens
    args.target_tokens = handle_target_tokens(cfg, args.flashloan_tokens, args.target_tokens)

    # Format the exchanges
    exchanges = handle_exchanges(cfg, args.exchanges)

    # Format the tenderly event exchanges
    tenderly_event_exchanges = handle_tenderly_event_exchanges(
        cfg, args.tenderly_event_exchanges, args.tenderly_fork_id
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

            logging_path: {args.logging_path}
            arb_mode: {args.arb_mode}
            blockchain: {args.blockchain}
            default_min_profit_gas_token: {args.default_min_profit_gas_token}
            exchanges: {exchanges}
            flashloan_tokens: {args.flashloan_tokens}
            target_tokens: {args.target_tokens}
            use_specific_exchange_for_target_tokens: {args.use_specific_exchange_for_target_tokens}
            loglevel: {loglevel}
            backdate_pools: {args.backdate_pools}
            alchemy_max_block_fetch: {args.alchemy_max_block_fetch}
            static_pool_data_filename: {args.static_pool_data_filename}
            cache_latest_only: {args.cache_latest_only}
            n_jobs: {args.n_jobs}
            polling_interval: {args.polling_interval}
            reorg_delay: {args.reorg_delay}
            use_cached_events: {args.use_cached_events}
            randomizer: {args.randomizer}
            limit_bancor3_flashloan_tokens: {args.limit_bancor3_flashloan_tokens}
            timeout: {args.timeout}
            replay_from_block: {args.replay_from_block}
            tenderly_fork_id: {args.tenderly_fork_id}
            tenderly_event_exchanges: {tenderly_event_exchanges}
            increment_time: {args.increment_time}
            increment_blocks: {args.increment_blocks}
            pool_data_update_frequency: {args.pool_data_update_frequency}
            prefix_path: {args.prefix_path}
            self_fund: {args.self_fund}
            read_only: {args.read_only}
            pool_finder_period: {args.pool_finder_period}

            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            Copy and paste the above configuration when reporting a bug. Please also include the error message and stack trace below:

            <INSERT ERROR MESSAGE AND STACK TRACE HERE>

            Please direct all questions/reporting to the Fastlane Telegram channel: https://t.me/BancorDevelopers

            +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            """

    cfg.logging_header = logging_header
    cfg.logger.info(logging_header)

    if args.is_args_test:
        return

    # Get the static pool data, tokens and uniswap v2 event mappings
    (
        static_pool_data,
        tokens,
        uniswap_v2_event_mappings,
        uniswap_v3_event_mappings,
        solidly_v2_event_mappings,
    ) = get_static_data(
        cfg, exchanges, args.blockchain, args.static_pool_data_filename, args.read_only
    )

    # Break if timeout is hit to test the bot flags
    if args.timeout == 1:
        cfg.logger.info("Timeout to test the bot flags")
        return

    if args.tenderly_fork_id:
        w3_tenderly = Web3(
            HTTPProvider(f"https://rpc.tenderly.co/fork/{args.tenderly_fork_id}")
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
        alchemy_max_block_fetch=args.alchemy_max_block_fetch,
        uniswap_v2_event_mappings=uniswap_v2_event_mappings,
        uniswap_v3_event_mappings=uniswap_v3_event_mappings,
        solidly_v2_event_mappings=solidly_v2_event_mappings,
        tokens=tokens.to_dict(orient="records"),
        replay_from_block=args.replay_from_block,
        target_tokens=args.target_tokens,
        tenderly_fork_id=args.tenderly_fork_id,
        tenderly_event_exchanges=tenderly_event_exchanges,
        w3_tenderly=w3_tenderly,
        forked_exchanges=cfg.UNI_V2_FORKS + cfg.UNI_V3_FORKS + cfg.SOLIDLY_V2_FORKS,
        blockchain=args.blockchain,
        prefix_path=args.prefix_path,
        read_only=args.read_only,
    )

    # Add initial pool data to the manager
    add_initial_pool_data(cfg, mgr, args.n_jobs)

    # Run the main loop
    run(mgr, args)


def run(mgr, args, tenderly_uri=None) -> None:
    loop_idx = last_block = last_block_queried = total_iteration_time = 0
    start_timeout = time.time()
    mainnet_uri = mgr.cfg.w3.provider.endpoint_uri
    handle_static_pools_update(mgr)

    event_gatherer = EventGatherer(
        config=mgr.cfg,
        w3=mgr.w3_async,
        exchanges=mgr.exchanges,
        event_contracts=mgr.event_contracts
    )

    pool_finder = PoolFinder(
        carbon_forks=mgr.cfg.network.CARBON_V1_FORKS,
        uni_v3_forks=mgr.cfg.network.UNI_V3_FORKS,
        flashloan_tokens=args.flashloan_tokens,
        exchanges=mgr.exchanges,
        web3=mgr.web3,
        multicall_address=mgr.cfg.network.MULTICALL_CONTRACT_ADDRESS
    )

    while True:
        try:
            # ensure 'last_updated_block' is in pool_data for all pools
            for pool in mgr.pool_data:
                if "last_updated_block" not in pool:
                    pool["last_updated_block"] = last_block_queried

            # Get current block number, then adjust to the block number reorg_delay blocks ago to avoid reorgs
            start_block, replay_from_block = get_start_block(
                args.alchemy_max_block_fetch,
                last_block,
                mgr,
                args.reorg_delay,
                args.replay_from_block,
            )

            # Get all events from the last block to the current block
            current_block = get_current_block(
                last_block,
                mgr,
                args.reorg_delay,
                replay_from_block,
                args.tenderly_fork_id,
            )

            # Log the current start, end and last block
            mgr.cfg.logger.info(
                f"Fetching events from {start_block} to {current_block}... {last_block}"
            )

            # Set the network connection to Mainnet if replaying from a block
            set_network_to_mainnet_if_replay(
                last_block,
                loop_idx,
                mainnet_uri,
                mgr,
                replay_from_block,
                args.use_cached_events,
            )

            # Get the events
            latest_events = (
                get_cached_events(mgr, args.logging_path)
                if args.use_cached_events
                else get_latest_events(
                    current_block,
                    mgr,
                    args.n_jobs,
                    start_block,
                    args.cache_latest_only,
                    args.logging_path,
                    event_gatherer
                )
            )
            iteration_start_time = time.time()

            # Update the pools from the latest events
            update_pools_from_events(args.n_jobs, mgr, latest_events)

            # Update new pool events from contracts
            if len(mgr.pools_to_add_from_contracts) > 0:
                mgr.cfg.logger.info(
                    f"Adding {len(mgr.pools_to_add_from_contracts)} new pools from contracts, "
                    f"{len(mgr.pool_data)} total pools currently exist. Current block: {current_block}."
                )
                async_update_pools_from_contracts(mgr, current_block=current_block)
                mgr.pools_to_add_from_contracts = []

            # Increment the loop index
            loop_idx += 1

            # Set the network connection to Tenderly if replaying from a block
            tenderly_uri, forked_from_block = set_network_to_tenderly_if_replay(
                last_block=last_block,
                loop_idx=loop_idx,
                mgr=mgr,
                replay_from_block=replay_from_block,
                tenderly_uri=tenderly_uri,
                use_cached_events=args.use_cached_events,
                tenderly_fork_id=args.tenderly_fork_id,
            )

            # Handle the initial iteration (backdate pools, update pools from contracts, etc.)
            async_handle_initial_iteration(
                backdate_pools=args.backdate_pools,
                current_block=current_block,
                last_block=last_block,
                mgr=mgr,
                start_block=start_block,
            )

            # Run multicall every iteration
            multicall_every_iteration(current_block=current_block, mgr=mgr)

            # Update the last block number
            last_block = current_block

            if not mgr.read_only:
                # Write the pool data to disk
                write_pool_data_to_disk(
                    cache_latest_only=args.cache_latest_only,
                    logging_path=args.logging_path,
                    mgr=mgr,
                    current_block=current_block,
                )

            # Handle/remove duplicates in the pool data
            handle_duplicates(mgr)

            # Re-initialize the bot
            bot = init_bot(mgr)

            if args.use_specific_exchange_for_target_tokens is not None:
                target_tokens = bot.db.get_tokens_from_exchange(
                    exchange_name=args.use_specific_exchange_for_target_tokens
                )
                mgr.cfg.logger.info(
                    f"[main] Using only tokens in: {args.use_specific_exchange_for_target_tokens}, found {len(target_tokens)} tokens"
                )

            if not mgr.read_only:
                handle_tokens_csv(mgr, mgr.prefix_path)

            # Handle subsequent iterations
            handle_subsequent_iterations(
                arb_mode=args.arb_mode,
                bot=bot,
                flashloan_tokens=args.flashloan_tokens,
                randomizer=args.randomizer,
                target_tokens=args.target_tokens,
                loop_idx=loop_idx,
                logging_path=args.logging_path,
                replay_from_block=replay_from_block,
                tenderly_uri=tenderly_uri,
                mgr=mgr,
                forked_from_block=forked_from_block,
            )

            # Sleep for the polling interval
            if not replay_from_block and args.polling_interval > 0:
                mgr.cfg.logger.info(
                    f"[main] Sleeping for polling_interval={args.polling_interval} seconds..."
                )
                time.sleep(args.polling_interval)

            # Check if timeout has been hit, and if so, break the loop for tests
            if args.timeout is not None and time.time() - start_timeout > args.timeout:
                mgr.cfg.logger.info("[main] Timeout hit... stopping bot")
                break

            # Delete all Tenderly forks except the most recent one
            if replay_from_block and not args.tenderly_fork_id:
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

            if args.tenderly_fork_id:
                w3 = Web3(HTTPProvider(tenderly_uri))

                # Increase time and blocks
                params = [w3.to_hex(args.increment_time)]  # number of seconds
                w3.provider.make_request(method="evm_increaseTime", params=params)

                params = [w3.to_hex(args.increment_blocks)]  # number of blocks
                w3.provider.make_request(method="evm_increaseBlocks", params=params)

            if (
                    loop_idx % args.pool_data_update_frequency == 0
                    and args.pool_data_update_frequency != -1
            ):
                mgr.cfg.logger.info(
                    f"[main] Terraforming {args.blockchain}. Standby for oxygen levels."
                )
                sblock = (
                    (current_block - (current_block - last_block_queried))
                    if loop_idx > 1
                    else None
                )
                (
                    exchange_df,
                    uniswap_v2_event_mappings,
                    uniswap_v3_event_mappings,
                    solidly_v2_event_mappings,
                ) = terraform_blockchain(
                    network_name=args.blockchain,
                    web3=mgr.web3,
                    start_block=sblock,
                )
                mgr.uniswap_v2_event_mappings = dict(
                    uniswap_v2_event_mappings[["address", "exchange"]].values
                )
                mgr.uniswap_v3_event_mappings = dict(
                    uniswap_v3_event_mappings[["address", "exchange"]].values
                )
                mgr.solidly_v2_event_mappings = dict(
                    solidly_v2_event_mappings[["address", "exchange"]].values
                )

            if args.pool_finder_period > 0 and (loop_idx - 1) % args.pool_finder_period == 0:
                mgr.cfg.logger.info(f"Searching for unsupported Carbon pairs.")
                uni_v2, uni_v3, solidly_v2 = pool_finder.get_pools_for_unsupported_pairs(mgr.cfg, mgr.pool_data, arb_mode=args.arb_mode)
                process_new_events(uni_v2, mgr.uniswap_v2_event_mappings, f"fastlane_bot/data/blockchain_data/{args.blockchain}/uniswap_v2_event_mappings.csv", args.read_only)
                process_new_events(uni_v3, mgr.uniswap_v3_event_mappings, f"fastlane_bot/data/blockchain_data/{args.blockchain}/uniswap_v3_event_mappings.csv", args.read_only)
                process_new_events(solidly_v2, mgr.solidly_v2_event_mappings, f"fastlane_bot/data/blockchain_data/{args.blockchain}/solidly_v2_event_mappings.csv", args.read_only)
                handle_static_pools_update(mgr)
                mgr.cfg.logger.info(f"Number of pools added: {len(uni_v2) + len(uni_v3) + len(solidly_v2)}")

            last_block_queried = current_block

            total_iteration_time += time.time() - iteration_start_time
            mgr.cfg.logger.info(
                f"\n\n********************************************\n"
                f"Average Total iteration time for loop {loop_idx}: {total_iteration_time / loop_idx}\n"
                f"bot_version: {bot_version}\n"
                f"\n********************************************\n\n"
            )

        except Exception:
            mgr.cfg.logger.error(f"Error in main loop: {format_exc()}")
            mgr.cfg.logger.error(
                f"Please report this error to the Fastlane Telegram channel if it persists."
                f"{mgr.cfg.logging_header}"
            )
            time.sleep(args.polling_interval)
            if args.timeout is not None and time.time() - start_timeout > args.timeout:
                mgr.cfg.logger.info("Timeout hit... stopping bot")
                mgr.cfg.logger.info("[main] Timeout hit... stopping bot")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache_latest_only",
        default='True',
        help="Set to True for production. Set to False for testing / debugging",
    )
    parser.add_argument(
        "--backdate_pools",
        default='False',
        help="Set to False for faster testing / debugging",
    )
    parser.add_argument(
        "--static_pool_data_filename",
        default="static_pool_data",
        help="Filename of the static pool data.",
    )
    parser.add_argument(
        "--arb_mode",
        default="multi_pairwise_all",
        help="See arb_mode in bot.py",
        choices=[
            "multi_triangle",
            "multi_triangle_complete",
            "b3_two_hop",
            "multi_pairwise_pol",
            "multi_pairwise_all",
        ],
    )
    parser.add_argument(
        "--flashloan_tokens",
        default=f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC},{T.DAI},{T.USDC},{T.USDT},{T.WETH}",
        help="The --flashloan_tokens flag refers to those token denominations which the bot can take "
             "a flash loan in.",
    )
    parser.add_argument(
        "--n_jobs", default=-1, help="Number of parallel jobs to run"
    )
    parser.add_argument(
        "--exchanges",
        default="carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3",
        help="Comma separated external exchanges.",
    )
    parser.add_argument(
        "--polling_interval",
        default=1,
        help="Polling interval in seconds",
    )
    parser.add_argument(
        "--alchemy_max_block_fetch",
        default=2000,
        help="Max number of blocks to fetch from alchemy",
    )
    parser.add_argument(
        "--reorg_delay",
        default=0,
        help="Number of blocks delayed to avoid reorgs",
    )
    parser.add_argument(
        "--logging_path", default="", help="The logging path."
    )
    parser.add_argument(
        "--loglevel",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="The logging level.",
    )
    parser.add_argument(
        "--use_cached_events",
        default='False',
        help="Set to True for debugging / testing. Set to False for production.",
    )
    parser.add_argument(
        "--randomizer",
        default="3",
        help="Set to the number of arb opportunities to pick from.",
    )
    parser.add_argument(
        "--limit_bancor3_flashloan_tokens",
        default='True',
        help="Only applies if arb_mode is `bancor_v3` or `b3_two_hop`.",
    )
    parser.add_argument(
        "--default_min_profit_gas_token",
        default="0.01",
        help="Set to the default minimum profit in gas token.",
    )
    parser.add_argument(
        "--timeout",
        default=None,
        help="Set to the timeout in seconds. Set to None for no timeout.",
    )
    parser.add_argument(
        "--target_tokens",
        default=None,
        help="A comma-separated string of tokens to target.",
    )
    parser.add_argument(
        "--replay_from_block",
        default=None,
        help="Set to a block number to replay from that block.",
    )
    parser.add_argument(
        "--tenderly_fork_id",
        default=None,
        help="Set to a Tenderly fork id.",
    )
    parser.add_argument(
        "--tenderly_event_exchanges",
        default="pancakeswap_v2,pancakeswap_v3",
        help="A comma-separated string of exchanges to include for the Tenderly event fetcher.",
    )
    parser.add_argument(
        "--increment_time",
        default=1,
        help="If tenderly_fork_id is set, this is the number of seconds to increment the fork time by for each iteration.",
    )
    parser.add_argument(
        "--increment_blocks",
        default=1,
        help="If tenderly_fork_id is set, this is the number of blocks to increment the block number "
             "by for each iteration.",
    )
    parser.add_argument(
        "--blockchain",
        default="ethereum",
        help="A blockchain from the list. Blockchains not in this list do not have a deployed Fast Lane contract and are not supported.",
        choices=["ethereum", "coinbase_base", "fantom", "mantle", "linea", "sei"],
    )
    parser.add_argument(
        "--pool_data_update_frequency",
        default=-1,
        help="How frequently pool data should be updated, in main loop iterations.",
    )
    parser.add_argument(
        "--use_specific_exchange_for_target_tokens",
        default=None,
        help="If an exchange is specified, this will limit the scope of tokens to the tokens found on the exchange",
    )
    parser.add_argument(
        "--prefix_path",
        default="",
        help="Prefixes the path to the write folders (used for deployment)",
    )
    parser.add_argument(
        "--self_fund",
        default='False',
        help="If True, the bot will attempt to submit arbitrage transactions using funds in your "
             "wallet when possible.",
    )
    parser.add_argument(
        "--read_only",
        default='True',
        help="If True, the bot will skip all operations which write to disk. Use this flag if you're "
             "running the bot in an environment with restricted write permissions.",
    )
    parser.add_argument(
        "--is_args_test",
        default='False',
        help="The logging path.",
    )
    parser.add_argument(
        "--rpc_url",
        default=None,
        help="Custom RPC URL. If not set, the bot will use the default Alchemy RPC URL for the blockchain (if available).",
    )
    parser.add_argument(
        "--pool_finder_period",
        default=100,
        help="Searches for pools that can service Carbon strategies that do not have viable routes.",
    )

    # Process the arguments
    args = parser.parse_args()
    main(args)
