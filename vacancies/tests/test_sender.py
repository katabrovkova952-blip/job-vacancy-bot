import pytest

from bot.sender import get_new_vacancies, MAX_VACANCIES_PER_DIGEST
from vacancies.models import SentVacancy, Vacancy, Subscriber
from vacancies.services import save_vacancies
from asgiref.sync import sync_to_async


@pytest.mark.django_db(transaction=True)
async def test_get_new_vacancies_excludes_already_sent(subscriber, raw_vacancy):
    await sync_to_async(save_vacancies)('dou', [raw_vacancy(title='Python Developer', external_id='100')])
    vacancy = await Vacancy.objects.afirst()

    first = await get_new_vacancies(subscriber)
    assert len(first) == 1

    await SentVacancy.objects.acreate(subscriber=subscriber, vacancy=vacancy)

    second = await get_new_vacancies(subscriber)
    assert second == []


@pytest.mark.django_db(transaction=True)
async def test_get_new_vacancies_returns_empty_without_filters(raw_vacancy):
    subscriber = await Subscriber.objects.acreate(chat_id=999, filters='')
    await sync_to_async(save_vacancies)('dou', [raw_vacancy(external_id='100')])

    assert await get_new_vacancies(subscriber) == []


@pytest.mark.django_db(transaction=True)
async def test_get_new_vacancies_respects_limit(subscriber, raw_vacancy):
    data = [
        raw_vacancy(title='Python Developer', external_id=str(i))
        for i in range(25)
    ]
    await sync_to_async(save_vacancies)('dou', data)

    result = await get_new_vacancies(subscriber)

    assert len(result) == MAX_VACANCIES_PER_DIGEST