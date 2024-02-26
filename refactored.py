import argparse
import importlib
import json
import os

import pandas as pd
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.tests.deterministic.constants import KNOWN_UNABLE_TO_DELETE
from fastlane_bot.tests.deterministic.utils import PoolParamsBuilder, StrategyManager, TestPool, Web3Manager, \
    get_default_main_args


def set_test_state_task(w3: Web3):
    """
    Sets the test state based on the static_pool_data_testing.csv file.
    
    Args:
        w3: Web3 instance
    """

    # Import pool data
    test_pools = pd.read_csv(args.static_pool_data_testing_path, dtype=str)
    pools = [TestPool(**test_pools_row[TestPool.attributes()].to_dict()) for index, test_pools_row in
             test_pools.iterrows()]
    pools = [pool for pool in pools if pool.is_supported]
    builder = PoolParamsBuilder(w3)

    # Handle each exchange_type differently for the required updates
    for pool in pools:

        # Set balances on pool
        pool.set_balance_via_faucet(w3, 0)
        pool.set_balance_via_faucet(w3, 1)

        # Set storage parameters
        update_params_dict = builder.get_update_params_dict(
            pool
        )

        # Update storage parameters
        for slot, params in update_params_dict.items():
            builder.set_storage_at(pool.pool_address, params)
            print(f"Updated storage parameters for {pool.pool_address} at slot {slot}")


def get_carbon_strategies_and_delete_task(w3: Web3, carbon_controller: Contract, from_block: int = 1000000):
    """
    Get the carbon strategies and delete them.

    Args:
        w3: Web3 instance
        carbon_controller: Contract, the carbon controller contract
        from_block: int, the block number to start from
    """
    strategy_mgr = StrategyManager(w3, carbon_controller)

    # Get the state of the carbon strategies
    (
        strategy_created_df,
        strategy_deleted_df,
        remaining_carbon_strategies
    ) = strategy_mgr.get_state_of_carbon_strategies(from_block)

    # takes about 4 minutes per 100 strategies, so 450 ~ 18 minutes
    undeleted_strategies = strategy_mgr.delete_all_carbon_strategies(remaining_carbon_strategies)

    # These strategies cannot be deleted on Ethereum
    assert all(
        x in KNOWN_UNABLE_TO_DELETE for x in undeleted_strategies
    ), f"Strategies not deleted that are unknown: {undeleted_strategies}"


def run_tests_on_mode_task(args: argparse.Namespace, w3: Web3, carbon_controller: Contract):

    # Dynamically import the chosen script module
    script_module = importlib.import_module('main')
    default_main_args = get_default_main_args()
    default_main_args.blockchain = args.network
    default_main_args.arb_mode = args.arb_mode
    default_main_args.timeout = 60 * 4  # 4 minutes
    script_module.main(default_main_args)

    test_strategies_path = os.path.normpath("fastlane_bot/tests/deterministic/test_strategies.json")
    with open(test_strategies_path) as file:
        test_strategies = json.load(file)['test_strategies']
        print(f"{len(test_strategies.keys())} test strategies imported")

    # Mark the block that new strats were created
    strats_created_from_block = w3.eth.get_block_number()
    print(f"strats_created_from_block: {strats_created_from_block}")

    # populate a dictionary with all the relevant test strategies
    test_strategy_txhashs = {}
    for i in range(1,len(test_strategies.keys())+1):
        i = str(i)
        test_strategy = test_strategies[i]
        get_token_approval(w3, test_strategy['token0'], carbon_controller.address, test_strategy['wallet'])
        get_token_approval(w3, test_strategy['token1'], carbon_controller.address, test_strategy['wallet'])
        txhash = createStrategy_fromTestDict(w3, carbon_controller, test_strategy)
        test_strategy_txhashs[i] = {}
        test_strategy_txhashs[i]['txhash'] = txhash


def main(args: argparse.Namespace):
    """
    Main function for the script. Runs the specified task based on the command line arguments.
    
    Args:
        args: argparse.Namespace, the command line arguments
    """
    # Initialize the Web3 Manager
    w3_manager = Web3Manager(args.rpc_url)
    w3 = w3_manager.w3

    # Get the Carbon Controller Address for the network
    carbon_controller_address = w3_manager.get_carbon_controller_address(
        multichain_addresses_path=args.multichain_addresses_path, network=args.network
    )

    # Initialize the Carbon Controller contract
    carbon_controller = w3_manager.get_carbon_controller(
        address=carbon_controller_address
    )

    if args.task == "set_test_state":
        set_test_state_task(w3)
    elif args.task == "get_carbon_strategies_and_delete":
        get_carbon_strategies_and_delete_task(w3, carbon_controller)
    elif args.task == "run_tests_on_mode":
        run_tests_on_mode_task(w3, carbon_controller, args.arb_mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fastlane Bot")
    parser.add_argument(
        "--static_pool_data_testing_path",
        default="fastlane_bot/data/blockchain_data/ethereum/static_pool_data_testing.csv",
        type=str,
        help="Path to the static pool data for testing",
    )
    parser.add_argument(
        "--rpc_url",
        default="https://virtual.mainnet.rpc.tenderly.co/fb866397-29bd-4886-8406-a2cc7b7c5b1f",
        type=str,
        help="URL for the RPC endpoint",
    )
    parser.add_argument(
        "--multichain_addresses_path",
        default="fastlane_bot/data/multichain_addresses.csv",
        type=str,
        help="Path to the multichain addresses",
    )
    parser.add_argument(
        "--network", default="ethereum", type=str, help="Network to use",
        choices=["ethereum"],
    )
    parser.add_argument(
        "--task",
        default="update_pool_params",
        type=str,
        choices=["set_test_state", "get_carbon_strategies_and_delete", "run_tests_on_mode"],
        help="Task to run",
    )
    parser.add_argument(
        "--arb_mode",
        default="multi",
        type=str,
        choices=["single", "multi", "triangle", "multi_triangle"],
        help="Arbitrage mode to test",
    )

    args = parser.parse_args()
    main(args)
