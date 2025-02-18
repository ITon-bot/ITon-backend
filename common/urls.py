from rest_framework import routers

from common.views import SpecializationViewSet, SkillViewSet, ReportViewSet, ReportAdminViewSet

app_name = 'common'

specialization_router = routers.DefaultRouter()
specialization_router.register(r'', SpecializationViewSet, basename='specialization')

skill_router = routers.DefaultRouter()
skill_router.register(r'', SkillViewSet, basename='skill')

report_router = routers.DefaultRouter()
report_router.register(r'', ReportViewSet, basename='report')

report_admin_router = routers.DefaultRouter()
report_admin_router.register(r'', ReportAdminViewSet, basename='report_admin')