from django.db import models


class Vacancy(models.Model):
    SOURCE_CHOICES = [('dou', 'DOU'), ('djinni', 'Djinni'), ('jobicy', 'Jobicy')]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    external_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    url = models.URLField()
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']
        constraints = [models.UniqueConstraint(fields=['source', 'external_id'], name='unique_vacancy_per_source')]

    def __str__(self) -> str:
        return self.title


class Subscriber(models.Model):
    LANGUAGE_CHOICES = [
        ('uk', 'Українська'),
        ('en', 'English'),
    ]
    language = models.CharField(max_length=5, default='uk')
    chat_id = models.BigIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    filters = models.CharField(max_length=300, blank=True, default='')

    def __str__(self) -> str:
        return str(self.chat_id)


class SentVacancy(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='sent_vacancies')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='sent_to')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        constraints = [models.UniqueConstraint(fields=['subscriber', 'vacancy'], name='unique_subscriber_vacancy')]

    def __str__(self) -> str:
        return f'{self.vacancy.title}, {self.subscriber.chat_id}'
