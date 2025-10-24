from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"status": "ok", "app": "LAVA2"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("users/", include("users.urls")),
    path("vehicles/", include("vehicles.urls")),
    path("services/", include("services.urls")),
]
