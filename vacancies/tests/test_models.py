from aiohttp.web_fileresponse import content_type
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from common.models import Specialization, Skill
from users.models import User
from vacancies.models import Vacancy, VacancyResponse
from views.models import View


class VacancyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='password')
        self.specialization = Specialization.objects.create(name='Backend Development')
        self.skill = Skill.objects.create(name='Python')
        self.vacancy = Vacancy.objects.create(
            title='Backend Developer',
            creator=self.user,
            company_name='Test Company',
            min_payment=1000,
            max_payment=3000,
            location='Remote',
            degree=True,
            type='full_time',
            job_format='remote',
            currency='USD',
            payment_format='monthly',
            experience='middle'
        )
        self.vacancy.specializations.add(self.specialization)
        self.vacancy.skills.add(self.skill)

    def test_vacancy_creation(self):
        self.assertEqual(self.vacancy.title, 'Backend Developer')
        self.assertEqual(self.vacancy.creator, self.user)
        self.assertEqual(self.vacancy.company_name, 'Test Company')
        self.assertEqual(self.vacancy.min_payment, 1000)
        self.assertEqual(self.vacancy.max_payment, 3000)
        self.assertEqual(self.vacancy.currency, 'USD')

    def test_register_view(self):
        self.vacancy.register_view(self.user)
        # нужно сделать мок redis
        self.assertTrue(True)

    def test_get_views_count(self):
        content_type = ContentType.objects.get_for_model(Vacancy)
        View.objects.create(
            object_id=self.vacancy.id,
            content_type=content_type,
            user=self.user
        )
        self.assertEqual(self.vacancy.get_views_count(), 1)


class VacancyResponseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', username='johndoe')
        self.vacancy = Vacancy.objects.create(
            title='Backend Developer',
            creator=self.user,
            company_name='Test Company',
            min_payment=1000,
            max_payment=3000,
            location='Remote',
            degree=True,
            type='full_time',
            job_format='remote',
            currency='USD',
            payment_format='monthly',
            experience='middle'
        )
        self.vacancy_response = VacancyResponse.objects.create(
            user=self.user,
            vacancy=self.vacancy,
            message='I wan\'t to work here!',
            status='pending',
            is_viewed=False
        )

    def test_vacancy_response_creation(self):
        self.assertEqual(self.vacancy_response.user, self.user)
        self.assertEqual(self.vacancy_response.vacancy, self.vacancy)
        self.assertEqual(self.vacancy_response.status, 'pending')
        self.assertEqual(self.vacancy_response.is_viewed, False)

    def test_vacancy_response_unique_constraint(self):
        with self.assertRaises(Exception):
            VacancyResponse.objects.create(user=self.user, vacancy=self.vacancy)
