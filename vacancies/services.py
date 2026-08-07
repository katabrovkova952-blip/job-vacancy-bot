import logging

from django.db.models import Q

from vacancies.models import Vacancy
from vacancies.sources.base import RawVacancy

logger = logging.getLogger(__name__)


def parse_keywords(raw: str) -> list[str]:
    if not raw:
        return []

    parts = raw.lower().split(',')
    words = [part.strip() for part in parts if part.strip()]
    return list(dict.fromkeys(words))


def build_keywords_condition(keywords: list[str]) -> Q:
    condition = Q()
    for keyword in keywords:
        condition |= Q(title__icontains=keyword)
    return condition


def save_vacancies(source: str, raw_vacancies: list[RawVacancy]) -> int:
    count = 0
    for raw in raw_vacancies:
        _, created = Vacancy.objects.get_or_create(
            source=source,
            external_id=raw.external_id,
            defaults={
                'title': raw.title,
                'company': raw.company,
                'location': raw.location,
                'url': raw.url,
                'description': raw.description,
                'published_at': raw.published_at,
            },
        )
        if created:
            count += 1

    logger.info('%s: збережено %s нових вакансій', source, count)
    return count
