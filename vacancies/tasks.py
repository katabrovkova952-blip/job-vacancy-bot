from celery import shared_task

from vacancies.sources.dou import fetch_dou_vacancies


@shared_task
def fetch_vacancies() -> int:
    return fetch_dou_vacancies()