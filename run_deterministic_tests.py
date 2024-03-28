"""
This script is used to run deterministic tests on the Fastlane Bot.

The script is run from the command line with the following command: `python run_deterministic_tests.py --task <task>
--rpc_url <rpc_url> --network <network> --arb_mode <arb_mode>` --timeout_minutes <timeout_minutes> --from_block
<from_block> --create_new_testnet <create_new_testnet>

The `--task` argument specifies the task to run. The default task is `end_to_end`. The options are:
- `set_test_state`: Set the test state based on the static_pool_data_testing.csv file.
- `get_carbon_strategies_and_delete`: Get the carbon strategies and delete them.
- `run_tests_on_mode`: Run tests on the specified arbitrage mode.
- `end_to_end`: Run all of the above tasks.

The `--rpc_url` argument specifies the URL for the RPC endpoint.

The `--network` argument specifies the network to test. Default is `ethereum`. The options are:
- `ethereum`: Ethereum network.

The `--arb_mode` argument specifies the arbitrage mode to test. Default is `multi`. The options are:
- `single`: Single arbitrage mode.
- `multi`: Multi arbitrage mode.
- `triangle`: Triangle arbitrage mode.
- `multi_triangle`: Multi triangle arbitrage mode.

The `--timeout_minutes` argument specifies the timeout for the tests (in minutes). The default is 10 minutes.

The `--from_block` argument specifies the block number to start from. The default is 1000000.

The `--create_new_testnet` argument specifies whether to create a new testnet. The default is `False`. The options are:
- `True`: Create a new testnet.
- `False`: Do not create a new testnet.

All data used in the tests is stored in the `fastlane_bot/tests/_data` directory.

Note: This script uses the function `get_default_main_args` which returns the default command line arguments for the
`main` function in the `main.py` file. If these arguments change in main.py then they should be updated in the
`get_default_main_args` function as well.

(c) Copyright Bprotocol foundation 2024.
All rights reserved.
Licensed under MIT License.
"""
import argparse

from fastlane_bot.tests.deterministic.dtest_constants import (
    DEFAULT_FROM_BLOCK,
    TENDERLY_RPC_KEY,
)
from fastlane_bot.tests.deterministic.dtest_main import main

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Fastlane Bot")
    parser.add_argument(
        "--task",
        default="end_to_end",
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
    parser.add_argument(
        "--delete_old_logs",
        default="True",
        type=str,
        choices=["True", "False"],
    )

    args = parser.parse_args()
    args.delete_old_logs = args.delete_old_logs.lower() == "true"
    main(args)
