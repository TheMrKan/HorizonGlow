import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import instance as config

import os
import logging.config

if not os.path.isdir("logs"):
    os.mkdir("logs")

logging.config.dictConfig(config.logging)
logger = logging.getLogger(__name__)

import user_commands
import support_commands
from core.api import APIClient
from middlewares import DbSessionMiddleware, UsersMiddleware
import globals


async def main():
    logger.info("Starting...")

    db_engine = create_async_engine(config.DATABASE_URL, echo=True)
    sessionmaker = async_sessionmaker(db_engine, expire_on_commit=False)

    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    globals.bot = bot

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(sessionmaker))
    dp.message.middleware(UsersMiddleware())

    dp.include_router(user_commands.router)
    dp.include_router(support_commands.router)

    APIClient.instance = APIClient(base_url=config.base_api_url,
                                   username=config.API_USERNAME,
                                   password=config.API_PASSWORD,
                                   secret_phrase=config.API_SECRET_PHRASE)
    await APIClient.instance.authenticate_async()
    logger.info("API auth completed")

    logger.info("Setup completed. Polling...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())