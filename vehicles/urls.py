# vehicles/urls.py
from django.urls import path

from .views import (
    VehicleCreateView,
    VehicleDeleteView,
    VehicleDetailView,
    VehicleListView,
    VehicleUpdateView,
)

app_name = "vehicles"

urlpatterns = [
    path("", VehicleListView.as_view(), name="list"),
    path("create/", VehicleCreateView.as_view(), name="create"),
    path("<int:pk>/", VehicleDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", VehicleUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", VehicleDeleteView.as_view(), name="delete"),
]
