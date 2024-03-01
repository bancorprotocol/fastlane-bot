"""
This script is used to run deterministic tests on the Fastlane Bot.

The script is run from the command line with the following command: `python run_deterministic_tests.py --task <task>
--rpc_url <rpc_url> --network <network> --arb_mode <arb_mode>` --timeout_minutes <timeout_minutes> --from_block
<from_block> --create_new_testnet <create_new_testnet>

The `--task` argument specifies the task to run. The options are:
- `set_test_state`: Set the test state based on the static_pool_data_testing.csv file.
- `get_carbon_strategies_and_delete`: Get the carbon strategies and delete them.
- `run_tests_on_mode`: Run tests on the specified arbitrage mode.
- `end_to_end`: Run all of the above tasks.

The `--rpc_url` argument specifies the URL for the RPC endpoint.

The `--network` argument specifies the network to test. The options are:
- `ethereum`: Ethereum network.

The `--arb_mode` argument specifies the arbitrage mode to test. The options are:
- `single`: Single arbitrage mode.
- `multi`: Multi arbitrage mode.
- `triangle`: Triangle arbitrage mode.
- `multi_triangle`: Multi triangle arbitrage mode.

The `--timeout_minutes` argument specifies the timeout for the tests (in minutes).

The `--from_block` argument specifies the block number to start from.

The `--create_new_testnet` argument specifies whether to create a new testnet. The options are:
- `True`: Create a new testnet.
- `False`: Do not create a new testnet.

The script uses the `fastlane_bot/tests/deterministic/dtest_constants.py` file to get the constants used in the tests.

The script uses the `fastlane_bot/tests/deterministic/utils.py` file to get the utility functions used in the tests.

All data used in the tests is stored in the `fastlane_bot/tests/deterministic/_data` directory.

Note: This script uses the function `get_default_main_args` which returns the default command line arguments for the
`main` function in the `main.py` file. If these arguments change in main.py then they should be updated in the
`get_default_main_args` function as well.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import argparse
import logging
import os
import subprocess
import time
from typing import Dict

from web3 import Web3

from fastlane_bot.tests.deterministic.dtest_constants import (
    DEFAULT_FROM_BLOCK,
    KNOWN_UNABLE_TO_DELETE,
    TENDERLY_RPC_KEY,
    TestCommandLineArgs,
)
from fastlane_bot.tests.deterministic.dtest_manager import TestManager
from fastlane_bot.tests.deterministic.dtest_pool import TestPool
from fastlane_bot.tests.deterministic.dtest_pool_params_builder import (
    TestPoolParamsBuilder,
)
from fastlane_bot.tests.deterministic.dtest_tx_helper import TestTxHelper


def get_logger(args: argparse.Namespace) -> logging.Logger:
    """
    Get the logger for the script.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(args.loglevel)
    logger.handlers.clear()  # Clear existing handlers to avoid duplicate logging

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(args.loglevel)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(ch)

    return logger


def set_test_state_task(w3: Web3):
    """
    Sets the test state based on the static_pool_data_testing.csv file.

    Args:
        w3: Web3 instance
    """
    args.logger.info("\nRunning set_test_state_task...")

    test_pools = TestPool.load_test_pools()

    pools = [
        TestPool(**test_pools_row[TestPool.attributes()].to_dict())
        for index, test_pools_row in test_pools.iterrows()
    ]
    pools = [pool for pool in pools if pool.is_supported]
    builder = TestPoolParamsBuilder(w3)
    builder.update_pools_by_exchange(args, builder, pools, w3)


def get_carbon_strategies_and_delete_task(
    test_manager: TestManager, args: argparse.Namespace
):
    """
    Get the carbon strategies and delete them.

    Args:
        test_manager: TestManager, the test manager
        args: argparse.Namespace, the command line arguments
    """
    args.logger.info("\nRunning get_carbon_strategies_and_delete_task...")

    # Get the state of the carbon strategies
    (
        strategy_created_df,
        strategy_deleted_df,
        remaining_carbon_strategies,
    ) = test_manager.get_state_of_carbon_strategies(args, args.from_block)

    # takes about 4 minutes per 100 strategies, so 450 ~ 18 minutes
    undeleted_strategies = test_manager.delete_all_carbon_strategies(
        args, remaining_carbon_strategies
    )

    # These strategies cannot be deleted on Ethereum
    assert all(
        x in KNOWN_UNABLE_TO_DELETE for x in undeleted_strategies
    ), f"Strategies not deleted that are unknown: {undeleted_strategies}"


