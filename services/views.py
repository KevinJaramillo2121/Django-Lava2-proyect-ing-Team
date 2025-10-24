# services/views.py
from django.views.generic import DetailView, ListView

from .models import Service


class PublicServiceListView(ListView):
    """
    Lista pública de servicios activos.
    Cualquiera puede acceder (sin login).
    """

    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"
    paginate_by = 12  # ajusta según UI

    def get_queryset(self):
        return Service.objects.filter(is_active=True).order_by("name")


class PublicServiceDetailView(DetailView):
    """
    Detalle público de un servicio (opcional, útil para SEO/UX).
    """

    model = Service
    template_name = "services/service_detail.html"
    context_object_name = "service"
