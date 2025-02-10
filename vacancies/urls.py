from rest_framework import routers

from vacancies.views import VacancyViewSet, VacancyResponseViewSet

app_name = 'vacancies'

vacancy_router = routers.DefaultRouter()
vacancy_router.register(r'', VacancyViewSet, basename='vacancy')

vacancy_response_router = routers.DefaultRouter()
vacancy_response_router.register(r'', VacancyResponseViewSet, basename='vacancy_response')
