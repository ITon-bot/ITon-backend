from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Education, AdditionalEducation, Experience
from vacancies.models import Vacancy

User = get_user_model()


class UserViewSetTest(APITestCase):
    def setUp(self):
        """Создаем тестового пользователя"""
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username="johndoe"
        )
        self.client.force_authenticate(user=self.user)

    def test_onboarding_required(self):
        """Проверяем, что `req_onboarding=True`, если у пользователя нет цели"""
        url = reverse('users-onboarding')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["req_onboarding"])

    def test_onboarding_not_required(self):
        """Проверяем, что `req_onboarding=False`, если у пользователя есть цель"""
        self.user.goal = "job_search"
        self.user.save()
        url = reverse('users-onboarding')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["req_onboarding"])

    def test_initial_update_profile_success(self):
        """Проверяем успешное обновление профиля"""
        url = reverse('users-initial-update-profile')
        response = self.client.put(
            url,
            {"goal": "job_search"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.goal, "job_search")

    def test_initial_update_profile_invalid(self):
        """Проверяем ошибку валидации"""
        url = reverse('users-initial-update-profile')
        response = self.client.put(
            url,
            {"goal": "123"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile(self):
        """Получение профиля"""
        url = reverse('users-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")

    def test_main_page(self):
        """Проверяем API `/main`"""
        url = reverse('users-main-page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vacancies_list(self):
        """Проверяем, что пользователь может получить свои вакансии"""
        Vacancy.objects.create(title="Python Dev", creator=self.user)
        url = reverse('users-vacancies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class EducationViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='John', last_name='Doe', username="johndoe")
        self.client.force_authenticate(user=self.user)
        self.education = Education.objects.create(
            user=self.user,
            name="Test Uni",
            start_date='2024-11-02',
            end_date='2025-01-01'
        )

    def test_create_education(self):
        url = reverse('educations-list')
        response = self.client.post(url, {
            "user": self.user.id,
            "name": "New University",
            "program": "SE",
            "location": "somewhere",
            "degree": 'bachelor',
            "start_date": "2022-11-02"
        })
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_education(self):
        url = reverse('educations-detail', kwargs={"pk": self.education.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_education(self):
        url = reverse('educations-detail', kwargs={"pk": self.education.pk})
        response = self.client.patch(url, {"name": "Updated Uni"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.name, "Updated Uni")

    def test_delete_education(self):
        url = reverse('educations-detail', kwargs={"pk": self.education.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AdditionalEducationViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='John', last_name='Doe', username="johndoe")
        self.client.force_authenticate(user=self.user)
        self.add_edu = AdditionalEducation.objects.create(
            user=self.user,
            name="Online Course",
            start_date='2024-11-20',
            type="course"
        )

    def test_create_additional_education(self):
        url = reverse('additional-educations-list')
        response = self.client.post(url, {
            "user": self.user.id,
            "name": "New Course",
            "type": "course",
            "start_date": "2024-11-20"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_additional_education(self):
        url = reverse('additional-educations-detail', kwargs={"pk": self.add_edu.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ExperienceViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='John', last_name='Doe', username="johndoe")
        self.client.force_authenticate(user=self.user)
        self.experience = Experience.objects.create(
            user=self.user,
            company_name="ITon",
            position="Dev",
            start_date='2024-11-20',
            end_date='2024-11-21'
        )

    def test_create_experience(self):
        url = reverse('experiences-list')
        response = self.client.post(url, {
            "user": self.user.id,
            "company_name": "New Company",
            "position": "Manager",
            "start_date": "2024-11-22"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_experience(self):
        url = reverse('experiences-detail', kwargs={"pk": self.experience.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
