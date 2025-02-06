from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from common.models import Specialization, Skill
from common.serializers import SpecializationSerializer, SkillSerializer


class SpecializationViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()


class SkillViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()
