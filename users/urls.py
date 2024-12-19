from django.urls import path, include
from rest_framework import routers

from users.views import UserViewSet

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='specification')

urlpatterns = [
    path('', include(router.urls)),
]
