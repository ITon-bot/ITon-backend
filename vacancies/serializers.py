import re

from rest_framework import serializers

from common.serializers import SkillSerializer, SpecializationSerializer, LocationSerializer, LanguageSerializer, \
    LanguageProficiencySerializer
from vacancies.models import Vacancy, VacancyResponse


class VacancyCreateSerializer(serializers.ModelSerializer):
    min_payment = serializers.IntegerField(required=False, allow_null=True)
    max_payment = serializers.IntegerField(required=False, allow_null=True)

    def format_payment(self, value):
        """Форматирует число с пробелами при отображении"""
        if value is not None:
            return '{:,}'.format(value).replace(",", " ")
        return value

    def to_representation(self, instance):
        """Форматируем min_payment и max_payment при отправке данных"""
        representation = super().to_representation(instance)
        if representation.get('min_payment') is not None:
            representation['min_payment'] = self.format_payment(representation['min_payment'])
        if representation.get('max_payment') is not None:
            representation['max_payment'] = self.format_payment(representation['max_payment'])
        return representation

    def validate(self, data):
        """Проверка: min_payment всегда должно быть <= max_payment"""
        min_payment = data.get('min_payment')
        max_payment = data.get('max_payment')

        if min_payment is not None and max_payment is not None and min_payment > max_payment:
            raise serializers.ValidationError({'min_payment': 'min_payment должно быть меньше или равно max_payment'})

        return data

    class Meta:
        model = Vacancy
        fields = ['name', 'creator', 'company_name', 'company_link', 'info',
                  'languages', 'specialization', 'min_payment', 'max_payment',
                  'location', 'degree', 'skills', 'type', 'job_format',
                  'currency', 'payment_format', 'experience']


class VacancySerializer(VacancyCreateSerializer):
    specialization = SpecializationSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Vacancy
        fields = '__all__'


class VacancyFeedSerializer(VacancyCreateSerializer):
    match_score = serializers.SerializerMethodField()
    skills = SkillSerializer(many=True, read_only=True)
    specialization = SpecializationSerializer()
    languages = LanguageProficiencySerializer(many=True, read_only=True)

    class Meta:
        model = Vacancy
        fields = [
            'id',
            'name',
            'company_name',
            'type',
            'job_format',
            'experience',
            'languages',
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
    custom_message = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Сообщение, которое будет отправлено кандидату вместе с уведомлением."
    )

    class Meta:
        model = VacancyResponse
        fields = ('status', 'custom_message')


class VacancyApprovalSerializer(serializers.ModelSerializer):
    custom_message = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Дополнительное сообщение для уведомления создателю вакансии."
    )

    class Meta:
        model = Vacancy
        fields = ('approval_status', 'custom_message')
