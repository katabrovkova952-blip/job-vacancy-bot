from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawVacancy:
    external_id: str
    title: str
    company: str
    location: str
    url: str
    description: str
    published_at: datetime
