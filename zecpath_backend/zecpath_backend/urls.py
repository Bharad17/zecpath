"""
URL configuration for zecpath_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path
from core.views import UserTestAPI, JobListAPI, SignupAPI, LoginAPI, LogoutAPI, ApplicationAPI, AdminControlAPI, Trigger500API
from core.profile_views import CandidateProfileAPI, EmployerProfileAPI
from rest_framework_simplejwt.views import TokenRefreshView
from core.profile_views import (
    CandidateProfileAPI,
    EmployerProfileAPI,
    CandidateResumeAPI,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user-test/', UserTestAPI.as_view()),
    path('api/jobs/', JobListAPI.as_view()),
    path('api/signup/', SignupAPI.as_view()),
    path('api/login/', LoginAPI.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/logout/', LogoutAPI.as_view()),
    path('api/applications/', ApplicationAPI.as_view()),
    path('api/admin-control/', AdminControlAPI.as_view()),
    path('api/candidate/profile/', CandidateProfileAPI.as_view()),
    path('api/employer/profile/', EmployerProfileAPI.as_view()),
    path("api/candidate/resume/", CandidateResumeAPI.as_view()),
    path("api/test-500/", Trigger500API.as_view()),
]