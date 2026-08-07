import pytest

from vacancies.models import Vacancy
from vacancies.services import parse_keywords, save_vacancies, build_keywords_condition


def test_parse_keywords_removes_duplicates():
    assert parse_keywords("python, django, Python, Django") == ['python', 'django']


def test_parse_keywords_normalizes_case():
    assert parse_keywords("PYTHON, DjAngo") == ['python', 'django']


def test_parse_keywords_comma_separated():
    assert parse_keywords("python, django") == ['python', 'django']


def test_parse_keywords_removes_spaces():
    assert parse_keywords("   python,  django  ") == ['python', 'django']


def test_parse_keywords_empty_line():
    assert parse_keywords("   ") == []


def test_parse_keywords_just_commas():
    assert parse_keywords(",,,,,") == []


def test_parse_keywords_many_words():
    assert parse_keywords("backend developer, python engineer") == ["backend developer", "python engineer"]


@pytest.mark.django_db
def test_save_vacancies_does_not_create_duplicates(raw_vacancy):
    data = [raw_vacancy(external_id='100')]

    first = save_vacancies('dou', data)
    second = save_vacancies('dou', data)

    assert first == 1
    assert second == 0
    assert Vacancy.objects.count() == 1


@pytest.mark.django_db
def test_same_external_id_from_different_sources(raw_vacancy):
    save_vacancies('dou', [raw_vacancy(external_id='100')])
    save_vacancies('jobicy', [raw_vacancy(external_id='100')])

    assert Vacancy.objects.count() == 2


@pytest.mark.django_db
def test_filters(raw_vacancy):
    save_vacancies('dou', [raw_vacancy(title='Python Backend', external_id='100')])
    save_vacancies('jobicy', [raw_vacancy(title='Recruiter', external_id='101')])

    condition = build_keywords_condition(['python'])
    found = Vacancy.objects.filter(condition)

    assert found.count() == 1
    assert found.first().title == 'Python Backend'


@pytest.mark.django_db
def test_filters_matches_any_keyword(raw_vacancy):
    save_vacancies('dou', [
        raw_vacancy(title='Python Backend', external_id='100'),
        raw_vacancy(title='Django Developer', external_id='101'),
        raw_vacancy(title='Recruiter', external_id='102'),
    ])

    condition = build_keywords_condition(['python', 'django'])

    assert Vacancy.objects.filter(condition).count() == 2