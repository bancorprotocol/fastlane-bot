"""
Main logic for the Bancor Arbitrage Bot (FastLane) - run.py filescript

Note: You should configure the bot in config.py before running this script.

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
import click
from carbon.tools.cpc import T
from fastlane_bot.bot import CarbonBot
from fastlane_bot.models import *

session.rollback()

flashloan_tokens = [T.BNT, T.WETH, T.WBTC, T.USDT, T.USDC, T.DAI]


@click.command()
@click.option("--mode", default="continuous", type=str)
@click.option("--flashloan_tokens", default=flashloan_tokens, type=list)
@click.option("--polling_interval", default=12, type=int)
def main(
    mode,
    flashloan_tokens,
    polling_interval,
):
    """
    Main logic for the Bancor Arbitrage Bot (FastLane) - run.py filescript

    Parmeters
    ---------
    mode: str
        The mode of the bot. Options are:
            - continuous: the bot will run continuously
            - single: the bot will run once and then exit
    flashloan_tokens: list
        The list of tokens that the bot will use for flashloans
    update_pools: bool
        Whether the bot should update the pools before running
    polling_interval: int
        The interval (in seconds) at which the bot will poll for new blocks
    seed_pools: bool
        Whether the bot should seed the pools before running

    """

    # Initialize the bot
    bot = CarbonBot(
        polling_interval=polling_interval,
    )

    # Run the bot
    bot.run(flashloan_tokens=flashloan_tokens, mode=mode)


if __name__ == "__main__":
    main()
