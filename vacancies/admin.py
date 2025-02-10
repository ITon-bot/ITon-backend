from django.contrib import admin

from vacancies.models import Vacancy, VacancyResponse


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    pass

@admin.register(VacancyResponse)
class VacancyResponseAdmin(admin.ModelAdmin):
    pass
