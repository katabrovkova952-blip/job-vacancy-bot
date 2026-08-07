import calendar
import html
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser
from django.conf import settings
from django.utils.html import strip_tags

from vacancies.sources.base import RawVacancy

logger = logging.getLogger(__name__)

SOURCE_NAME = 'dou'


def extract_external_id(url: str) -> str | None:
    match = re.search(r'/vacancies/(\d+)', url)
    return match.group(1) if match else None


@dataclass
class VacancyInfo:
    position: str
    company: str
    location: str


def parse_title(raw: str) -> VacancyInfo:
    position = raw.strip()
    company = ''
    location = ''

    parts = position.split(',', 1)
    if len(parts) == 2:
        position = parts[0].strip()
        location = parts[1].strip()

    parts = position.rsplit(' в ', 1)
    if len(parts) == 2:
        position = parts[0].strip()
        company = parts[1].strip()

    return VacancyInfo(position=position, company=company, location=location)


def fetch() -> list[RawVacancy]:
    feed = feedparser.parse(settings.DOU_FEED_URL)

    if feed.bozo:
        logger.error('Не вдалося розібрати фід DOU: %s', feed.bozo_exception)
        return []

    result = []
    for entry in feed.entries:
        try:
            external_id = extract_external_id(entry.link)
            if external_id is None:
                continue

            published_parsed = getattr(entry, 'published_parsed', None)
            if published_parsed is None:
                continue

            published_at = datetime.fromtimestamp(calendar.timegm(published_parsed), tz=timezone.utc)

            info = parse_title(html.unescape(entry.title))
            result.append(
                RawVacancy(
                    external_id=external_id,
                    title=info.position,
                    company=info.company,
                    location=info.location,
                    url=entry.link,
                    description=strip_tags(html.unescape(entry.summary)),
                    published_at=published_at,
                )
            )
        except Exception:
            logger.exception('Помилка обробки вакансії DOU')

    return result
