from os import environ

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from users.models import User
from users.tests.utils import create_valid_token


class UserWithLocationTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.user_data = {
            "id": 12345,
            "username": "location_user",
            "first_name": "Loc",
            "last_name": "Tester"
        }
        self.secret_key = environ.get('BOT_TOKEN')
        self.valid_token = create_valid_token(self.secret_key, self.user_data)
        self.auth_header = {"HTTP_AUTHORIZATION": f"tma {self.valid_token}"}

    def test_update_user_location(self):
        """
        Если юзер уже есть, обновим его локацию через PATCH
        """
        user_obj = User.objects.create(
            id=54321,
            username="existing_user",
            first_name="Exist",
            last_name="User"
        )
        url = reverse("user-detail", args=[user_obj.pk])

        patch_data = {
            "location": {
                "name": "New York City",
                "address": "Manhattan",
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
        response = self.client.patch(url, patch_data, format="json", **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_obj.refresh_from_db()
        self.assertIsNotNone(user_obj.location)
        self.assertEqual(user_obj.location.name, "New York City")
        self.assertEqual(str(user_obj.location.latitude), "40.712800")
