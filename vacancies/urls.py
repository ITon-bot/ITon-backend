from rest_framework import routers

from vacancies.views import VacancyViewSet, VacancyResponseViewSet, VacancyAdminViewSet

app_name = 'vacancies'

vacancy_router = routers.DefaultRouter()
vacancy_router.register(r'', VacancyViewSet, basename='vacancy')

vacancy_response_router = routers.DefaultRouter()
vacancy_response_router.register(r'', VacancyResponseViewSet, basename='vacancy_response')

vacancy_admin_router = routers.DefaultRouter()
vacancy_admin_router.register(r'', VacancyAdminViewSet, basename='vacancy_admin')
