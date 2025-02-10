import json

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

from common.models import Specialization, Skill, Location
from vacancies.tasks import redis_client
from users.models import User
from django.utils.translation import gettext_lazy as _

from views.models import View


class Vacancy(models.Model):
    TYPE_CHOICES = [('full_time', _('Full Time')),
                    ('part_time', _('Part Time')),
                    ('freelance', _('Freelance'))]

    JOB_FORMAT_CHOICES = [('remote', _('Remote')),
                          ('onsite', _('Onsite'))]

    LANGUAGE_CHOICES = [('en', _('English')),
                        ('ru', _('Russian'))]

    CURRENCY_CHOICES = [('USD', 'USD'),
                        ('RUB', 'RUB'),
                        ('TON', 'TON')]

    PAYMENT_FORMAT_CHOICES = [('hourly', _('Hourly')),
                              ('monthly', _('Monthly')),
                              ('fixed', _('Fixed')),
                              ('yearly', _('Yearly'))]

    EXPERIENCE_CHOICES = [('intern', _('Intern')),
                          ('junior', _('Junior')),
                          ('middle', _('Middle')),
                          ('senior', _('Senior'))]

    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_link = models.URLField(blank=True, null=True)
    info = models.TextField(blank=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    job_format = models.CharField(max_length=100, choices=JOB_FORMAT_CHOICES)
    language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    payment_format = models.CharField(max_length=50, choices=PAYMENT_FORMAT_CHOICES)
    min_payment = models.IntegerField(blank=True, null=True)
    max_payment = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='vacancies')
    experience = models.CharField(max_length=100, choices=EXPERIENCE_CHOICES)
    degree = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, blank=True)
    is_approved = models.BooleanField(default=False)
    response_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def register_view(self, user):
        """Записываем просмотр в Redis"""
        view_data = json.dumps({
            "user_id": user.id,
            "vacancy_id": self.id,
            "timestamp": now().isoformat()
        })
        redis_client.rpush("pending_vacancy_views", view_data)

    def get_views_count(self):
        """Получаем количество просмотров вакансии"""
        content_type = ContentType.objects.get_for_model(Vacancy)
        return View.objects.filter(object_id=self.id, content_type=content_type).count()


class VacancyResponse(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected'))
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vacancy_responses'
    )
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.vacancy.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'vacancy'], name='unique_vacancy_response')
        ]
