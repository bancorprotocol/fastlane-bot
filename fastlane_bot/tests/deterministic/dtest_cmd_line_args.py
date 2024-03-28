from dataclasses import dataclass

from fastlane_bot.tools.cpc import T


@dataclass
class TestCommandLineArgs:
    """
    This class is used to mock the command line arguments for the main.py
    """

    cache_latest_only: str = "True"
    backdate_pools: str = "True"
    static_pool_data_filename: str = "static_pool_data_testing"
    arb_mode: str = "multi_pairwise_all"
    flashloan_tokens: str = (
        f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC},{T.DAI},{T.USDC},{T.USDT},{T.WETH}"
    )
    n_jobs: int = -1
    exchanges: str = "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3"
    polling_interval: int = 0
    alchemy_max_block_fetch: int = 1
    reorg_delay: int = 0
    logging_path: str = "logs_dtest"
    loglevel: str = "INFO"
    use_cached_events: str = "False"
    run_data_validator: str = "False"
    randomizer: int = 1
    limit_bancor3_flashloan_tokens: str = "True"
    default_min_profit_gas_token: str = "0.002"  # "0.01"
    timeout: int = None
    target_tokens: str = None
    replay_from_block: int = None
    tenderly_fork_id: int = None
    tenderly_event_exchanges: str = "pancakeswap_v2,pancakeswap_v3"
    increment_time: int = 1
    increment_blocks: int = 1
    blockchain: str = "ethereum"
    pool_data_update_frequency: int = -1
    use_specific_exchange_for_target_tokens: str = None
    prefix_path: str = ""
    version_check_frequency: int = 1
    self_fund: str = "False"
    read_only: str = "False"
    is_args_test: str = "False"
    rpc_url: str = None

    @staticmethod
    def args_to_command_line(args):
        """
        Convert a TestCommandLineArgs instance to a list of command-line arguments.

        Args:
            args: An instance of TestCommandLineArgs.

        Returns:
            A list of command-line arguments.
        """
        cmd_args = []
        for field, value in args.__dict__.items():
            if value is not None:  # Only include fields that have a value
                cmd_args.extend((f"--{field}", str(value)))
        return cmd_args
