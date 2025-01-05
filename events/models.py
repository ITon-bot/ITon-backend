from django.db import models

from common.models import Skill, Specialization, Location
from users.models import User
from views.models import View
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    TYPE_CHOICES = [('conference', 'Conference'),
                    ('meetup', _('Meetup'))]

    LANGUAGE_CHOICES = [('en', _('English')),
                        ('ru', _('Russian'))]

    FORMAT_CHOICES = [('online', _('Online')),
                      ('offline', _('Offline')),
                      ('hybrid', _('Hybrid'))]

    JOIN_TYPE_CHOICES = [('open', _('Open')),
                         ('invite_only', _('Invite Only'))]

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
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='events')
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

    def view_count(self):
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(Event)
        return View.objects.filter(content_type=content_type, object_id=self.id).count()


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
