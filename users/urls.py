from rest_framework import routers

from users.views import UserViewSet, EducationViewSet, AdditionalEducationViewSet, ExperienceViewSet

app_name = 'users'

user_router = routers.DefaultRouter()
user_router.register(r'', UserViewSet, basename='users')

education_router = routers.DefaultRouter()
education_router.register(r'', EducationViewSet, basename='educations')

additional_education_router = routers.DefaultRouter()
additional_education_router.register(r'', AdditionalEducationViewSet, basename='additional-educations')

experience_router = routers.DefaultRouter()
experience_router.register(r'', ExperienceViewSet, basename='experiences')

user_book_router = routers.DefaultRouter()

