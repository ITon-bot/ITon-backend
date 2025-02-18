from rest_framework import mixins
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet

from common.models import Specialization, Skill, Report
from common.serializers import SpecializationSerializer, SkillSerializer, ReportSerializer, ReportAdminSerializer
from common.services import perform_update_and_notify
from vacancies.services import send_report_closed_notification


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
