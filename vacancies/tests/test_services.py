from vacancies.services import parse_keywords


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

