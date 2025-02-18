from django.contrib import admin

from common.models import Language, LanguageProficiency, Report


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(LanguageProficiency)
class LanguageProficiencyAdmin(admin.ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'content_object', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('reporter__username', 'message')
