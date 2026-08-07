import pytest

from vacancies.sources.dou import extract_external_id, parse_title


@pytest.mark.parametrize(
    ('url', 'expected'),
    [
        pytest.param(
            'https://jobs.dou.ua/companies/jooble/vacancies/367785/?utm_source=jobsrss',
            '367785', id='query param'
        ),
        pytest.param(
            'https://jobs.dou.ua/companies/jooble/vacancies/367785/',
            '367785', id='no query param'
        ),
        pytest.param(
            'https://jobs.dou.ua/companies/jooble/vacancies/367785',
            '367785', id='no slash at the end'
        ),
        pytest.param(
            'https://jobs.dou.ua/vacancies/?remote&category=Python',
            None, id='returns none for feed url'
        ),
        pytest.param('https://example.com/no-id-here/',
         None, id='no id'
         ),
        ('', None),
    ],
)
def test_extract_external_id(url, expected):
    assert extract_external_id(url) == expected


@pytest.mark.parametrize(
    ('title', 'position', 'company', 'location'),
    [
        (
            'Web Scraping Specialist в Jooble, Київ, віддалено',
            'Web Scraping Specialist', 'Jooble', 'Київ, віддалено',
        ),
        (
            'Junior Python Developer в SoftServe',
            'Junior Python Developer', 'SoftServe', '',
        ),
        (
            'Розробник в команду підтримки в EPAM, Львів',
            'Розробник в команду підтримки', 'EPAM', 'Львів',
        ),
        (
            'Просто якийсь текст',
            'Просто якийсь текст', '', '',
        ),
    ],
)
def test_parse_title(title, position, company, location):
    result = parse_title(title)
    assert result.position == position
    assert result.company == company
    assert result.location == location