from os import environ

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import Experience
from users.tests.utils import create_valid_token


class ExperienceViewSetTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.user_data = {
            "id": 99903,
            "username": "exp_tester",
        }
        self.secret_key = environ.get('BOT_TOKEN')
        self.valid_token = create_valid_token(self.secret_key, self.user_data)
        self.auth_header = {"HTTP_AUTHORIZATION": f"tma {self.valid_token}"}

        self.experience_data = {
            "company_name": "TestCompany",
            "position": "QA Engineer",
            "start_date": "2022-01-10",
            "end_date": "2023-01-10",
        }

    def test_create_experience(self):
        url = reverse("experience-list")
        response = self.client.post(url, self.experience_data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exp_id = response.data["id"]
        exp_obj = Experience.objects.get(pk=exp_id)
        self.assertEqual(exp_obj.company_name, "TestCompany")
        self.assertEqual(exp_obj.user.id, self.user_data["id"])

    def test_retrieve_experience(self):
        exp_obj = Experience.objects.create(
            user_id=self.user_data['id'],
            **self.experience_data
        )
        url = reverse("experience-detail", args=[exp_obj.pk])
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["position"], "QA Engineer")

    def test_list_experience(self):
        Experience.objects.create(user_id=self.user_data['id'], company_name="Company1", position="Dev",
                                  start_date="2021-01-01")
        Experience.objects.create(user_id=self.user_data['id'], company_name="Company2", position="DevOps",
                                  start_date="2020-06-01")
        url = reverse("experience-list")
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_experience(self):
        exp_obj = Experience.objects.create(user_id=self.user_data['id'], **self.experience_data)
        url = reverse("experience-detail", args=[exp_obj.pk])
        new_data = {"position": "Senior QA"}
        response = self.client.patch(url, new_data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exp_obj.refresh_from_db()
        self.assertEqual(exp_obj.position, "Senior QA")

    def test_destroy_experience(self):
        exp_obj = Experience.objects.create(user_id=self.user_data['id'], **self.experience_data)
        url = reverse("experience-detail", args=[exp_obj.pk])
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Experience.objects.filter(pk=exp_obj.pk).exists())
