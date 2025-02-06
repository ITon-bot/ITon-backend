from rest_framework import routers

from vacancies.views import VacancyViewSet

app_name = 'vacancies'

vacancy_router = routers.DefaultRouter()
vacancy_router.register(r'', VacancyViewSet, basename='vacancy')
