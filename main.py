"""

Бот разработан командой The Code Factory в 2025 году
https://the-code-factory-team.github.io

"""

import asyncio
import logging
import configparser
import os
from maxapi.types import BotStarted
from functions.handlers import router, hello
from functions.docs_module import docs_router
from functions.schedule_module import schedule_router
from functions.help_module import help_router

from maxapi import Bot, Dispatcher

logging.basicConfig(level=logging.INFO)

config = configparser.RawConfigParser()
config.sections()
config.read(os.path.join(os.path.dirname(
    __file__), 'config.ini'), encoding="utf-8")

bot = Bot(config['BOT']['token'])
dp = Dispatcher()
dp.include_routers(router)
dp.include_routers(schedule_router)
dp.include_routers(help_router)
dp.include_routers(docs_router)


@dp.bot_started()
async def bot_started(event: BotStarted):
    return await hello(event)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
