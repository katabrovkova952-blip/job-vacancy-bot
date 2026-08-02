from django.core.management.base import BaseCommand
from typing import Any


class Command(BaseCommand):
    help = 'Запускає Telegram-бота'

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write('Бот стартує...')