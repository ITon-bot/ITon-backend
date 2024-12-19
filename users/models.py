from django.db import models

from common.models import Specialization, Skill


class User(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('hidden', 'Hidden'),
    ]

    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('freelance', 'Freelance'),
    ]

    GOAL_CHOICES = [
        ('career_growth', 'Career Growth'),
        ('personal_development', 'Personal Development'),
        ('networking', 'Networking'),
        ('project_building', 'Building Projects'),
        ('job_search', 'Job Search'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    tg_id = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    specializations = models.ManyToManyField(Specialization, related_name='users')
    skills = models.ManyToManyField(Skill, related_name='users')
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=512, blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES)
    status = models.BooleanField(default=True)
    portfolio = models.URLField(blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    visiability = models.CharField(max_length=50, choices=VISIBILITY_CHOICES, default='public')

    def __str__(self):
        return self.first_name


class Education(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="educations"
    )

    name = models.CharField(max_length=128)
    location = models.CharField(max_length=255, blank=True, null=True)
    program = models.TextField(blank=True, null=True)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.degree})"


class AdditionalEducation(models.Model):
    EDUCATION_TYPE_CHOICES = [
        ('course', 'Course'),
        ('book', 'Book'),
        ('other', 'Other'),
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
