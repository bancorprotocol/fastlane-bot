"""
This file contains constants used in the deterministic tests.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT License.
"""
from dataclasses import dataclass

from fastlane_bot.tools.cpc import T

KNOWN_UNABLE_TO_DELETE = {
    68737038118029569619601670701217178714718: ("pDFS", "ETH"),
}
TEST_MODE_AMT = (
    115792089237316195423570985008687907853269984665640564039457584007913129639935
)
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
SUPPORTED_EXCHANGES = ["uniswap_v2", "uniswap_v3", "pancakeswap_v2", "pancakeswap_v3"]
BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DEFAULT_GAS = 2000000
DEFAULT_GAS_PRICE = 0
DEFAULT_FROM_BLOCK = 1000000
TENDERLY_RPC_KEY = "fb866397-29bd-4886-8406-a2cc7b7c5b1f"  # https://virtual.mainnet.rpc.tenderly.co/9ea4ceb3-d0f5-4faf-959e-f51cf1f6b52b, from_block: 19325893, fb866397-29bd-4886-8406-a2cc7b7c5b1f
FILE_DATA_DIR = "fastlane_bot/data/blockchain_data"
TEST_FILE_DATA_DIR = "fastlane_bot/tests/deterministic/_data"
binance14 = "0x28C6c06298d514Db089934071355E5743bf21d60"
TOKENS_MODIFICATIONS = {
    "0x0": {
        "address": "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5",
        "modifications": {
            "before": {
                "0x0000000000000000000000000000000000000000000000000000000000000006": "0x01",
                "0x0000000000000000000000000000000000000000000000000000000000000007": "0x01",
                "0x000000000000000000000000000000000000000000000000000000000000000d": "0x01",
            },
            "after": {
                "0x0000000000000000000000000000000000000000000000000000000000000006": "0x0000000000000000000000000000000000000000000000000000000000000019",
                "0x0000000000000000000000000000000000000000000000000000000000000007": "0x0000000000000000000000000000000000000000000000000000000000000005",
                "0x000000000000000000000000000000000000000000000000000000000000000d": "0x2386f26fc10000",
            },
            "balance": 288551667147,
        },
        "strategy_id": 9868188640707215440437863615521278132277,
        "strategy_beneficiary": "0xe3d51681Dc2ceF9d7373c71D9b02c5308D852dDe",
    },
    "PAXG": {
        "address": "0x45804880De22913dAFE09f4980848ECE6EcbAf78",
        "modifications": {
            "before": {
                "0x000000000000000000000000000000000000000000000000000000000000000d": "0x00",
            },
            "after": {
                "0x000000000000000000000000000000000000000000000000000000000000000d": "0x00000000000000000000000000000000000000000000000000000000000000c8",
            },
            "balance": 395803389286127,
        },
        "strategy_id": 15312706511442230855851857334429569515620,
        "strategy_beneficiary": "0xFf365375777069eBd8Fa575635EB31a0787Afa6c",
    },
}


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
    logging_path: str = ""
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
