"""
This script is used to run deterministic tests on the Fastlane Bot.

The script is run from the command line with the following command:
`python run_deterministic_tests.py --task <task> --rpc_url <rpc_url> --network <network> --arb_mode <arb_mode>` --timeout_minutes <timeout_minutes>

The `--task` argument specifies the task to run. The options are:
- `set_test_state`: Set the test state based on the static_pool_data_testing.csv file.
- `get_carbon_strategies_and_delete`: Get the carbon strategies and delete them.
- `run_tests_on_mode`: Run tests on the specified arbitrage mode.
- `run_results_crosscheck`: Run the results crosscheck task.
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

The script uses the `fastlane_bot/tests/deterministic/constants.py` file to get the constants used in the tests.

The script uses the `fastlane_bot/tests/deterministic/utils.py` file to get the utility functions used in the tests.

All data used in the tests is stored in the `fastlane_bot/tests/deterministic/_data` directory.

Note: This script uses the function `get_default_main_args` which returns the default command line arguments for the
`main` function in the `main.py` file. If these arguments change in main.py then they should be updated in the
`get_default_main_args` function as well.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
import argparse
import importlib
import json
import os
from typing import Dict

import pandas as pd
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.tests.deterministic.constants import (
    DEFAULT_FROM_BLOCK, KNOWN_UNABLE_TO_DELETE,
    TENDERLY_RPC_KEY, TEST_FILE_DATA_DIR,
)
from fastlane_bot.tests.deterministic.main_args_mock import ArgumentParserMock
from fastlane_bot.tests.deterministic.test_tx_helper import TestTxHelper
from fastlane_bot.tests.deterministic.mgr_strategy import StrategyManager
from fastlane_bot.tests.deterministic.test_pool_params_builder import TestPoolParamsBuilder
from fastlane_bot.tests.deterministic.test_pool import TestPool
from fastlane_bot.tests.deterministic.test_strategy import TestStrategy
from fastlane_bot.tests.deterministic.mgr_web3 import Web3Manager


def set_test_state_task(w3: Web3):
    """
    Sets the test state based on the static_pool_data_testing.csv file.

    Args:
        w3: Web3 instance
    """
    print("\nRunning set_test_state_task...")

    # Import pool data
    # Set the default paths
    static_pool_data_testing_path = os.path.normpath(
        f"{TEST_FILE_DATA_DIR}/static_pool_data_testing.csv"
    )

    test_pools = pd.read_csv(static_pool_data_testing_path, dtype=str)
    pools = [
        TestPool(**test_pools_row[TestPool.attributes()].to_dict())
        for index, test_pools_row in test_pools.iterrows()
    ]
    pools = [pool for pool in pools if pool.is_supported]
    builder = TestPoolParamsBuilder(w3)

    # Handle each exchange_type differently for the required updates
    for pool in pools:
        # Set balances on pool
        pool.set_balance_via_faucet(w3, 0)
        pool.set_balance_via_faucet(w3, 1)

        # Set storage parameters
        update_params_dict = builder.get_update_params_dict(pool)

        # Update storage parameters
        for slot, params in update_params_dict.items():
            builder.set_storage_at(pool.pool_address, params)
            print(f"Updated storage parameters for {pool.pool_address} at slot {slot}")


def get_carbon_strategies_and_delete_task(
        w3: Web3, carbon_controller: Contract, from_block: int
):
    """
    Get the carbon strategies and delete them.

    Args:
        w3: Web3 instance
        carbon_controller: Contract, the carbon controller contract
        from_block: int, the block number to start from
    """
    print("\nRunning get_carbon_strategies_and_delete_task...")

    # Initialize the Strategy Manager
    strategy_mgr = StrategyManager(w3, carbon_controller)

    # Get the state of the carbon strategies
    (
        strategy_created_df,
        strategy_deleted_df,
        remaining_carbon_strategies,
    ) = strategy_mgr.get_state_of_carbon_strategies(from_block)

    # takes about 4 minutes per 100 strategies, so 450 ~ 18 minutes
    undeleted_strategies = strategy_mgr.delete_all_carbon_strategies(
        remaining_carbon_strategies
    )

    # These strategies cannot be deleted on Ethereum
    assert all(
        x in KNOWN_UNABLE_TO_DELETE for x in undeleted_strategies
    ), f"Strategies not deleted that are unknown: {undeleted_strategies}"


def run_tests_on_mode_task(
        args: argparse.Namespace,
        w3: Web3,
        carbon_controller: Contract,
        test_strategies: Dict,
):
    """
    Run tests on the specified arbitrage mode.

    Args:
        args: argparse.Namespace, the command line arguments
        w3: Web3 instance
        carbon_controller: Contract, the carbon controller contract
        test_strategies: Dict, the test strategies
    """
    print("\nRunning run_tests_on_mode_task...")

    # Initialize the Strategy Manager
    strategy_mgr = StrategyManager(w3, carbon_controller)

    # Get the default main args
    default_main_args = ArgumentParserMock()
    default_main_args.blockchain = args.network
    default_main_args.arb_mode = args.arb_mode
    default_main_args.timeout = args.timeout
    default_main_args.rpc_url = args.rpc_url

    # Print the default main args
    print(f"\n\n ********\n"
          f"default_main_args: {default_main_args}"
          f"\n ********\n\n")

    # Dynamically import the chosen script module
    script_module = importlib.import_module("main")

    # Run the main function in the script module
    script_module.main(default_main_args)

    # Mark the block that new strats were created
    strats_created_from_block = w3.eth.get_block_number()
    print(f"strats_created_from_block: {strats_created_from_block}")

    # populate a dictionary with all the relevant test strategies
    test_strategy_txhashs: Dict[TestStrategy] or Dict = {}
    for i, (key, args) in enumerate(test_strategies.items()):
        args["w3"] = w3
        test_strategy = TestStrategy(**args)
        test_strategy.get_token_approval(
            token_id=0, approval_address=carbon_controller.address
        )
        test_strategy.get_token_approval(
            token_id=1, approval_address=carbon_controller.address
        )
        tx_hash = strategy_mgr.create_strategy(test_strategy)
        test_strategy_txhashs[str(i + 1)] = {"txhash": tx_hash} if tx_hash else {}

    # Write the test strategy txhashs to a file
    test_strategy_txhashs_path = os.path.normpath(
        f"{TEST_FILE_DATA_DIR}/test_strategy_txhashs.json"
    )

    # Initialize the Strategy Manager
    strategy_mgr = StrategyManager(w3, carbon_controller)

    # Get the new state of the carbon strategies
    (
        strategy_created_df,
        strategy_deleted_df,
        remaining_carbon_strategies,
    ) = strategy_mgr.get_state_of_carbon_strategies(strats_created_from_block)

    new_strats_created = strategy_created_df["id"].to_list()
    print(f"There have been {len(new_strats_created)} new strategies created")

    print(f"strategy_created_df.columns: {list(strategy_created_df.columns)}")
    strategy_created_df.to_csv("strategy_created_df.csv")

    print("\nAdd the strategy ids...")
    for i in test_strategy_txhashs.keys():
        try:
            test_strategy_txhashs[i]['strategyid'] = strategy_created_df[
                strategy_created_df['transaction_hash'] == test_strategy_txhashs[i]['txhash']].id.values[0]
        except Exception as e:
            print(f"Add the strategy ids Error: {i}, {e}")

    with open(test_strategy_txhashs_path, "w") as f:
        json.dump(test_strategy_txhashs, f)
        f.close()


def run_results_crosscheck_task():
    """
    Run the results crosscheck task.
    """
    print("\nRunning run_results_crosscheck_task...")

    # Initialize the tx helper
    tx_helper = TestTxHelper()

    # Successful transactions on Tenderly are marked by status=1
    actually_txt_all_successful_txs = tx_helper.tx_scanner()
    print(f"len(actually_txt_all_successful_txs): {len(actually_txt_all_successful_txs)}")

    # print first 3 examples of actually_txt_all_successful_txs
    for i, tx in enumerate(actually_txt_all_successful_txs):
        print(f"\nactually_txt_all_successful_txs[{i}]: {tx}")
        if i == 2:
            break

    test_results_path = os.path.normpath(
        f"{TEST_FILE_DATA_DIR}/test_results.json"
    )
    with open(test_results_path) as f:
        test_datas = json.load(f)["test_data"]
        f.close()
        print(f"{len(test_datas.keys())} test results imported")

    test_strategy_txhashs_path = os.path.normpath(
        f"{TEST_FILE_DATA_DIR}/test_strategy_txhashs.json"
    )
    with open(test_strategy_txhashs_path) as f:
        test_strategy_txhashs = json.load(f)
        f.close()
        print(f"{len(test_strategy_txhashs.keys())} test strategy txhashs imported")

    # Loop over the created test strategies and verify test data
    for i in test_strategy_txhashs.keys():
        search_id = test_strategy_txhashs[i]["strategyid"]
        print(f"Evaluating test {search_id}")
        tx_data = tx_helper.get_tx_data(search_id, actually_txt_all_successful_txs)
        print(f"tx_data = {tx_data}")
        tx_helper.clean_tx_data(tx_data)
        test_data = test_datas[i]
        if tx_data == test_data:
            print(f"Test {i} PASSED")
        else:
            print(f"Test {i} FAILED")

    print("ALL TESTS PASSED")


def main(args: argparse.Namespace):
    """
    Main function for the script. Runs the specified task based on the command line arguments.

    Args:
        args: argparse.Namespace, the command line arguments
    """
    print(f"Running task: {args.task}")

    # Initialize the Web3 Manager
    w3_manager = Web3Manager(args.rpc_url)
    strategy_mgr = StrategyManager
    w3 = w3_manager.w3

    multichain_addresses_path = os.path.normpath(
        "fastlane_bot/data/multichain_addresses.csv"
    )

    # Get the Carbon Controller Address for the network
    carbon_controller_address = w3_manager.get_carbon_controller_address(
        multichain_addresses_path=multichain_addresses_path, network=args.network
    )

    # Initialize the Carbon Controller contract
    carbon_controller = w3_manager.get_carbon_controller(
        address=carbon_controller_address
    )

    if args.task == "set_test_state":
        set_test_state_task(w3)
    elif args.task == "get_carbon_strategies_and_delete":
        get_carbon_strategies_and_delete_task(w3, carbon_controller, args.from_block)
    elif args.task == "run_tests_on_mode":
        test_strategies = strategy_mgr.get_test_strategies()
        run_tests_on_mode_task(w3, carbon_controller, args.arb_mode, test_strategies)
    elif args.task == "run_results_crosscheck":
        run_results_crosscheck_task()
    elif args.task == "end_to_end":
        set_test_state_task(w3)
        get_carbon_strategies_and_delete_task(w3, carbon_controller, args.from_block)
        test_strategies = strategy_mgr.get_test_strategies()
        run_tests_on_mode_task(args, w3, carbon_controller, test_strategies)
        run_results_crosscheck_task()
    else:
        raise ValueError(f"Task {args.task} not recognized")


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
        default=4,
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
        default='False',
        type=str,
        help="Create a new testnet",
    )

    args = parser.parse_args()
    args.timeout = args.timeout_minutes * 60

    if args.create_new_testnet.lower() == 'true':
        uri, from_block = Web3Manager.create_new_testnet()
        print(f"uri: {uri}, from_block: {from_block}")

        args.rpc_url = uri

    main(args)
