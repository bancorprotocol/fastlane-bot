#!/usr/bin/env python3
"""
Database event updater.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio

from fastlane_bot import Bot, Config
# from fastlane_bot.bot import CarbonBot
# from fastlane_bot.config import logger
# from fastlane_bot.db.manager import DatabaseManager
#import fastlane_bot.config as c

# TODO: Refactor this with click inputs like in the run.py file

#db = DatabaseManager()
#cfg = C = Config.new(config=Config.CONFIG_MAINNET)
bot = Bot(ConfigObj=Config.new(config=Config.CONFIG_MAINNET))
bot.update(bot.UDTYPE_FROM_CONTRACTS, drop_tables=False)

# # bot.db.drop_all_tables()  # uncomment as needed
# bot.db.update_pools_from_contracts(top_n=10)


# async def create_tasks_and_run(updater):
#     tasks = []
#     logger.info("Creating tasks")
#     for args in updater.filters:
#         exchange, _filter = args["exchange"], args["_filter"]
#         task = asyncio.create_task(updater._log_loop(exchange, _filter))
#         tasks.append(task)
#         logger.info(f"Created task for {exchange} {_filter}")
#
#     await asyncio.gather(*tasks)
#
# try:
#     asyncio.run(create_tasks_and_run(updater))
# except KeyboardInterrupt:
#     print("Stopped by user")
