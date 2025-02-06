from django.db.models import F
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from vacancies.models import Vacancy
from vacancies.serializers import VacancySerializer, VacancyFeedSerializer

from vacancies.services import annotate_match_score


class VacancyViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    serializer_class = VacancySerializer
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
