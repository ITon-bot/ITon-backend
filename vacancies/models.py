from django.db import models

from common.models import Specialization, Skill
from users.models import User


class Vacancy(models.Model):
    TYPE_CHOICES = [('full_time', 'Full Time'),
                    ('part_time', 'Part Time'),
                    ('freelance', 'Freelance')]

    JOB_FORMAT_CHOICES = [('remote', 'Remote'),
                          ('onsite', 'Onsite')]

    LANGUAGE_CHOICES = [('en', 'English'),
                        ('ru', 'Russian')]

    CURRENCY_CHOICES = [('USD', 'USD'),
                        ('RUB', 'RUB'),
                        ('TON', 'TON')]

    PAYMENT_FORMAT_CHOICES = [('hourly', 'Hourly'),
                              ('monthly', 'Monthly'),
                              ('fixed', 'Fixed'),
                              ('yearly', 'Yearly')]

    EXPERIENCE_CHOICES = [('junior', 'Junior'),
                          ('mid', 'Mid'),
                          ('senior', 'Senior')]

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
    location = models.CharField(max_length=512, blank=True, null=True)
    experience = models.CharField(max_length=100, choices=EXPERIENCE_CHOICES)
    degree = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, blank=True)
    is_approved = models.BooleanField(default=False)
    response_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class JobResponse(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_responses'
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.vacancy.name}"
