"""
Main logic for the Bancor Arbitrage Bot (FastLane) - run.py filescript

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""

import os
import time
import click
from decimal import Decimal
from brownie import Contract
from fastlane_bot.constants import ec
from fastlane_bot.networks import EthereumNetwork
from fastlane_bot.ui import FastLaneArbBotUI
from fastlane_bot.utils import check_paths


all_tokens = "".join(f"{tkn}-" for tkn in ec.SUPPORTED_TOKENS)
all_tokens = all_tokens[:-1]


@click.command()
@click.option("--base_path", default=os.path.normpath(os.getcwd()), type=str)
@click.option("--filetype", default=ec.DEFAULT_FILETYPE, type=str)
@click.option("--verbose", default=ec.VERBOSE, type=str)
@click.option("--n_jobs", default=ec.DEFAULT_N_JOBS, type=int)
@click.option("--number_of_retries", default=ec.DEFAULT_NUM_RETRIES, type=int)
@click.option("--execute_mode", default=ec.DEFAULT_EXECUTE_MODE, type=str)
@click.option("--exchanges", default=f"{ec.BANCOR_V3_NAME}-{ec.UNISWAP_V3_NAME}-{ec.UNISWAP_V2_NAME}-{ec.SUSHISWAP_V2_NAME}", type=str)
@click.option("--tokens", default=all_tokens, type=str)
@click.option("--min_profit", default=ec.DEFAULT_MIN_PROFIT, type=Decimal)
@click.option("--search_delay", default=ec.DEFAULT_SEARCH_DELAY, type=int)
@click.option("--network_name", default=ec.PRODUCTION_NETWORK_NAME, type=str)
@click.option(
    "--fastlane_contract_address", default=ec.FASTLANE_CONTRACT_ADDRESS, type=str
)
@click.option("--max_slippage", default=ec.DEFAULT_MAX_SLIPPAGE, type=Decimal)
@click.option("--tenderly_fork_id", default=ec.TENDERLY_FORK, type=str)
@click.option("--blocktime_deviation", default=ec.DEFAULT_BLOCKTIME_DEVIATION, type=int)
@click.option("--env", default="local", type=str)
def main(
        base_path: str,
        filetype: str,
        verbose: str,
        n_jobs: str,
        number_of_retries: str,
        execute_mode: str,
        exchanges: str,
        tokens: str,
        min_profit: Decimal,
        search_delay: int,
        network_name: str,
        fastlane_contract_address: str,
        max_slippage: Decimal,
        tenderly_fork_id: str,
        blocktime_deviation: int,
        env: str,
):
    """
    Takes a list of tkn addresses, collects liquidity pool data for each pool in Bancor, Uniswap V2, and Sushi,
    and calculates possible arbitrage in the path

    :param network_name: (str), name of the network to run the bot on
    :param fastlane_contract_address: (str), address of the arb contract
    :param search_delay: (int), number of seconds to wait between each search
    :param number_of_retries: (int), number of times to retry a failed request
    :param verbose: (str), logging level to use
    :param n_jobs: (int), number of jobs to run in parallel
    :param tokens: (list), list of tokens to run the bot on
    :param exchanges: (list), list of routes to run the bot on
    :param base_path: (str), path to save the output
    :param filetype: (str), options are ('csv', 'parquet')file type to save the output
    :param execute_mode: (str) options are ('search', 'execute', 'search_and_execute')
                        - search will only search for arbitrage opportunities,
                        - execute will only execute arbitrage opportunities,
                        - and search_and_execute will do both.
    :param min_profit: (float), minimum profit that needs to be found for a trade to be executed.
    :param max_slippage: (float), this is the maximum slippage percentage that is allowed for a trade to be executed.
    :param tenderly_fork_id: (str), the fork id to use for tenderly
    :param blocktime_deviation: (int), the maximum blocktime deviation allowed for a trade to be executed
    :param env: (str), the environment to run the bot on (local, dev, prod)
    """

    # Initialize the logger
    logger = ec.DEFAULT_LOGGER
    logger.info("Starting Arbitrage Bot")
    logger.info(f"network_name: {network_name}")

    # Parse the input parameters
    exchanges = exchanges.split("-")
    tokens = all_tokens if tokens == "all_tokens" else tokens
    tokens = tokens.split("-")
    n_jobs = int(n_jobs)
    number_of_retries = int(number_of_retries)
    blocktime_deviation = blocktime_deviation
    max_slippage = Decimal(str(max_slippage))

    # Check if the paths exist
    check_paths(base_path)

    ETH_PRIVATE_KEY = os.environ.get("ETH_PRIVATE_KEY_BE_CAREFUL")
    if env != "local":
        os.remove(".env")

    # Initialize the bot
    bot = FastLaneArbBotUI(
        base_path=base_path,
        filetype=filetype,
        verbose=verbose,
        n_jobs=n_jobs,
        number_of_retries=number_of_retries,
        execute_mode=execute_mode,
        min_profit=min_profit,
        search_delay=search_delay,
        network_name=network_name,
        fastlane_contract_address=fastlane_contract_address,
        max_slippage=max_slippage,
        tenderly_fork_id=tenderly_fork_id,
        blocktime_deviation=blocktime_deviation,
        web3=EthereumNetwork(
            network_id=ec.PRODUCTION_NETWORK
            if network_name == ec.PRODUCTION_NETWORK_NAME
            else ec.TEST_NETWORK,
            network_name=network_name,
            provider_url=ec.ETHEREUM_MAINNET_PROVIDER
            if network_name == ec.PRODUCTION_NETWORK_NAME
            else ec.TENDERLY_FORK_RPC,
            fastlane_contract_address=fastlane_contract_address,
        ).connect_network(),
        bancor_network_info=Contract.from_abi(
            name=ec.BANCOR_V3_NAME,
            address=ec.BANCOR_V3_NETWORK_INFO_ADDRESS,
            abi=ec.BANCOR_V3_NETWORK_INFO_ABI,
        ),
        _ETH_PRIVATE_KEY=ETH_PRIVATE_KEY,
    )

    bot.archive_trade_routes()
    bot.build_candidate_routes(tokens=tokens, exchanges=exchanges)

    initial_search = True
    while True:

        if network_name == "tenderly" and not initial_search:
            try:
                bot.execute_random_swaps(
                    num=5, web3=bot.web3, unique_pools=bot.unique_pools
                )
            except Exception as e:
                logger.warning(f"{e}")

        if execute_mode == "execute":
            bot.execute()

        elif execute_mode == "search":
            bot.search_candidate_routes(initial_search=initial_search)

        elif execute_mode == "search_and_execute":
            bot.search_candidate_routes(initial_search=initial_search)
            bot.execute()

        else:
            raise ValueError(f"Invalid execute_mode: {execute_mode}")

        time.sleep(search_delay)
        initial_search = False


if __name__ == "__main__":
    main()
