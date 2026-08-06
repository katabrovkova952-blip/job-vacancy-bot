from django.db.models import Q


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