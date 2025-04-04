from django.test import TestCase
from users.models import User
from vacancies.models import Vacancy, VacancyResponse
from common.models import Specialization, Skill
from vacancies.serializers import (
    VacancyMainSerializer,
    VacancyListSerializer,
    VacancySerializer,
    VacancyFeedSerializer,
    VacancyResponseSerializer,
    VacancyResponseShortSerializer,
    VacancyResponseStatusUpdateSerializer,
    VacancyApprovalSerializer
)


class VacancySerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', username='johndoe')
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

    def test_vacancy_main_serializer(self):
        serializer = VacancyMainSerializer(instance=self.vacancy)
        data = serializer.data
        self.assertEqual(data['title'], 'Backend Developer')
        self.assertEqual(data['company_name'], 'Test Company')
        self.assertEqual(data['min_payment'], '1 000')
        self.assertEqual(data['max_payment'], '3 000')

    def test_vacancy_list_serializer(self):
        serializer = VacancyListSerializer(instance=self.vacancy)
        data = serializer.data
        self.assertEqual(data['title'], 'Backend Developer')
        self.assertEqual(data['approval_status'], 'pending')

    def test_vacancy_serializer(self):
        serializer = VacancySerializer(instance=self.vacancy)
        data = serializer.data
        self.assertEqual(data['title'], 'Backend Developer')
        self.assertTrue('specializations' in data)
        self.assertTrue('skills' in data)

    def test_vacancy_feed_serializer(self):
        serializer = VacancyFeedSerializer(instance=self.vacancy)
        data = serializer.data
        self.assertEqual(data['title'], 'Backend Developer')
        self.assertTrue('match_score' in data)


class VacancyResponseSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name='John', username='johndoe')
        self.vacancy = Vacancy.objects.create(
            title='Backend Developer',
            creator=self.user,
            type='full_time',
            job_format='remote',
            currency='USD',
            payment_format='monthly',
            experience='middle'
        )
        self.response = VacancyResponse.objects.create(
            user=self.user,
            vacancy=self.vacancy,
            message='I am interested in this position',
            status='pending'
        )

    def test_vacancy_response_serializer(self):
        serializer = VacancyResponseSerializer(instance=self.response)
        data = serializer.data
        self.assertEqual(data['message'], 'I am interested in this position')
        self.assertEqual(data['status'], 'pending')

    def test_vacancy_response_status_update_serializer(self):
        data = {'status': 'approved', 'custom_message': 'Congratulations!'}
        serializer = VacancyResponseStatusUpdateSerializer(instance=self.response, data=data)
        self.assertTrue(serializer.is_valid())

    def test_vacancy_approval_serializer(self):
        data = {'approval_status': 'accepted', 'custom_message': 'Your vacancy has been approved!'}
        serializer = VacancyApprovalSerializer(instance=self.vacancy, data=data)
        self.assertTrue(serializer.is_valid())
