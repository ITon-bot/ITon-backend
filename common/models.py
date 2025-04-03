from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class Specialization(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    code = models.CharField(max_length=5, unique=True, help_text=_("Unique code for the language (e.g., 'en', 'ru')"))
    name = models.CharField(max_length=50, help_text=_("Display name of the language"))

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['name']

    def __str__(self):
        return self.name


class LanguageProficiency(models.Model):
    LEVEL_CHOICES = [
        ('fluent', _('Fluent')),
        ('basic', _('Basic')),
        ('native', _('Native')),
        ('conversational', _('Conversational')),
    ]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.CharField(max_length=32, choices=LEVEL_CHOICES)

    class Meta:
        verbose_name = _("Language Proficiency")
        verbose_name_plural = _("Language Proficiencies")

    def __str__(self):
        return f'{self.content_object} - {self.language} ({self.level})'


class Report(models.Model):
    reporter = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reports_sent',
        verbose_name="Пожаловался")
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Тип жалобы")
    object_id = models.PositiveIntegerField(verbose_name="ID объекта")
    content_object = GenericForeignKey('content_type', 'object_id')

    message = models.TextField(
        verbose_name="Сообщение жалобы",
        help_text="Опишите, в чем проблема или причина жалобы",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_resolved = models.BooleanField(default=False, verbose_name="Жалоба решена")

    class Meta:
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Жалоба от {self.reporter} на {self.content_object}"
