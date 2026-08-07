import asyncio

from celery import shared_task

from bot.sender import send_digests
from vacancies.services import save_vacancies


@shared_task
def fetch_dou() -> int:
    from vacancies.sources import dou

    return save_vacancies(dou.SOURCE_NAME, dou.fetch())


@shared_task
def fetch_jobicy() -> int:
    from vacancies.sources import jobicy

    return save_vacancies(jobicy.SOURCE_NAME, jobicy.fetch())


@shared_task
def send_vacancy_digests() -> int:
    return asyncio.run(send_digests())
