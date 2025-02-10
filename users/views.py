from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet

from .models import User, Education, AdditionalEducation, Experience
from .serializers import EducationSerializer, AdditionalEducationSerializer, \
    ExperienceSerializer, UserSerializer, ProfileSerializer, ProfileMainSerializer


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=['GET'], url_path='onboarding')
    def onboarding(self, request):
        if not request.user.goal:
            requires = True
        else:
            requires = False
        return Response({"req_onboarding": requires}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='profile')
    def profile(self, request):
        user = User.objects.select_related('location') \
            .prefetch_related(
            'specializations',
            'skills',
            Prefetch('educations', queryset=Education.objects.select_related('location')),
            'additional_education',
            'experiences'
        ).get(pk=request.user.pk)

        serializer = ProfileSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='main')
    def main_page(self, request):
        user = User.objects.select_related('location') \
            .prefetch_related('specializations') \
            .get(pk=request.user.pk)

        serializer = ProfileMainSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class EducationViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    serializer_class = EducationSerializer
    queryset = Education.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdditionalEducationViewSet(mixins.CreateModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.ListModelMixin,
                                 mixins.DestroyModelMixin,
                                 GenericViewSet):
    serializer_class = AdditionalEducationSerializer
    queryset = AdditionalEducation.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExperienceViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
