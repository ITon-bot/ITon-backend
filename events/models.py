from django.db import models

from common.models import Skill, Specialization
from users.models import User


class Event(models.Model):
    TYPE_CHOICES = [('conference', 'Conference'),
                    ('meetup', 'Meetup')]

    LANGUAGE_CHOICES = [('en', 'English'),
                        ('ru', 'Russian')]

    FORMAT_CHOICES = [('online', 'Online'),
                      ('offline', 'Offline'),
                      ('hybrid', 'hybrid')]

    JOIN_TYPE_CHOICES = [('open', 'Open'),
                         ('invite_only', 'Invite Only')]

    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_link = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    specializations = models.ManyToManyField(Specialization, related_name='events')
    skills = models.ManyToManyField(Skill, blank=True)
    language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES)
    info = models.TextField()
    photo = models.ImageField(upload_to='event_photos/', blank=True, null=True)
    format = models.CharField(max_length=100,
                              choices=FORMAT_CHOICES)
    location = models.CharField(max_length=512, blank=True, null=True)
    age_restriction = models.IntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField(blank=True, null=True)
    join_type = models.CharField(max_length=100, choices=JOIN_TYPE_CHOICES)
    join_link = models.URLField(blank=True, null=True)
    tg_chat = models.URLField(blank=True, null=True)
    tg_link = models.URLField(blank=True, null=True)
    participants = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Speaker(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='speaker_photos/')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Partner(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField()
    logo = models.ImageField(upload_to='partner_logos/')

    def __str__(self):
        return self.name


class EventParticipant(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_participations'
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='participants'
    )
    is_approved = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.event.name}"
