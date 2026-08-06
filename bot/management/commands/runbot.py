import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from django.conf import settings
from django.core.management.base import BaseCommand

from bot.handlers import commands_router


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command='start', description='Підписатися'),
        BotCommand(command='pause', description='Поставити на паузу'),
        BotCommand(command='help', description='Довідка'),
        BotCommand(command='filters', description='Фільтри')
    ]
    await bot.set_my_commands(commands)


logger = logging.getLogger(__name__)


async def run_bot() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(commands_router)

    await set_commands(bot)

    logger.info('Бот запускається...')
    await dp.start_polling(bot)


class Command(BaseCommand):
    help = 'Запускає Telegram-бота'
    def handle(self, *args: Any, **options: Any) -> None:
        asyncio.run(run_bot())