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

from common.urls import specialization_router, skill_router, report_router, report_admin_router, schema_view
from common.views import SetLanguageView
from users.urls import user_router, education_router, additional_education_router, experience_router, user_book_router
from vacancies.urls import vacancy_router, vacancy_response_router, vacancy_admin_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include(user_router.urls), name='users'),
    path('api/educations/', include(education_router.urls), name='educations'),
    path('api/additional-educations/', include(additional_education_router.urls), name='additional-educations'),
    path('api/user-books/', include(user_book_router.urls), name='user-books'),
    path('api/experiences/', include(experience_router.urls), name='experiences'),
    path('api/vacancies/', include(vacancy_router.urls), name='vacancies'),
    path('api/vacancy-responses/', include(vacancy_response_router.urls), name='vacancy-responses'),
    path('api/specializations/', include(specialization_router.urls), name='specializations'),
    path('api/skills/', include(skill_router.urls), name='skills'),
    path('api/reports/', include(report_router.urls), name='reports'),
    # admin
    path('api/vacancies-admin/', include(vacancy_admin_router.urls), name='vacancies-admin'),
    path('api/reports-admin/', include(report_admin_router.urls), name='reports-admin'),

    # loc
    path('api/set-language/', SetLanguageView.as_view(), name='set-language'),

    # swagger
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
