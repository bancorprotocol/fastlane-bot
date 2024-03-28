import argparse
import logging
import os
import subprocess
import time
from typing import Dict

from web3 import Web3

from fastlane_bot.tests.deterministic.dtest_constants import KNOWN_UNABLE_TO_DELETE
from fastlane_bot.tests.deterministic.dtest_cmd_line_args import TestCommandLineArgs
from fastlane_bot.tests.deterministic.dtest_manager import TestManager
from fastlane_bot.tests.deterministic.dtest_pool import TestPool
from fastlane_bot.tests.deterministic.dtest_pool_params_builder import TestPoolParamsBuilder
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


def set_test_state_task(mgr: TestManager):
    """
    Sets the test state based on the static_pool_data_testing.csv file.

    Args:
        mgr: TestManager, the test manager
    """

    test_pools = TestPool.load_test_pools()

    pools = [
        TestPool(**test_pools_row[TestPool.attributes()].to_dict())
        for index, test_pools_row in test_pools.iterrows()
    ]
    pools = [pool for pool in pools if pool.is_supported]
    builder = TestPoolParamsBuilder(mgr.w3)
    builder.update_pools_by_exchange(mgr.args, builder, pools, mgr.w3)


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
    if args.delete_old_logs:
        test_manager.delete_old_logs(args)

    if args.task == "set_test_state":
        set_test_state_task(test_manager)
    elif args.task == "get_carbon_strategies_and_delete":
        get_carbon_strategies_and_delete_task(test_manager, args)
    elif args.task == "run_tests_on_mode":
        _extracted_run_tests_on_mode(test_manager, args)
    elif args.task == "end_to_end":
        get_carbon_strategies_and_delete_task(test_manager, args)
        set_test_state_task(test_manager)
        _extracted_run_tests_on_mode(test_manager, args)
    else:
        raise ValueError(f"Task {args.task} not recognized")


def _extracted_run_tests_on_mode(test_manager: TestManager, args: argparse.Namespace):
    """
    Extracted task handling.
    """
    test_strategies = test_manager.get_test_strategies(args)
    run_tests_on_mode_task(args, test_manager, test_strategies)