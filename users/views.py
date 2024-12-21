from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet

from .models import User
from .serializers import UserSerializer, ProfileSerializer


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

