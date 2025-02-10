from rest_framework import serializers

from common.serializers import SkillSerializer, SpecializationSerializer, LocationSerializer
from vacancies.models import Vacancy, VacancyResponse


class VacancySerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Vacancy
        fields = '__all__'


class VacancyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = '__all__'


class VacancyFeedSerializer(serializers.ModelSerializer):
    match_score = serializers.SerializerMethodField()
    skills = SkillSerializer(many=True, read_only=True)
    specialization = SpecializationSerializer()

    class Meta:
        model = Vacancy
        fields = [
            'id',
            'name',
            'company_name',
            'type',
            'job_format',
            'experience',
            'min_payment',
            'max_payment',
            'specialization',
            'skills',
            'location',
            'match_score',
        ]

    def get_match_score(self, obj):
        """
        Возвращает значение match_score, которое было аннотировано в QuerySet.
        """
        if hasattr(obj, 'match_score'):
            return obj.match_score
        return None


class VacancyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyResponse
        fields = ['user', 'vacancy', 'message', 'status', 'is_viewed', 'created_at']


class VacancyResponseStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyResponse
        fields = ('status',)
