from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.services import perform_update_and_notify
from vacancies.models import Vacancy, VacancyResponse
from vacancies.serializers import (VacancyFeedSerializer, VacancyMainSerializer,
                                   VacancyResponseSerializer, VacancyResponseStatusUpdateSerializer,
                                   VacancyApprovalSerializer, VacancyResponseShortSerializer)

from vacancies.services import send_status_notification, send_verification_notification, \
    get_vacancy_feed_queryset, get_onboarding_vacancies, annotate_response_match_score


class VacancyViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    serializer_class = VacancyMainSerializer
    queryset = Vacancy.objects.all()

    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = Vacancy.objects.select_related('creator') \
            .prefetch_related('skills', 'specializations', 'languages') \
            .get(id=pk)

        instance.register_view(request.user)
        views_count = instance.get_views_count()

        serializer = self.get_serializer(instance)
        response_data = serializer.data
        response_data['views_count'] = views_count

        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='feed')
    def feed(self, request, *args, **kwargs):
        qs = get_vacancy_feed_queryset(self.get_queryset(), request.query_params, request.user)
        page = self.paginate_queryset(qs)
        serializer = VacancyFeedSerializer(page if page is not None else qs, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='onboarding')
    def onboarding(self, request, *args, **kwargs):
        data = get_onboarding_vacancies(self.get_queryset(), request, VacancyFeedSerializer)
        return Response(data)

    @action(detail=True, methods=['GET'], url_path='responses')
    def responses(self, request, pk=None):
        vacancy = self.get_object()

        if vacancy.type == 'freelance' and vacancy.parent_vacancy is None:
            all_vacancy_ids = list(vacancy.child_vacancies.values_list('id', flat=True)) + [vacancy.id]
            child_vacancies = vacancy.child_vacancies.values('id',
                                                             'specializations__name')
            responses_qs = VacancyResponse.objects.filter(vacancy_id__in=all_vacancy_ids)
        else:
            child_vacancies = []
            responses_qs = vacancy.responses.all()

        child_vacancy_id = request.query_params.get('child_vacancy_id')
        if child_vacancy_id:
            responses_qs = responses_qs.filter(vacancy_id=child_vacancy_id)

        filter_param = request.query_params.get('filter')
        if filter_param == 'new':
            responses_qs = responses_qs.filter(is_viewed=False)
        elif filter_param == 'rejected':
            responses_qs = responses_qs.filter(status='rejected')
        elif filter_param == 'invited':
            responses_qs = responses_qs.filter(status='approved')
        elif filter_param == 'viewed':
            responses_qs = responses_qs.filter(is_viewed=True)

        responses_qs = annotate_response_match_score(responses_qs, vacancy)

        serializer = VacancyResponseShortSerializer(responses_qs.distinct(), many=True)

        vacancy_data = {
            'id': vacancy.id,
            'name': vacancy.name,
            'company_name': vacancy.company_name,
            'approval_status': vacancy.approval_status,
            'response_count': vacancy.response_count,
            'views_count': vacancy.views_count,
            'child_vacancies': {cv['specializations__name']: cv['id'] for cv in child_vacancies}
        }

        return Response(
            {
                'vacancy': vacancy_data,
                'responses': serializer.data
            },
            status=status.HTTP_200_OK
        )


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
