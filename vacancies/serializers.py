from rest_framework import serializers
from common.models import Specialization, Skill, Language
from vacancies.models import Vacancy, VacancyResponse


class VacancyMainSerializer(serializers.ModelSerializer):
    specializations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Specialization.objects.all(),
        required=False
    )
    skills = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        required=False
    )

    languages = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Language.objects.all(),
        required=False
    )

    min_payment = serializers.IntegerField(required=False, allow_null=True)
    max_payment = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Vacancy
        fields = [
            'name', 'creator', 'company_name', 'company_link', 'info',
            'languages', 'specializations', 'min_payment', 'max_payment',
            'location', 'degree', 'skills', 'type', 'job_format',
            'currency', 'payment_format', 'experience',
        ]

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
        """Проверка: min_payment <= max_payment"""
        min_payment = data.get('min_payment')
        max_payment = data.get('max_payment')
        if min_payment is not None and max_payment is not None and min_payment > max_payment:
            raise serializers.ValidationError(
                {'min_payment': 'min_payment должно быть меньше или равно max_payment'}
            )
        return data

    def create(self, validated_data):
        """
        Если type='freelance' и передано несколько specializations,
        то создаем родительскую вакансию и дочерние (по одной на каждую специализацию).
        Иначе — обычное поведение.
        """
        specializations = list(validated_data.pop('specializations', []))
        skills = list(validated_data.pop('skills', []))
        languages = list(validated_data.pop('languages', []))
        vacancy_type = validated_data.get('type')

        if vacancy_type != 'freelance' or len(specializations) <= 1:
            vacancy = super().create(validated_data)
            vacancy.specializations.set(specializations)
            vacancy.skills.set(skills)
            vacancy.languages.set(languages)
            return vacancy

        parent_vacancy = Vacancy.objects.create(**validated_data)
        parent_vacancy.specializations.set(specializations)
        parent_vacancy.skills.set(skills)

        for spec in specializations:
            child_vacancy = Vacancy.objects.create(
                parent_vacancy=parent_vacancy,
                **validated_data
            )
            child_vacancy.specializations.set([spec])
            child_vacancy.skills.set(skills)

        return parent_vacancy


class VacancyListSerializer(serializers.ModelSerializer):
    # approval_status_display = serializers.CharField(source='get_approval_status_display')

    class Meta:
        model = Vacancy
        fields = [
            'id',
            'name',
            'company_name',
            'approval_status',
            'response_count',
            'views_count',
            'type',
            'job_format',
        ]


class VacancySerializer(VacancyMainSerializer):
    specializations = serializers.SerializerMethodField(read_only=True)
    skills = serializers.SerializerMethodField(read_only=True)
    languages = serializers.SerializerMethodField(read_only=True)

    class Meta(VacancyMainSerializer.Meta):
        fields = '__all__'

    def get_specializations(self, obj):
        return [
            {
                'id': spec.id,
                'name': spec.name,  # пример
            }
            for spec in obj.specializations.all()
        ]

    def get_skills(self, obj):
        return [
            {
                'id': skill.id,
                'name': skill.name,
            }
            for skill in obj.skills.all()
        ]

    def get_languages(self, obj):
        return [
            {
                'id': lang.id,
                'language': lang.language.name,
                'level': lang.level,
            }
            for lang in obj.languages.all()
        ]


class VacancyFeedSerializer(VacancyMainSerializer):
    match_score = serializers.SerializerMethodField()
    specializations = serializers.SerializerMethodField(read_only=True)
    skills = serializers.SerializerMethodField(read_only=True)
    languages = serializers.SerializerMethodField(read_only=True)

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
            'specializations',
            'skills',
            'location',
            'match_score',
        ]

    def get_match_score(self, obj):
        """
        Возвращает значение match_score, которое было аннотировано в QuerySet.
        """
        return getattr(obj, 'match_score', None)

    def get_specializations(self, obj):
        return [
            {
                'id': spec.id,
                'name': spec.name,
            }
            for spec in obj.specializations.all()
        ]

    def get_skills(self, obj):
        return [
            {
                'id': skill.id,
                'name': skill.name,
            }
            for skill in obj.skills.all()
        ]

    def get_languages(self, obj):
        return [
            {
                'id': lang.id,
                'language': lang.language.name,
                'level': lang.level,
            }
            for lang in obj.languages.all()
        ]


class VacancyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyResponse
        fields = ['user', 'vacancy', 'message', 'status', 'is_viewed', 'created_at']


class VacancyResponseShortSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    match_score = serializers.FloatField(read_only=True)

    class Meta:
        model = VacancyResponse
        fields = ['id', 'first_name', 'status', 'match_score']


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
