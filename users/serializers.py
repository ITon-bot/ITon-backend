from rest_framework import serializers

from users.models import User, Education, AdditionalEducation, Experience


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id', 'first_name', 'last_name', 'photo_url']

    def validate_tg_id(self, value):
        if User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Пользователь с таким id уже существует.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    """
    Универсальный сериализатор для CRUD операций с моделью Education.
    """

    class Meta:
        model = Education
        fields = ['id', 'user', 'name', 'location', 'program', 'degree', 'start_date', 'end_date']
        read_only_fields = ['id', 'user']

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
