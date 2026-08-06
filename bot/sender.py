import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from django.conf import settings
from django.templatetags.i18n import language

from bot.texts import t
from vacancies.models import SentVacancy, Subscriber, Vacancy
from vacancies.services import build_keywords_condition, parse_keywords

logger = logging.getLogger(__name__)

MAX_VACANCIES_PER_DIGEST = 20

async def send_to_subscriber(bot: Bot, subscriber: Subscriber, text: str) -> bool:
    try:
        await bot.send_message(chat_id=subscriber.chat_id, text=text)
        return True

    except TelegramForbiddenError:
        subscriber.is_active = False
        await subscriber.asave(update_fields=['is_active'])
        logger.info('Підписник %s заблокував бота — деактивовано', subscriber.chat_id)
        return False

    except TelegramRetryAfter as e:
        logger.warning('Ліміт Telegram, чекаємо %s с', e.retry_after)
        await asyncio.sleep(e.retry_after)
        return await send_to_subscriber(bot, subscriber, text)


def format_digest(vacancies: list[Vacancy], language: str) -> str:
    lines = [t('digest_header', language, count=str(len(vacancies)))]

    for vacancy in vacancies:
        company = f' — {vacancy.company}' if vacancy.company else ''
        lines.append(f'• {vacancy.title}{company}\n{vacancy.url}')

    return '\n\n'.join(lines)


async def get_new_vacancies(subscriber: Subscriber) -> list[Vacancy]:
    keywords = parse_keywords(subscriber.filters)
    if not keywords:
        return []

    sent_ids = SentVacancy.objects.filter(subscriber=subscriber).values_list('vacancy_id', flat=True)
    queryset = (
        Vacancy.objects
        .filter(build_keywords_condition(keywords))
        .exclude(id__in=sent_ids)[:MAX_VACANCIES_PER_DIGEST]
    )
    return [vacancy async for vacancy in queryset]


async def send_digest_to(bot: Bot, subscriber: Subscriber) -> int:
    vacancies = await get_new_vacancies(subscriber)
    if not vacancies:
        return 0

    text = format_digest(vacancies, subscriber.language)
    if not await send_to_subscriber(bot, subscriber, text):
        return 0

    await SentVacancy.objects.abulk_create(
        [SentVacancy(subscriber=subscriber, vacancy=v) for v in vacancies],
        ignore_conflicts=True,
    )
    return len(vacancies)


async def send_digests() -> int:
    bot = Bot(token=settings.BOT_TOKEN)
    total = 0

    try:
        async for subscriber in Subscriber.objects.filter(is_active=True):
            total += await send_digest_to(bot, subscriber)
            await asyncio.sleep(0.05)
    finally:
        await bot.session.close()

    logger.info('Розсилка завершена, всього надіслано: %s', total)
    return total
