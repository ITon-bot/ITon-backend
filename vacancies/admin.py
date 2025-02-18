from django.contrib import admin

from vacancies.models import Vacancy, VacancyResponse


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator', 'company_name')


@admin.register(VacancyResponse)
class VacancyResponseAdmin(admin.ModelAdmin):
    pass