def run_tests_on_mode_task(
    args: argparse.Namespace,
    test_manager: TestManager,
    test_strategies: Dict,
):
    """
    Run tests on the specified arbitrage mode.

    Args:
        args: argparse.Namespace, the command line arguments
        test_manager: TestManager, the test manager
        test_strategies: Dict, the test strategies
    """
    args.logger.info("\nRunning run_tests_on_mode_task...")

    # Get the default main.py CL args, then overwrite based on the current command line args
    default_main_args = test_manager.overwrite_command_line_args(args)

    # Print the default main args
    args.logger.debug(f"command-line args: {default_main_args}")

    # Run the main.py script with the default main args
    cmd_args = ["python", "main.py"] + TestCommandLineArgs.args_to_command_line(
        default_main_args
    )
    proc = subprocess.Popen(cmd_args)
    time.sleep(3)
    most_recent_pool_data_path = test_manager.get_most_recent_pool_data_path(args)

    # Wait for the main.py script to create the latest_pool_data.json file
    while not os.path.exists(most_recent_pool_data_path):
        time.sleep(3)
        args.logger.debug("Waiting for pool data...")

    strats_created_from_block = test_manager.get_strats_created_from_block(
        args, test_manager.w3
    )

    # Approve and create the strategies
    test_strategy_txhashs = test_manager.approve_and_create_strategies(
        args, test_strategies, strats_created_from_block
    )

    # Write the strategy txhashs to a json file
    test_manager.write_strategy_txhashs_to_json(test_strategy_txhashs)

    # Run the results crosscheck task
    run_results_crosscheck_task(args, proc)


def run_results_crosscheck_task(args, proc: subprocess.Popen):
    """
    Run the results crosscheck task.

    Args:
        args: argparse.Namespace, the command line arguments
        proc: subprocess.Popen, the process
    """
    args.logger.info("\nRunning run_results_crosscheck_task...")

    # Initialize the tx helper
    tx_helper = TestTxHelper()

    # Wait for the transactions to be completed
    test_strategy_txhashs = tx_helper.wait_for_txs(args)

    # Scan for successful transactions on Tenderly which are marked by status=1
    actual_txs = tx_helper.tx_scanner(args)
    # tx_helper.log_txs(actual_txs, args)
    expected_txs = tx_helper.load_json_file("test_results.json", args)

    results_description = tx_helper.log_results(
        args, actual_txs, expected_txs, test_strategy_txhashs
    )
    proc.terminate()
    for k, v in results_description.items():
        args.logger.info(f"{k}: {v}")


def main(args: argparse.Namespace):
    """
    Main function for the script. Runs the specified task based on the command line arguments.

    Args:
        args: argparse.Namespace, the command line arguments
    """

    # Set up the logger
    args.logger = get_logger(args)
    args.logger.info(f"Running task: {args.task}")

    # Set the timeout in seconds
    args.timeout = args.timeout_minutes * 60

    if str(args.create_new_testnet).lower() == "true":
        uri, from_block = TestManager.create_new_testnet()
        args.rpc_url = uri

    # Initialize the Web3 Manager
    test_manager = TestManager(args=args)
    test_manager.delete_old_logs(args)

    if args.task == "set_test_state":
        set_test_state_task(test_manager.w3)
    elif args.task == "get_carbon_strategies_and_delete":
        get_carbon_strategies_and_delete_task(test_manager, args)
    elif args.task == "run_tests_on_mode":
        _extracted_task_handling(test_manager, args)
    elif args.task == "end_to_end":
        get_carbon_strategies_and_delete_task(test_manager, args)
        set_test_state_task(test_manager.w3)
        _extracted_task_handling(test_manager, args)
    else:
        raise ValueError(f"Task {args.task} not recognized")


def _extracted_task_handling(test_manager: TestManager, args: argparse.Namespace):
    """
    Extracted task handling.
    """
    test_strategies = test_manager.get_test_strategies(args)
    run_tests_on_mode_task(args, test_manager, test_strategies)


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Fastlane Bot")
    parser.add_argument(
        "--task",
        default="update_pool_params",
        type=str,
        choices=[
            "set_test_state",
            "get_carbon_strategies_and_delete",
            "run_tests_on_mode",
            "run_results_crosscheck",
            "end_to_end",
        ],
        help="Task to run",
    )
    parser.add_argument(
        "--rpc_url",
        default=f"https://virtual.mainnet.rpc.tenderly.co/{TENDERLY_RPC_KEY}",
        type=str,
        help="URL for the RPC endpoint",
    )
    parser.add_argument(
        "--network",
        default="ethereum",
        type=str,
        help="Network to test",
        choices=["ethereum"],  # TODO: add support for other networks
    )
    parser.add_argument(
        "--arb_mode",
        default="multi",
        type=str,
        choices=["single", "multi", "triangle", "multi_triangle"],
        help="Arbitrage mode to test",
    )
    parser.add_argument(
        "--timeout_minutes",
        default=10,
        type=int,
        help="Timeout for the tests (in minutes)",
    )
    parser.add_argument(
        "--from_block",
        default=DEFAULT_FROM_BLOCK,
        type=int,
        help="Replay from block",
    )
    parser.add_argument(
        "--create_new_testnet",
        default="False",
        type=str,
        help="Create a new testnet",
    )
    parser.add_argument(
        "--loglevel",
        default="DEBUG",
        type=str,
        help="Logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    args = parser.parse_args()
    main(args)
