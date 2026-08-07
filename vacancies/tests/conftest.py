import pytest
from django.utils import timezone

from vacancies.models import Subscriber
from vacancies.sources.base import RawVacancy


@pytest.fixture
def raw_vacancy():
    def _make(external_id='1', title='Python Developer', company='Acme'):
        return RawVacancy(
            external_id=external_id,
            title=title,
            company=company,
            location='Київ',
            url=f'https://example.com/{external_id}/',
            description='Опис',
            published_at=timezone.now(),
        )

    return _make


@pytest.fixture
def subscriber():
    return Subscriber.objects.create(chat_id=123456, filters='python')
