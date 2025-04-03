from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from users.models import User, Specialization, Skill, Experience, Education, AdditionalEducation, UserBook

from vacancies.models import Vacancy


class UserModelTest(TestCase):
    def setUp(self):
        self.specialization = Specialization.objects.create(name='Backend Developer')
        self.skill = Skill.objects.create(name='Python')

        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'role': 'developer',
            'specialization': self.specialization,
            'bio': 'A passionate developer.',
            'date_of_birth': '1990-01-01',
            'location': 'Remote',
            'photo_url': 'http://example.com/photo.jpg',
            'goal': 'career_growth',
            'status': True,
            'portfolio': 'http://example.com/portfolio',
            'job_type': 'full_time',
            'tg_id': 123456789,
        }

        self.user = User.objects.create(**self.user_data)

    def test_user_creation(self):
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.role, 'developer')
        self.assertEqual(self.user.specialization.name, 'Backend Developer')

    def test_calculate_total_experience(self):
        Experience.objects.create(
            user=self.user,
            company_name='ITon',
            position='Software Developer',
            start_date='2015-05-01',
            end_date='2018-05-01'
        )
        self.user.calculate_total_experience()
        self.assertEqual(self.user.total_experience, 37)

    def test_get_experience_level(self):
        self.user.total_experience = 18
        self.assertEqual(self.user.get_experience_level(), 'junior')

        self.user.total_experience = 48
        self.assertEqual(self.user.get_experience_level(), 'middle')

    def test_should_show_username(self):
        viewer = User.objects.create(username='viewer', first_name='Viewer', tg_id=987654321)

        self.assertFalse(self.user.should_show_username(viewer))

        vacancy = Vacancy.objects.create(
            title='Python Backend Developer',
            creator=viewer,
        )

        from vacancies.models import VacancyResponse
        VacancyResponse.objects.create(user=self.user, vacancy=vacancy, status='approved')
        self.assertTrue(self.user.should_show_username(viewer))


class EducationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            first_name='John',
            username='johndoe'
        )
        self.education_data = {
            'user': self.user,
            'name': 'DSU',
            'location': 'Russia',
            'program': 'Software Engineering',
            'degree': 'bachelor',
            'start_date': '2022-09-01',
            'end_date': '2026-06-01'
        }
        self.education = Education.objects.create(**self.education_data)

    def test_education_creation(self):
        self.assertEqual(self.education.name, 'DSU')
        self.assertEqual(self.education.location, 'Russia')
        self.assertEqual(self.education.program, 'Software Engineering')
        self.assertEqual(self.education.degree, 'bachelor')

    def test_education_unique_together(self):
        with self.assertRaises(Exception):
            Education.objects.create(
                user=self.user,
                name='DSU',
                location='Russia',
                program='Software Engineering',
                degree='bachelor',
                start_date='2020-09-01'
            )


class UserBookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe'
        )

        self.book = UserBook.objects.create(
            user=self.user,
            title='Clean Code',
            authors=['Robert C. Martin'],
            publish_year=2008,
            cover_url='http://example.com/clean-code.jpg'
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'Clean Code')
        self.assertEqual(self.book.authors, ['Robert C. Martin'])
        self.assertEqual(self.book.publish_year, 2008)
        self.assertEqual(str(self.book), 'johndoe - Clean Code')

    def test_book_unique_together(self):
        with self.assertRaises(Exception):
            UserBook.objects.create(
                user=self.user,
                title='Clean Code',
                authors=['Robert C. Martin'],
                publish_year=2008
            )


class AdditionalEducationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
        )

        self.photo = SimpleUploadedFile(
            name='test_cert.jpg',
            content=b'simple image content',
            content_type='image/jpeg'
        )

        self.course = AdditionalEducation.objects.create(
            user=self.user,
            type='course',
            name='Django Advanced',
            photo=self.photo,
            description='Advanced Django course',
            link='http://example.com/django-advanced',
            start_date='2023-01-15',
            end_date='2023-03-15'
        )

    def test_additional_education_creation(self):
        self.assertEqual(self.course.type, 'course')
        self.assertEqual(self.course.name, 'Django Advanced')
        self.assertTrue(self.course.photo.name.startswith('book_photos/'))
        self.assertEqual(self.course.description, 'Advanced Django course')
        self.assertEqual(str(self.course), 'johndoe - Django Advanced(course)')

    def test_additional_education_types(self):
        test_event = AdditionalEducation.objects.create(
            user=self.user,
            type='event',
            name='Tech Conference 2023',
            start_date='2023-05-10'
        )
        self.assertEqual(test_event.type, 'event')


class ExperienceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe'
        )

        self.current_job = Experience.objects.create(
            user=self.user,
            company_name='Google',
            link='https://google.com',
            position='Software Engineer',
            info='Developing cool stuff',
            start_date='2022-01-01'
        )

        self.past_job = Experience.objects.create(
            user=self.user,
            company_name='Microsoft',
            position='Junior Developer',
            start_date='2020-01-01',
            end_date='2021-12-31'
        )

    def test_experience_creation(self):
        self.assertEqual(self.current_job.company_name, 'Google')
        self.assertEqual(self.current_job.position, 'Software Engineer')
        self.assertTrue(self.current_job.is_current_job())
        self.assertFalse(self.past_job.is_current_job())

    def test_experience_str_representation(self):
        self.assertEqual(str(self.current_job), 'johndoe - Google')
