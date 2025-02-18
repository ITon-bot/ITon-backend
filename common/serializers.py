from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.reverse import reverse

from common.models import Location, Specialization, Skill, Language, LanguageProficiency, Report


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'latitude', 'longitude']


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['name']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['code', 'name']


class LanguageProficiencySerializer(serializers.ModelSerializer):
    code = serializers.ReadOnlyField(source='language.code')
    name = serializers.ReadOnlyField(source='language.name')

    class Meta:
        model = LanguageProficiency
        fields = ['id', 'code', 'name', 'level']


class ReportSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Report
        fields = ('id', 'reporter', 'content_type', 'object_id', 'message', 'created_at', 'is_resolved')
        read_only_fields = ('id', 'reporter', 'created_at', 'is_resolved')

    def create(self, validated_data):
        content_type_str = validated_data.pop('content_type')
        try:
            app_label, model = content_type_str.split('.')
            content_type = ContentType.objects.get(app_label=app_label, model=model)
        except Exception:
            raise serializers.ValidationError({"content_type": "Неверный формат или тип модели."})

        validated_data['content_type'] = content_type
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class ReportAdminSerializer(serializers.ModelSerializer):
    custom_message = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Сообщение, которое будет отправлено пользователю при закрытии жалобы."
    )
    content_object_display = serializers.SerializerMethodField()
    content_object_url = serializers.SerializerMethodField()
    content_object_details = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = (
            'id',
            'reporter',
            'content_object_display',
            'content_object_url',
            'content_object_details',
            'message',
            'created_at',
            'is_resolved',
            'custom_message'
        )
        read_only_fields = (
            'id',
            'reporter',
            'content_object_display',
            'content_object_url',
            'content_object_details',
            'message',
            'created_at'
        )

    def get_content_object_display(self, obj):
        return str(obj.content_object)

    def get_content_object_url(self, obj):
        request = self.context.get('request')
        if obj.content_type.model == 'vacancy':
            return reverse('vacancy-detail', kwargs={'pk': obj.object_id}, request=request)
        elif obj.content_type.model == 'user':
            return reverse('user-detail', kwargs={'pk': obj.object_id}, request=request)
        return None

    def get_content_object_details(self, obj):
        if obj.content_type.model == 'vacancy':
            from vacancies.serializers import VacancySerializer
            serializer = VacancySerializer(obj.content_object, context=self.context)
            return serializer.data
        elif obj.content_type.model == 'user':
            from users.serializers import UserSerializer

            serializer = UserSerializer(obj.content_object, context=self.context)
            return serializer.data
        return None
