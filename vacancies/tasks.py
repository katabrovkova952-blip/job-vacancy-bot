import asyncio

from celery import shared_task

from bot.sender import send_digests
from vacancies.sources.dou import fetch_dou_vacancies


@shared_task
def fetch_vacancies() -> int:
    return fetch_dou_vacancies()


@shared_task
def send_vacancy_digests() -> int:
    return asyncio.run(send_digests())