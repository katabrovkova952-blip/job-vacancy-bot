from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Запускає Telegram-бота'

    def handle(self, *args, **options) -> None:
        self.stdout.write('Бот стартує...')