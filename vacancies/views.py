from django.db.models import F
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.services import perform_update_and_notify
from vacancies.models import Vacancy, VacancyResponse
from vacancies.serializers import (VacancyFeedSerializer, VacancyCreateSerializer,
                                   VacancyResponseSerializer, VacancyResponseStatusUpdateSerializer,
                                   VacancyApprovalSerializer)

from vacancies.services import annotate_match_score, send_status_notification, send_verification_notification


class VacancyViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    serializer_class = VacancyCreateSerializer
    queryset = Vacancy.objects.all()

    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = Vacancy.objects.select_related('creator', 'location', 'specialization') \
            .prefetch_related('skills') \
            .get(id=pk)

        instance.register_view(request.user)
        views_count = instance.get_views_count()

        serializer = self.get_serializer(instance)
        response_data = serializer.data
        response_data['views_count'] = views_count

        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='feed')
    def feed(self, request, *args, **kwargs):
        qs = self.get_queryset()

        qs = qs.select_related('specialization', 'location')
        qs = qs.prefetch_related('skills', 'creator')

        filters = {}
        if vacancy_type := request.query_params.get('type'):
            filters['type'] = vacancy_type
        if experience := request.query_params.get('experience'):
            filters['experience'] = experience

        qs = qs.filter(**filters)

        qs = annotate_match_score(qs, request.user)

        ordering = request.query_params.get('ordering')
        order_fields = [F(ordering).desc(nulls_last=True), '-match_score'] if ordering in ['min_payment',
                                                                                           'max_payment'] else [
            '-match_score']
        qs = qs.order_by(*order_fields)

        page = self.paginate_queryset(qs)
        serializer = VacancyFeedSerializer(
            page if page is not None else qs,
            many=True,
            context={"request": request}
        )
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='responses')
    def responses(self, request, pk=None):
        vacancy = self.get_object()

        responses_qs = vacancy.responses.all().order_by('is_viewed', '-created_at')
        responses_list = list(responses_qs)

        serializer = VacancyResponseSerializer(responses_list, many=True)

        vacancy.responses.filter(is_viewed=False).update(is_viewed=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class VacancyResponseViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             GenericViewSet):
    queryset = VacancyResponse.objects.all()
    serializer_class = VacancyResponseSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            instance = self.get_object()
            if self.request.user == instance.vacancy.creator:
                return VacancyResponseStatusUpdateSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.vacancy.creator:
            return Response(
                {'detail': 'Изменять отклик может только создатель вакансии.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return perform_update_and_notify(
            view=self,
            request=request,
            update_method=lambda: super(VacancyResponseViewSet, self).update(request, *args, **kwargs),
            field_name='status',
            notification_func=send_status_notification
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.vacancy.creator:
            return Response(
                {'detail': 'Изменять отклик может только создатель вакансии.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return perform_update_and_notify(
            view=self,
            request=request,
            update_method=lambda: super(VacancyResponseViewSet, self).partial_update(request, *args, **kwargs),
            field_name='status',
            notification_func=send_status_notification
        )


class VacancyAdminViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          GenericViewSet):
    """
    ViewSet для администрирования вакансий.
    Позволяет администраторам обновлять поле approval_status.
    При изменении этого поля отправляется уведомление создателю вакансии,
    с возможностью прикрепления дополнительного сообщения.
    """
    queryset = Vacancy.objects.all()
    serializer_class = VacancyApprovalSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        return perform_update_and_notify(
            view=self,
            request=request,
            update_method=lambda: super(VacancyAdminViewSet, self).update(request, *args, **kwargs),
            field_name='approval_status',
            notification_func=send_verification_notification
        )

    def partial_update(self, request, *args, **kwargs):
        return perform_update_and_notify(
            view=self,
            request=request,
            update_method=lambda: super(VacancyAdminViewSet, self).partial_update(request, *args, **kwargs),
            field_name='approval_status',
            notification_func=send_verification_notification
        )
