from django.conf.global_settings import LANGUAGE_COOKIE_NAME
from django.core.cache import cache
from rest_framework import mixins, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from common.models import Specialization, Skill, Report
from common.serializers import SpecializationSerializer, SkillSerializer, ReportSerializer, ReportAdminSerializer, \
    LanguageSerializer
from common.services import perform_update_and_notify
from core.settings import LANGUAGES, CACHE_TTL
from vacancies.services import send_report_closed_notification
from django.utils.translation import gettext as _, activate


class SpecializationViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()

    def get_queryset(self):
        return self.queryset

    def list(self, request):
        cached_data = cache.get('all_specializations')
        if cached_data:
            return Response(cached_data)

        queryset = Specialization.objects.all().order_by('name')
        serializer = SpecializationSerializer(queryset, many=True)
        data = serializer.data
        cache.set('all_specializations', data, timeout=CACHE_TTL)
        return Response(data)


class SkillViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()

    def get_queryset(self):
        return self.queryset

    def list(self, request):
        cached_data = cache.get('all_skills')
        if cached_data:
            return Response(cached_data)

        queryset = Skill.objects.all().order_by('name')
        serializer = SkillSerializer(queryset, many=True)
        data = serializer.data
        cache.set('all_skills', data, timeout=CACHE_TTL)
        return Response(data)


class ReportViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class ReportAdminViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    """
    Админский ViewSet для работы с жалобами.
    Позволяет просматривать список жалоб с фильтрацией по статусу, обновлять их (например, закрывать тикеты),
    а при закрытии отправлять уведомление пользователю, отправившему жалобу.
    """
    queryset = Report.objects.all()
    serializer_class = ReportAdminSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['is_resolved']

    def update(self, request, *args, **kwargs):
        return perform_update_and_notify(
            view=self,
            request=request,
            update_method=lambda: super(ReportAdminViewSet, self).update(request, *args, **kwargs),
            field_name='is_resolved',
            notification_func=send_report_closed_notification
        )

    def partial_update(self, request, *args, **kwargs):
        return perform_update_and_notify(
            view=self,
            request=request,
            update_method=lambda: super(ReportAdminViewSet, self).partial_update(request, *args, **kwargs),
            field_name='is_resolved',
            notification_func=send_report_closed_notification
        )


class SetLanguageView(APIView):
    """
    Эндпоинт для смены языка.
    """

    def post(self, request, *args, **kwargs):
        serializer = LanguageSerializer(data=request.data)
        if serializer.is_valid():
            lang_code = serializer.validated_data['language']

            if lang_code not in dict(LANGUAGES):
                return Response({"error": _("Invalid language code")}, status=status.HTTP_400_BAD_REQUEST)

            activate(lang_code)

            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code

            response = Response({"detail": _("Language has been changed.")}, status=status.HTTP_200_OK)
            response.set_cookie(LANGUAGE_COOKIE_NAME, lang_code, max_age=31536000)

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
