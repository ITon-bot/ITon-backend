from django.db import models

from common.models import Specialization, Skill, Location
from django.utils.translation import gettext_lazy as _


# last_login = models.DateTimeField(_("last login"), blank=True, null=True)

class User(models.Model):
    VISIBILITY_CHOICES = [
        ('public', _('Public')),
        ('hidden', _('Hidden')),
    ]

    JOB_TYPE_CHOICES = [
        ('full_time', _('Full Time')),
        ('part_time', _('Part Time')),
        ('freelance', _('Freelance')),
    ]

    GOAL_CHOICES = [
        ('career_growth', _('Career Growth')),
        ('personal_development', _('Personal Development')),
        ('networking', _('Networking')),
        ('project_building', _('Building Projects')),
        ('job_search', _('Job Search')),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    specializations = models.ManyToManyField(Specialization, related_name='users')
    skills = models.ManyToManyField(Skill, related_name='users')
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='users')
    photo_url = models.URLField(blank=True, null=True)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES)
    status = models.BooleanField(default=True)
    portfolio = models.URLField(blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    is_blocked = models.BooleanField(default=False)
    visiability = models.CharField(max_length=50, choices=VISIBILITY_CHOICES, default='public')

    USERNAME_FIELD = 'username'

    SAFE_FIELDS = ['first_name', 'last_name', 'username', 'photo_url', 'bio']

    def __str__(self):
        return self.first_name

    @classmethod
    def login(cls, user_dict):
        tg_id = user_dict.get('id')
        if not tg_id:
            raise ValueError("User ID is required for login.")

        defaults_dict = {key: user_dict[key] for key in cls.SAFE_FIELDS if key in user_dict}

        user, was_created = cls.objects.update_or_create(
            id=tg_id,
            defaults=defaults_dict
        )

        return user, was_created


class Education(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', _('Bachelor')),
        ('master', _('Master')),
        ('other', _('Other')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="educations"
    )

    name = models.CharField(max_length=128)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name="educations")
    program = models.TextField(blank=True, null=True)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    unique_together = ('user', 'location', 'degree')

    def __str__(self):
        return f"{self.name} ({self.degree})"


class AdditionalEducation(models.Model):
    EDUCATION_TYPE_CHOICES = [
        ('course', _('Course')),
        ('book', _('Book')),
        ('other', _('Other')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="additional_education",
    )
    type = models.CharField(
        max_length=50,
        choices=EDUCATION_TYPE_CHOICES,
        default='course'
    )
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='book_photos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.type}) - {self.user.first_name} {self.user.last_name}"


class Experience(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="experiences"
    )
    company_name = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=255)
    info = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def is_current_job(self):
        """Определяет, является ли это место работы текущим."""
        return self.end_date is None
