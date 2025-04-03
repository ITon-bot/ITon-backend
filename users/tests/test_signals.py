from django.test import TestCase
from users.models import User, Experience


class UpdateUserExperienceSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_experience_creation_updates_total_experience(self):
        self.assertEqual(self.user.total_experience, 0)

        Experience.objects.create(
            user=self.user, company_name="ITon", position="Dev",
            start_date="2020-01-01", end_date="2022-01-01"
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.total_experience, 24)

    def test_experience_deletion_updates_total_experience(self):
        exp = Experience.objects.create(
            user=self.user, company_name="ITon", position="Dev",
            start_date="2020-01-01", end_date="2022-01-01"
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_experience, 24)

        exp.delete()
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_experience, 0)

    def test_experience_update_updates_total_experience(self):
        exp = Experience.objects.create(
            user=self.user, company_name="ITon", position="Dev",
            start_date="2020-01-01", end_date="2022-01-01"
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_experience, 24)

        exp.end_date = "2023-01-01"
        exp.save()

        self.user.refresh_from_db()
        self.assertEqual(self.user.total_experience, 37)
