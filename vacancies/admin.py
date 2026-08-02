from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from .models import SentVacancy, Subscriber, Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'source', 'published_at')
    list_filter = ('source', 'published_at')
    search_fields = ('title', 'company', 'description')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'is_active')
    list_filter = ('is_active',)


@admin.register(SentVacancy)
class SentVacancyAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'subscriber', 'sent_at')
    list_filter = ('sent_at',)

    def get_queryset(self, request: HttpRequest) -> QuerySet[SentVacancy]:
        return super().get_queryset(request).select_related('vacancy', 'subscriber')