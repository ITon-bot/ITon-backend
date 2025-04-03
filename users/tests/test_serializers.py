from django.test import TestCase

from common.models import Specialization
from users.models import User, Education, AdditionalEducation, Experience
from users.serializers import UserSerializer, EducationSerializer, MainPageSerializer, AdditionalEducationSerializer, \
    ExperienceSerializer
from vacancies.models import VacancyResponse, Vacancy


class UserSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            bio="Software Developer",
            goal="career_growth",
            total_experience=24
        )

    def test_user_serializer(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["username"], "johndoe")
        self.assertEqual(data["bio"], "Software Developer")
        self.assertEqual(data["goal"], "career_growth")
        self.assertEqual(data["total_experience"], 24)


class EducationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.education_data = {
            "user": self.user,
            "name": "MIT",
            "location": "USA",
            "program": "Computer Science",
            "degree": "bachelor",
            "start_date": "2020-09-01",
            "end_date": "2024-06-01",
        }
        self.education = Education.objects.create(**self.education_data)

    def test_education_serializer(self):
        serializer = EducationSerializer(instance=self.education)
        data = serializer.data

        self.assertEqual(data["name"], "MIT")
        self.assertEqual(data["location"], "USA")
        self.assertEqual(data["program"], "Computer Science")
        self.assertEqual(data["degree"], "bachelor")

    def test_education_invalid_dates(self):
        invalid_data = self.education_data.copy()
        invalid_data["user"] = self.user.id
        invalid_data["location"] = "DSU"
        invalid_data["start_date"] = "2025-01-01"
        invalid_data["end_date"] = "2024-01-01"

        serializer = EducationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(serializer.errors["non_field_errors"][0],
                         "Дата окончания не может быть раньше даты начала.")


class ExperienceSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="devuser")
        self.experience_data = {
            "user": self.user,
            "company_name": "Tech Corp",
            "position": "Backend Developer",
            "start_date": "2021-05-01",
            "end_date": "2023-04-01",
        }
        self.experience = Experience.objects.create(**self.experience_data)

    def test_experience_serializer(self):
        serializer = ExperienceSerializer(instance=self.experience)
        data = serializer.data

        self.assertEqual(data["company_name"], "Tech Corp")
        self.assertEqual(data["position"], "Backend Developer")

    def test_education_invalid_dates(self):
        invalid_data = self.experience_data.copy()
        invalid_data['user'] = self.user.id
        invalid_data["start_date"] = "2025-01-01"
        invalid_data["end_date"] = "2024-01-01"

        serializer = ExperienceSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(serializer.errors["non_field_errors"][0],
                         "Дата окончания не может быть раньше даты начала.")


class AdditionalEducationSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="eduuser")
        self.additional_education_data = {
            "user": self.user,
            "type": "course",
            "name": "Advanced Python",
            "start_date": "2022-01-01",
            "end_date": "2022-06-01",
        }
        self.additional_education = AdditionalEducation.objects.create(**self.additional_education_data)

    def test_additional_education_serializer(self):
        serializer = AdditionalEducationSerializer(instance=self.additional_education)
        data = serializer.data

        self.assertEqual(data["name"], "Advanced Python")
        self.assertEqual(data["type"], "course")

    def test_education_invalid_dates(self):
        invalid_data = self.additional_education_data.copy()
        invalid_data['user'] = self.user.id
        invalid_data["start_date"] = "2025-01-01"
        invalid_data["end_date"] = "2024-01-01"

        serializer = AdditionalEducationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(serializer.errors["non_field_errors"][0],
                         "Дата окончания не может быть раньше даты начала.")


class MainPageSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="mainuser")
        self.specialization = Specialization.objects.create(name="Backend Development")
        self.user.specialization = self.specialization
        self.user.save()

        self.vacancy = Vacancy.objects.create(
            creator=self.user, title="Backend Developer", description="Django Developer"
        )

        self.vacancy_response = VacancyResponse.objects.create(
            user=self.user, vacancy=self.vacancy, status="pending", is_viewed=False
        )

    def test_main_page_serializer(self):
        serializer = MainPageSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data["vacancy_response_count"], 1)
        self.assertEqual(data["new_vacancy_responses_count"], 1)
