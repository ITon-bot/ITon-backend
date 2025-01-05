from os import environ

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from users.models import Education, AdditionalEducation
from users.tests.utils import create_valid_token


class EducationWithLocationTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.user_data = {
            "id": 99901,
            "username": "edu_tester",
            "first_name": "Edu",
        }
        self.secret_key = environ.get('BOT_TOKEN')
        self.valid_token = create_valid_token(self.secret_key, self.user_data)
        self.auth_header = {"HTTP_AUTHORIZATION": f"tma {self.valid_token}"}

    def test_create_education_with_location(self):
        """
        Создание Education вместе с НОВОЙ Location в одном запросе.
        """
        url = reverse("education-list")
        data = {
            "name": "Harvard University",
            "program": "CS Program",
            "degree": "bachelor",
            "start_date": "2020-09-01",
            "end_date": "2024-06-30",
            "location": {
                "name": "Harvard Square",
                "address": "Cambridge, MA",
                "latitude": 42.3736,
                "longitude": -71.1189
            }
        }

        response = self.client.post(url, data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        edu_obj = Education.objects.get(name="Harvard University")
        self.assertIsNotNone(edu_obj)

        self.assertIsNotNone(edu_obj.location)
        self.assertEqual(edu_obj.location.name, "Harvard Square")
        self.assertEqual(str(edu_obj.location.latitude), "42.373600")
        self.assertEqual(str(edu_obj.location.longitude), "-71.118900")

    def test_create_education_without_location(self):
        """
        Создание Education без поля location (оно не обязательно).
        """
        url = reverse("education-list")
        data = {
            "name": "No Location University",
            "degree": "master",
            "start_date": "2021-01-01",
            "end_date": "2023-12-31",
        }

        response = self.client.post(url, data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        edu_obj = Education.objects.get(name="No Location University")
        self.assertIsNotNone(edu_obj)
        self.assertIsNone(edu_obj.location)

    def test_update_education_location(self):
        """
        Обновление (PATCH) Education, чтобы изменить / добавить location.
        """
        edu_obj = Education.objects.create(
            user_id=self.user_data["id"],
            name="Old University",
            start_date="2019-09-01",
            end_date="2023-06-30",
        )

        url = reverse("education-detail", args=[edu_obj.pk])
        patch_data = {
            "location": {
                "name": "MIT Campus",
                "address": "77 Massachusetts Ave",
                "latitude": 42.3592,
                "longitude": -71.0935
            }
        }
        response = self.client.patch(url, patch_data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        edu_obj.refresh_from_db()
        self.assertIsNotNone(edu_obj.location)
        self.assertEqual(edu_obj.location.name, "MIT Campus")

        patch_data_2 = {
            "location": {
                "name": "MIT Main Building",
                "address": "Mass Ave, Cambridge"
            }
        }
        response = self.client.patch(url, patch_data_2, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        edu_obj.refresh_from_db()
        self.assertEqual(edu_obj.location.name, "MIT Main Building")
        self.assertEqual(edu_obj.location.address, "Mass Ave, Cambridge")


class AdditionalEducationViewSetTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.user_data = {
            "id": 99902,
            "username": "add_edu_tester",
        }
        self.secret_key = environ.get('BOT_TOKEN')
        self.valid_token = create_valid_token(self.secret_key, self.user_data)
        self.auth_header = {"HTTP_AUTHORIZATION": f"tma {self.valid_token}"}

        self.additional_edu_data = {
            "type": "course",
            "name": "Django Advanced",
            "description": "Deep dive into Django",
            "start_date": "2021-01-01",
            "end_date": "2021-06-01",
        }

    def test_create_additional_education(self):
        url = reverse("additional_education-list")
        response = self.client.post(url, self.additional_edu_data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        aedu_id = response.data["id"]
        aedu_obj = AdditionalEducation.objects.get(pk=aedu_id)
        self.assertEqual(aedu_obj.name, "Django Advanced")
        self.assertEqual(aedu_obj.user.id, self.user_data['id'])

    def test_retrieve_additional_education(self):
        aedu_obj = AdditionalEducation.objects.create(
            user_id=self.user_data['id'],
            **self.additional_edu_data
        )
        url = reverse("additional_education-detail", args=[aedu_obj.pk])
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Django Advanced")

    def test_list_additional_education(self):
        AdditionalEducation.objects.create(user_id=self.user_data['id'], name="Course 1", type="course",
                                           start_date="2021-01-01", end_date="2021-02-01")
        AdditionalEducation.objects.create(user_id=self.user_data['id'], name="Course 2", type="course",
                                           start_date="2021-03-01", end_date="2021-04-01")

        url = reverse("additional_education-list")
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_additional_education(self):
        aedu_obj = AdditionalEducation.objects.create(
            user_id=self.user_data['id'],
            **self.additional_edu_data
        )
        url = reverse("additional_education-detail", args=[aedu_obj.pk])
        new_data = {"name": "Django & DRF Mastery"}
        response = self.client.patch(url, new_data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        aedu_obj.refresh_from_db()
        self.assertEqual(aedu_obj.name, "Django & DRF Mastery")

    def test_destroy_additional_education(self):
        aedu_obj = AdditionalEducation.objects.create(
            user_id=self.user_data['id'],
            **self.additional_edu_data
        )
        url = reverse("additional_education-detail", args=[aedu_obj.pk])
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AdditionalEducation.objects.filter(pk=aedu_obj.pk).exists())
