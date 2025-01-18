import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import instance as config

import os
import logging.config

if not os.path.isdir("logs"):
    os.mkdir("logs")

logging.config.dictConfig(config.logging)
logger = logging.getLogger(__name__)

import user_commands


async def main():
    logger.info("Starting...")

    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

    dp = Dispatcher()

    dp.include_router(user_commands.router)

    logger.info("Setup completed. Polling...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())