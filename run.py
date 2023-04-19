"""
Main logic for the Bancor Arbitrage Bot (FastLane) - run.py filescript

Note: You should configure the bot in config.py before running this script.

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
import click
from carbon.tools.cpc import T
from carbon.bot import CarbonBot

from carbon.models import *
session.rollback()

flashloan_tokens = [T.BNT, T.WETH]


@click.command()
@click.option("--mode", default="single", type=str)
@click.option("--flashloan_tokens", default=flashloan_tokens, type=list)
@click.option("--update_pools", default=False, type=bool)
def main(
        mode,
        flashloan_tokens,
        update_pools,
):
    """
    Main logic for the Bancor Arbitrage Bot (FastLane) - run.py filescript

    Parmeters
    ---------
    execute_mode: str
        Execution mode for the bot. Can be "single" or "continuous"
    exchanges: str
        Comma separated list of exchanges to use. Can be "uniswap_v2", "uniswap_v3", "sushiswap", "bancor_v2", "bancor_v3", "carbon_v1"
    flashloan_tokens: str
        Comma separated list of flashloan tokens to use. Can be "ETH", "DAI", "USDC", "USDT", "WBTC", "WETH", "BNT" or any other token that can be flashloaned
    min_profit: Decimal
        Minimum profit to execute a trade
    network_name: str
        Network name to use. Can be "Mainnet (Tenderly)" or "Mainnet (Infura)"
    fastlane_contract_address: str
        FastLane contract address
    max_slippage: Decimal
        Maximum slippage to execute a trade
    blocktime_deviation: int
        Blocktime deviation to use
    update_pools: bool
        Whether to update the pools or not. In production, this should be False and the pools should be updated by an independent process
    """

    # Initialize the bot
    bot = CarbonBot(
        mode=mode,
        polling_interval=update_pools,
        update_pools=True,
        # seed_pools=True,
    )

    # Run the bot
    bot.run(flashloan_tokens=flashloan_tokens, update_pools=update_pools)


if __name__ == "__main__":
    main()
