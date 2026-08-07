import html
import logging
from datetime import datetime, timezone

import httpx
from django.conf import settings
from django.utils.html import strip_tags

from vacancies.sources.base import RawVacancy

logger = logging.getLogger(__name__)

SOURCE_NAME = 'jobicy'


def parse_pub_date(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def fetch() -> list[RawVacancy]:
    try:
        response = httpx.get(settings.JOBICY_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        logger.exception('Не вдалося отримати дані Jobicy')
        return []

    result: list[RawVacancy] = []

    for job in data.get('jobs', []):
        try:
            result.append(
                RawVacancy(
                    external_id=str(job['id']),
                    title=html.unescape(job['jobTitle']),
                    company=html.unescape(job.get('companyName', '')),
                    location=job.get('jobGeo', ''),
                    url=job['url'],
                    description=strip_tags(html.unescape(job.get('jobExcerpt', ''))),
                    published_at=parse_pub_date(job['pubDate']),
                )
            )
        except Exception:
            logger.exception('Помилка обробки вакансії Jobicy: %s', job.get('id'))

    return result
