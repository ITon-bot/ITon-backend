from django.contrib import admin

from common.admin import LanguageProficiencyInline
from vacancies.models import Vacancy, VacancyResponse

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'creator', 'company_name')
    inlines = [LanguageProficiencyInline]


@admin.register(VacancyResponse)
class VacancyResponseAdmin(admin.ModelAdmin):
    pass
