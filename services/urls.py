# services/urls.py
from django.urls import path

from .views import PublicServiceDetailView, PublicServiceListView

app_name = "services"

urlpatterns = [
    path("", PublicServiceListView.as_view(), name="public_list"),
    path("<int:pk>/", PublicServiceDetailView.as_view(), name="public_detail"),
]
