import argparse

from fastlane_bot.tools.cpc import T


def main():
    parser = argparse.ArgumentParser(description='Command-line tool options')

    parser.add_argument("--cache_latest_only", default=True, type=bool, help="Set to True for production. Set to False for testing / debugging")
    parser.add_argument("--backdate_pools", default=False, type=bool, help="Set to False for faster testing / debugging")
    parser.add_argument("--static_pool_data_filename", default="static_pool_data", help="Filename of the static pool data.")
    parser.add_argument("--arb_mode", default="multi_pairwise_all", help="See arb_mode in bot.py", choices=["single", "multi", "triangle", "multi_triangle", "b3_two_hop", "multi_pairwise_pol", "multi_pairwise_all"])
    parser.add_argument("--flashloan_tokens", default=f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC},{T.DAI},{T.USDC},{T.USDT},{T.WETH}", type=str, help="The --flashloan_tokens flag refers to those token denominations which the bot can take a flash loan in.")
    parser.add_argument("--n_jobs", default=-1, help="Number of parallel jobs to run")
    parser.add_argument("--exchanges", default="carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3", help="Comma separated external exchanges.")
    parser.add_argument("--polling_interval", default=1, help="Polling interval in seconds")
    parser.add_argument("--alchemy_max_block_fetch", default=2000, help="Max number of blocks to fetch from alchemy")
    parser.add_argument("--reorg_delay", default=0, help="Number of blocks delayed to avoid reorgs")
    parser.add_argument("--logging_path", default="", help="The logging path.")
    parser.add_argument("--loglevel", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="The logging level.")
    parser.add_argument("--use_cached_events", default=False, type=bool, help="Set to True for debugging / testing. Set to False for production.")
    parser.add_argument("--run_data_validator", default=False, type=bool, help="Set to True for debugging / testing. Set to False for production.")
    parser.add_argument("--randomizer", default=3, type=int, help="Set to the number of arb opportunities to pick from.")
    parser.add_argument("--limit_bancor3_flashloan_tokens", default=True, type=bool, help="Only applies if arb_mode is `bancor_v3` or `b3_two_hop`.")
    parser.add_argument("--default_min_profit_gas_token", default="0.01", type=str, help="Set to the default minimum profit in gas token.")
    parser.add_argument("--timeout", default=None, type=int, help="Set to the timeout in seconds. Set to None for no timeout.")
    parser.add_argument("--target_tokens", default=None, type=str, help="A comma-separated string of tokens to target.")
    parser.add_argument("--replay_from_block", default=None, type=int, help="Set to a block number to replay from that block.")
    parser.add_argument("--tenderly_fork_id", default=None, type=str, help="Set to a Tenderly fork id.")
    parser.add_argument("--tenderly_event_exchanges", default="pancakeswap_v2,pancakeswap_v3", type=str, help="A comma-separated string of exchanges to include for the Tenderly event fetcher.")
    parser.add_argument("--increment_time", default=1, type=int, help="If tenderly_fork_id is set, this is the number of seconds to increment the fork time by for each iteration.")
    parser.add_argument("--increment_blocks", default=1, type=int, help="If tenderly_fork_id is set, this is the number of blocks to increment the block number by for each iteration.")
    parser.add_argument("--blockchain", default="ethereum", help="A blockchain from the list. Blockchains not in this list do not have a deployed Fast Lane contract and are not supported.", choices=["ethereum", "coinbase_base"])
    parser.add_argument("--pool_data_update_frequency", default=-1, type=int, help="How frequently pool data should be updated, in main loop iterations.")
    parser.add_argument("--use_specific_exchange_for_target_tokens", default=None, type=str, help="If an exchange is specified, this will limit the scope of tokens to the tokens found on the exchange")
    parser.add_argument("--prefix_path", default="", type=str, help="Prefixes the path to the write folders (used for deployment)")
    parser.add_argument("--version_check_frequency", default=1, type=int, help="How frequently pool data should be updated, in main loop iterations.")
    parser.add_argument("--self_fund", default=False, type=bool, help="If True, the bot will attempt to submit arbitrage transactions using funds in your wallet when possible.")
    parser.add_argument("--read_only", default=True, type=bool, help="If True, the bot will skip all operations which write to disk. Use this flag if you're running the bot in an environment with restricted write permissions.")

    args = parser.parse_args()

    # Your code logic goes here using the args namespace
    for arg in vars(args):
        print(arg, getattr(args, arg))

if __name__ == "__main__":
    main()
