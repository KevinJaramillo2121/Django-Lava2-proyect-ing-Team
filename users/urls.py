from django.http import JsonResponse
from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    ProfileUpdateView,
    ProfileView,
    RegisterStep1View,
    RegisterStep2View,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterStep1View.as_view(), name="register_step1"),
    path("register/profile/", RegisterStep2View.as_view(), name="register_step2"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
