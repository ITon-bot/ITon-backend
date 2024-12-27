from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet

from .models import User, Education, AdditionalEducation, Experience
from .serializers import UserSerializer, ProfileSerializer, EducationSerializer, AdditionalEducationSerializer, \
    ExperienceSerializer


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=['GET'], url_path='profile')
    def profile(self, request):
        serializer = ProfileSerializer(request.telegram_user)
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
        serializer.save(user=self.request.telegram_user)


class AdditionalEducationViewSet(mixins.CreateModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.ListModelMixin,
                                 mixins.DestroyModelMixin,
                                 GenericViewSet):
    serializer_class = AdditionalEducationSerializer
    queryset = AdditionalEducation.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.telegram_user)


class ExperienceViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.telegram_user)
