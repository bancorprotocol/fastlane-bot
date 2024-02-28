"""
This module contains the ArgumentParserMock class, which is used to mock the command line arguments for the main.py

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
from dataclasses import dataclass

from fastlane_bot.tools.cpc import T


@dataclass
class ArgumentParserMock:
    """
    This class is used to mock the command line arguments for the main.py
    """

    cache_latest_only: str = "True"
    backdate_pools: str = "True"
    static_pool_data_filename: str = "static_pool_data"
    arb_mode: str = "multi_pairwise_all"
    flashloan_tokens: str = (
        f"{T.LINK},{T.NATIVE_ETH},{T.BNT},{T.WBTC},{T.DAI},{T.USDC},{T.USDT},{T.WETH}"
    )
    n_jobs: int = -1
    exchanges: str = "carbon_v1,bancor_v3,bancor_v2,bancor_pol,uniswap_v3,uniswap_v2,sushiswap_v2,balancer,pancakeswap_v2,pancakeswap_v3"
    polling_interval: int = 1
    alchemy_max_block_fetch: int = 1200
    reorg_delay: int = 0
    logging_path: str = ""
    loglevel: str = "INFO"
    use_cached_events: str = "False"
    run_data_validator: str = "False"
    randomizer: int = 3
    limit_bancor3_flashloan_tokens: str = "True"
    default_min_profit_gas_token: str = "-100"  # "0.01"
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
