from django.contrib import admin

from common.admin import LanguageProficiencyInline
from users.models import User, Education, Experience


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'is_blocked')
    inlines = [LanguageProficiencyInline]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    pass


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    pass
