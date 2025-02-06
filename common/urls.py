from rest_framework import routers

from common.views import SpecializationViewSet, SkillViewSet

app_name = 'common'

specialization_router = routers.DefaultRouter()
specialization_router.register(r'', SpecializationViewSet, basename='specialization')

skill_router = routers.DefaultRouter()
skill_router.register(r'', SkillViewSet, basename='skill')
