TEXTS = {
    'uk': {
        'welcome': (
            'Привіт! Я надсилатиму нові вакансії.\n\n'
            'Спершу вкажи, що тебе цікавить:\n'
            '/filters python, django\n\n'
            'Усі команди — /help'
        ),
        'already_subscribed': 'Ти вже підписаний.',
        'welcome_back': 'З поверненням! Підписку відновлено.',
        'not_subscribed': 'Спершу натисни /start',
        'paused': 'Підписку зупинено. Щоб відновити — /start',
        'already_paused': 'Підписка вже на паузі.',
        'filters_current': 'Поточні фільтри: {filters}',
        'filters_ask': 'Напиши нові ключові слова через кому:',
        'filters_updated': 'Фільтри оновлено: {filters}',
        'filters_invalid': 'Не вдалося розпізнати ключові слова. Спробуй: python, django',
        'no_vacancies': 'Поки що нових вакансій за цими фільтрами немає.',
        'digest_header': 'Знайдено нових вакансій: {count}',
        'language_changed': 'Мову змінено на українську.',
        'filters_not_set': 'не встановлені',
        'help': (
            'Я надсилаю нові вакансії з DOU та Jobicy.\n\n'
            '/start — підписатися\n'
            '/filters — налаштувати ключові слова\n'
            '/ua — українською\n'
            '/en — in English\n'
            '/pause — поставити на паузу\n'
            '/help — ця довідка'
        ),
    },
    'en': {
        'welcome': (
            'Hi! I will send you new job openings.\n\n'
            'First, tell me what you are looking for:\n'
            '/filters python, django\n\n'
            'All commands — /help'
        ),
        'already_subscribed': 'You are already subscribed.',
        'welcome_back': 'Welcome back! Subscription restored.',
        'not_subscribed': 'Press /start first',
        'paused': 'Subscription paused. To resume — /start',
        'already_paused': 'Subscription is already paused.',
        'filters_current': 'Your filters: {filters}',
        'filters_ask': 'Send new keywords separated by commas:',
        'filters_updated': 'Filters updated: {filters}',
        'filters_invalid': 'Could not parse keywords. Try: python, django',
        'no_vacancies': 'No new vacancies matching your filters yet.',
        'digest_header': 'New vacancies found: {count}',
        'language_changed': 'Language changed to English.',
        'filters_not_set': 'not set',
        'help': (
            'I send new job openings from DOU and Jobicy.\n\n'
            '/start — subscribe\n'
            '/filters — set keywords\n'
            '/ua — українською\n'
            '/en — in English\n'
            '/pause — pause\n'
            '/help — this message'
        ),
    },
}

DEFAULT_LANGUAGE = 'uk'


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: str) -> str:
    texts = TEXTS.get(lang, TEXTS[DEFAULT_LANGUAGE])
    template = texts.get(key, TEXTS[DEFAULT_LANGUAGE].get(key, key))
    return template.format(**kwargs) if kwargs else template
