from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import Specialization, Skill, Location
from django.utils.translation import gettext_lazy as _

year = 12


class User(AbstractUser):
    """
    Кастомная модель пользователя, унаследованная от AbstractUser.
    """

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
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('ru', _('Russian'))
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    specializations = models.ManyToManyField(Specialization, related_name='users', null=True)
    skills = models.ManyToManyField(Skill, related_name='users', null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='users', blank=True)
    language = models.CharField(max_length=32, choices=LANGUAGE_CHOICES, null=True)
    photo_url = models.URLField(blank=True, null=True)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, null=True, blank=True)
    status = models.BooleanField(default=True)
    portfolio = models.URLField(blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, null=True)
    is_blocked = models.BooleanField(default=False)
    visibility = models.CharField(max_length=50, choices=VISIBILITY_CHOICES, default='public')

    SAFE_FIELDS = ['first_name', 'last_name', 'username', 'photo_url', 'bio']

    def __str__(self):
        return self.first_name or self.username

    @classmethod
    def login(cls, user_dict):
        tg_id = user_dict.get('id')
        if not tg_id:
            raise ValueError("User ID (Telegram ID) is required for login.")

        defaults_dict = {
            key: user_dict[key]
            for key in cls.SAFE_FIELDS
            if key in user_dict
        }

        user, was_created = cls.objects.update_or_create(
            pk=tg_id,
            defaults=defaults_dict
        )
        return user, was_created

    total_experience = models.IntegerField(default=0)

    def calculate_total_experience(self):
        """
        Вычисляет общий опыт работы пользователя на основе его записей в Experience.
        """
        total_days = 0
        for exp in self.experiences.all():
            end_date = exp.end_date if exp.end_date else date.today()
            delta = end_date - exp.start_date
            total_days += delta.days

        self.total_experience = round(total_days / 30, 1)
        self.save()

    def get_experience_level(self):
        """
        Возвращает уровень опыта пользователя (junior, mid, senior) на основе total_experience.
        """
        if self.total_experience < 1 * year:
            return 'intern'
        elif 1 * year  <= self.total_experience < 2 * year:
            return 'junior'
        elif 2 * year<= self.total_experience < 5 * year:
            return 'middle'
        else:
            return 'senior'


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
