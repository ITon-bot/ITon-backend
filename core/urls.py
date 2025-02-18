"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from common.urls import specialization_router, skill_router, report_router, report_admin_router
from users.urls import user_router, education_router, additional_education_router, experience_router
from vacancies.urls import vacancy_router, vacancy_response_router, vacancy_admin_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include(user_router.urls)),
    path('api/educations/', include(education_router.urls)),
    path('api/additional-educations/', include(additional_education_router.urls)),
    path('api/experiences/', include(experience_router.urls)),
    path('api/vacancies/', include(vacancy_router.urls)),
    path('api/vacancy-responses/', include(vacancy_response_router.urls)),
    path('api/specializations/', include(specialization_router.urls)),
    path('api/skills/', include(skill_router.urls)),
    path('api/reports/', include(report_router.urls)),

    # admin
    path('api/vacancies-admin/', include(vacancy_admin_router.urls)),
    path('api/reports-admin/', include(report_admin_router.urls))
]
