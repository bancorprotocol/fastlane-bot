#!/usr/bin/env python3
"""
Main logic for the Bancor Arbitrage Bot (FastLane) - run.py filescript

Note: You should configure the bot in config.py before running this script.

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
import click

from fastlane_bot import Config
from fastlane_bot.bot import CarbonBot

flashloan_tokens = None


@click.command()
@click.option("--mode", default="continuous", type=str)
@click.option("--flashloan_tokens", default=flashloan_tokens, type=list)
@click.option("--polling_interval", default=12, type=int)
@click.option("--config", default=None, type=str)
@click.option("--arb_mode", default="single", type=str)
def main(
        mode: str = "continuous",
        flashloan_tokens: list = None,
        polling_interval: int = 12,
        config: str = None,
        arb_mode: str = "single"


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
    config: str
        The config to use. Options are:
            - None: use the default config (Mainnet)
            - tenderly: use the tenderly config

    arb_mode: str
        The mode of the bot. Options are:
            - None: default mode
            - multi_triangle: the bot will run in multi triangle mode
            - ...

    """
    print("Starting bot...")

    if config and config == 'tenderly':
        cfg = Config.new(config=Config.CONFIG_TENDERLY)
    else:
        cfg = Config.new(config=Config.CONFIG_MAINNET)

    bot = CarbonBot(ConfigObj=cfg)
    bot.run(polling_interval=polling_interval, flashloan_tokens=flashloan_tokens, mode=mode, arb_mode=arb_mode)


if __name__ == "__main__":
    main()
