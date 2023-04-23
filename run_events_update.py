#!/usr/bin/env python3
"""
Database event updater.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio
from fastlane_bot.bot import CarbonBot
from fastlane_bot.config import logger
from fastlane_bot.db.events import EventHandler
from fastlane_bot.db.manager import DatabaseManager
import fastlane_bot.config as c

# TODO: Refactor this with click inputs like in the run.py file

db = DatabaseManager()

# db.drop_all_tables()

bot = CarbonBot(
    db=db,
    polling_interval=c.DEFAULT_POLL_INTERVAL,
)
db.update_pools()
updater = EventHandler(
    db=db,
)

async def create_tasks_and_run(updater):
    tasks = []
    logger.info("Creating tasks")
    for args in updater.filters:
        exchange, _filter = args["exchange"], args["_filter"]
        task = asyncio.create_task(updater._log_loop(exchange, _filter))
        tasks.append(task)
        logger.info(f"Created task for {exchange} {_filter}")

    await asyncio.gather(*tasks)

try:
    asyncio.run(create_tasks_and_run(updater))
except KeyboardInterrupt:
    print("Stopped by user")
