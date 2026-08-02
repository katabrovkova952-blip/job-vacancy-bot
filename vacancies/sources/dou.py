import re
from dataclasses import dataclass
from datetime import datetime, timezone
import feedparser
from django.utils.html import strip_tags, html
import logging
from vacancies.models import Vacancy


DOU_URL = 'https://jobs.dou.ua/vacancies/feeds/?exp=0-1&remote&category=Python'

logger = logging.getLogger(__name__)


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


def fetch_dou_vacancies() -> int:
    feed = feedparser.parse(DOU_URL)
    if feed.bozo:
        logger.error('Не вдалося розібрати фід DOU: %s', feed.bozo_exception)
        return 0

    count = 0
    for entry in feed.entries:
        try:
            external_id = extract_external_id(entry.link)
            if external_id is None:
                logger.warning('Не знайдено id у посиланні: %s', entry.link)
                continue

            info = parse_title(entry.title)

            _, created = Vacancy.objects.get_or_create(
                source='dou',
                external_id=external_id,
                defaults={
                    'title': info.position,
                    'company': info.company,
                    'location': info.location,
                    'url': entry.link,
                    'description': strip_tags(html.unescape(entry.summary)),
                    'published_at': datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                },
            )
            if created:
                count+=1

        except Exception:
            logger.exception('Помилка обробки вакансії: %s', entry.get('link'))
            continue

    logger.info('DOU: збережено %s нових вакансій', count)
    return count