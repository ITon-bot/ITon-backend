from rest_framework import serializers

from common.models import Location
from common.serializers import LocationSerializer, SpecializationSerializer, SkillSerializer
from users.models import User, Education, AdditionalEducation, Experience
from vacancies.models import VacancyResponse


class UserSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False, allow_null=True)

    specializations = SpecializationSerializer(many=True)
    skills = SkillSerializer(many=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'role', 'specializations',
                  'skills', 'bio', 'date_of_birth', 'location', 'language',
                  'photo_url', 'goal', 'status', 'portfolio', 'job_type',
                  'is_blocked', 'visibility', 'total_experience']

    def create(self, validated_data):
        location_data = validated_data.pop('location', None)
        if location_data:
            loc = Location.objects.create(**location_data)
            validated_data['location'] = loc
        else:
            validated_data['location'] = None

        user = super().create(validated_data)

        return user

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        if location_data is not None:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)
        elif 'location' in self.initial_data and self.initial_data['location'] is None:
            instance.location = None

        user = super().update(instance, validated_data)

        return user


class EducationSerializer(serializers.ModelSerializer):
    """
    Универсальный сериализатор для CRUD операций с моделью Education.
    """
    location = LocationSerializer(required=False, allow_null=True)

    class Meta:
        model = Education
        fields = ['id', 'user', 'name', 'location', 'program', 'degree', 'start_date', 'end_date']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        """
        Если в POST-запросе пришли поля location: {...},
        создаём новую запись в Location. Если не пришли — location=None.
        """
        location_data = validated_data.pop('location', None)
        if location_data:
            loc = Location.objects.create(**location_data)
            validated_data['location'] = loc
        else:
            validated_data['location'] = None

        return Education.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Если нужно обновлять Education+Location PATCH/PUT запросом.
        """
        location_data = validated_data.pop('location', None)

        if location_data is not None:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        return super().update(instance, validated_data)

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
        read_only_fields = ['id', 'user']

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
        read_only_fields = ['id', 'user']

    def validate(self, data):
        """
        Проверяем даты на корректность
        """
        if data.get('end_date') and data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала.")
        return data


class ProfileSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False, allow_null=True)
    specializations = SpecializationSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    additional_education = AdditionalEducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'role', 'specializations',
            'skills', 'bio', 'date_of_birth', 'location', 'language', 'photo_url', 'goal',
            'status', 'portfolio', 'job_type', 'is_blocked', 'visibility', 'total_experience',
            'educations', 'additional_education', 'experiences'
        ]


class ProfileMainSerializer(serializers.ModelSerializer):
    specializations = SpecializationSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    vacancy_response_count = serializers.SerializerMethodField()
    new_vacancy_responses_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'specializations',
            'location',
            'language',
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
