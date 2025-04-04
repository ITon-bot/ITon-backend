from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from common.models import Specialization, Skill
from vacancies.models import Vacancy, VacancyResponse

User = get_user_model()


class VacancyViewSetTests(APITestCase):
    def setUp(self):
        self.specialization = Specialization.objects.create(name='Backend Development')
        self.user = User.objects.create(first_name='John', username='johndoe', specialization=self.specialization)
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

    def test_retrieve_vacancy(self):
        url = reverse('vacancies-detail', kwargs={"pk": self.vacancy.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.vacancy.title)

    def test_vacancy_feed(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('vacancies-feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vacancy_onboarding(self):
        url = reverse('vacancies-onboarding')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class VacancyResponseViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='John', username='johndoe')
        self.creator = User.objects.create_user(first_name='Doe', username='doejohn')
        self.client.force_authenticate(user=self.user)
        self.vacancy = Vacancy.objects.create(
            title='Test Vacancy',
            creator=self.creator,
            type='full_time',
            job_format='remote',
            currency='USD',
            payment_format='monthly',
            experience='junior',
            approval_status='pending'
        )
        self.response = VacancyResponse.objects.create(
            user=self.user, vacancy=self.vacancy, message='Interested!'
        )

    def test_create_response(self):
        user = User.objects.create(username='otheruser')
        data = {'user': user.id, 'vacancy': self.vacancy.id, 'message': 'I am interested'}
        url = reverse('vacancy-responses-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_response_forbidden(self):
        data = {'status': 'approved'}
        url = reverse('vacancy-responses-detail', kwargs={'pk': self.response.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VacancyAdminViewSetTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(first_name='Admin', username='admin')
        self.user = User.objects.create_user(first_name='John', username='johndoe')
        self.client.force_authenticate(user=self.admin)
        self.vacancy = Vacancy.objects.create(
            title='Test Vacancy',
            creator=self.user,
            type='full_time',
            job_format='remote',
            currency='USD',
            payment_format='monthly',
            experience='junior',
            approval_status='pending'
        )

    def test_admin_can_update_approval_status(self):
        data = {'approval_status': 'accepted'}
        url = reverse('vacancy-admin-detail', kwargs={'pk': self.vacancy.id})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vacancy.refresh_from_db()
        self.assertEqual(self.vacancy.approval_status, 'accepted')
