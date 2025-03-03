from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions

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

schema_view = get_schema_view(
    openapi.Info(
        title="ITon API",
        default_version='v1',
        description="This is documentation for ITon",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
