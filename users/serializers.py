from rest_framework import serializers

from common.models import Specialization
from common.serializers import SpecializationSerializer, SkillSerializer, \
    LanguageProficiencySerializer
from users.models import User, Education, AdditionalEducation, Experience, UserBook
from vacancies.models import VacancyResponse


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)


class UserBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBook
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }


class UserInitUpdateSerializer(serializers.ModelSerializer):
    specialization = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ['goal', 'specialization']
        extra_kwargs = {
            'goal': {'required': False},
        }


class UserSerializer(serializers.ModelSerializer):
    languages = LanguageProficiencySerializer(source='user_languages', many=True, read_only=True)
    specialization = SpecializationSerializer()
    skills = SkillSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'role', 'specialization',
                  'skills', 'bio', 'date_of_birth', 'location', 'languages',
                  'photo_url', 'goal', 'status', 'portfolio', 'job_type',
                  'is_blocked', 'visibility', 'total_experience']


class EducationSerializer(serializers.ModelSerializer):
    """
    Универсальный сериализатор для CRUD операций с моделью Education.
    """

    class Meta:
        model = Education
        fields = ['id', 'user', 'name', 'location', 'program', 'degree', 'start_date', 'end_date']

    def to_representation(self, instance):
        """
        Настройка для представления данных.
        Используется для операций чтения (GET).
        """
        representation = super().to_representation(instance)
        representation.pop('user', None)
        return representation

    def validate(self, data):
        """
        Валидация данных. Пример проверки.
        """
        if data.get('end_date') and data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала.")
        return data


class AdditionalEducationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели AdditionalEducation
    """

    class Meta:
        model = AdditionalEducation
        fields = [
            'id', 'user', 'type', 'name', 'photo',
            'description', 'link', 'start_date', 'end_date'
        ]

    def validate(self, data):
        """
        Проверяем даты на корректность
        """
        if data.get('end_date') and data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала.")
        return data


class ExperienceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Experience
    """

    class Meta:
        model = Experience
        fields = [
            'id', 'user', 'company_name', 'link', 'position',
            'info', 'start_date', 'end_date'
        ]

    def validate(self, data):
        """
        Проверяем даты на корректность
        """
        if data.get('end_date') and data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала.")
        return data


class ProfileSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    additional_educations = AdditionalEducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    languages = LanguageProficiencySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'role',
            'specialization', 'skills', 'bio', 'date_of_birth',
            'location', 'languages', 'photo_url', 'goal', 'status',
            'portfolio', 'job_type', 'is_blocked', 'visibility', 'total_experience',
            'educations', 'additional_educations', 'experiences'
        ]


class MainPageSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    vacancy_response_count = serializers.SerializerMethodField()
    new_vacancy_responses_count = serializers.SerializerMethodField()
    languages = LanguageProficiencySerializer(source='user_languages', many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'specialization',
            'location',
            'languages',
            'goal',
            'vacancy_response_count',
            'new_vacancy_responses_count',
        ]

    def get_vacancy_response_count(self, obj):
        return obj.vacancy_responses.count()

    def get_new_vacancy_responses_count(self, obj):
        return VacancyResponse.objects.filter(
            vacancy__creator_id=obj.pk,
            status='pending',
            is_viewed=False
        ).count()
