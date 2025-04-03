from datetime import date

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from common.models import Specialization, Skill, LanguageProficiency
from django.utils.translation import gettext_lazy as _


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

    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Фамилия')
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=100, blank=True, null=True, verbose_name='Роль??')
    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    skills = models.ManyToManyField(Skill, related_name='users')
    bio = models.TextField(blank=True, null=True, verbose_name='О себе')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    location = models.CharField(max_length=128, null=True, blank=True, verbose_name='Локация')
    languages = GenericRelation(
        LanguageProficiency,
        related_query_name='user_languages'
    )
    photo_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на фото')
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, null=True, blank=True, verbose_name='Цель')
    status = models.BooleanField(default=True, verbose_name='Онлайн/оффлайн')
    portfolio = models.URLField(blank=True, null=True, verbose_name='Ссылка на портфолио')
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, null=True, verbose_name='Тип работы')
    is_blocked = models.BooleanField(default=False)
    visibility = models.CharField(max_length=50, choices=VISIBILITY_CHOICES, default='public')
    tg_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name='Telegram ID')
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

        user, was_created = cls.objects.get_or_create(
            tg_id=tg_id,
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

        self.total_experience = round(total_days / 30)
        self.save()

    def get_experience_level(self):
        """
        Возвращает уровень опыта пользователя (junior, mid, senior) на основе total_experience.
        """
        year = 12
        if self.total_experience < year:
            return 'intern'
        elif year <= self.total_experience < 2 * year:
            return 'junior'
        elif 2 * year <= self.total_experience < 5 * year:
            return 'middle'
        else:
            return 'senior'

    def should_show_username(self, viewer):
        """
        Определяет, можно ли показывать username этому пользователю.
        """
        from vacancies.models import VacancyResponse
        if VacancyResponse.objects.filter(user=self, vacancy__creator=viewer, status='approved').exists():
            return True

        if VacancyResponse.objects.filter(user=viewer, vacancy__creator=self, status='approved').exists():
            return True

        return False


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

    name = models.CharField(max_length=128, verbose_name='Название учреждения')
    location = models.CharField(max_length=128, blank=True, verbose_name='Место обучения')
    program = models.CharField(max_length=64, verbose_name='Направление обучения')
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, verbose_name='Степень обучения')
    start_date = models.DateField(verbose_name='Дата начала обучения')
    end_date = models.DateField(blank=True, null=True, verbose_name='Дата окончания обучения')

    class Meta:
        unique_together = ('user', 'name', 'location', 'degree', 'program')

    def __str__(self):
        return f"{self.name} ({self.degree})"


class UserBook(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='books'
    )
    title = models.CharField(max_length=500, verbose_name=_("Название"))
    authors = models.JSONField(default=list, verbose_name=_("Авторы"))
    publish_year = models.PositiveSmallIntegerField(verbose_name=_("Год издания"))
    cover_url = models.URLField(verbose_name=_("Обложка"))

    class Meta:
        unique_together = ['user', 'title']
        verbose_name = _("Книга пользователя")
        verbose_name_plural = _("Книги пользователей")

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AdditionalEducation(models.Model):
    EDUCATION_TYPE_CHOICES = [
        ('course', _('Course')),
        ('test', _('Test')),
        ('event', _('Event'))
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
        return f"{self.user} - {self.name}({self.type})"


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

    def __str__(self):
        return f'{self.user} - {self.company_name}'

    def is_current_job(self):
        """Определяет, является ли это место работы текущим."""
        return self.end_date is None
