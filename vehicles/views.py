# vehicles/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

# Importamos Booking y estados para verificar reservas activas
from bookings.models import Booking, BookingStatus

from .forms import VehicleForm
from .models import Vehicle


class OwnerQuerysetMixin(LoginRequiredMixin):
    """
    Mixin para asegurar que todas las consultas se limiten al propietario actual.
    - Evita accesos a objetos de otros usuarios.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class VehicleListView(OwnerQuerysetMixin, ListView):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"
    paginate_by = 10  # opcional


class VehicleDetailView(OwnerQuerysetMixin, DetailView):
    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"
    context_object_name = "vehicle"


class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:list")

    def form_valid(self, form):
        # Asignar el propietario al guardar
        vehicle = form.save(commit=False)
        vehicle.owner = self.request.user
        vehicle.save()
        messages.success(self.request, "Vehículo creado correctamente.")
        return super().form_valid(form)


class VehicleUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"
    success_url = reverse_lazy("vehicles:list")

    def form_valid(self, form):
        messages.success(self.request, "Vehículo actualizado.")
        return super().form_valid(form)


class VehicleDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Vehicle
    template_name = "vehicles/vehicle_confirm_delete.html"
    success_url = reverse_lazy("vehicles:list")

    def post(self, request, *args, **kwargs):
        """
        Antes de eliminar, verificamos reservas activas/futuras:
        - status CONFIRMED o PENDING con fecha >= ahora → BLOQUEAR
        - COMPLETED/CANCELLED o pasadas → permitir
        """
        self.object = self.get_object()

        now = timezone.now()
        has_active = Booking.objects.filter(
            vehicle=self.object,
            scheduled_at__gte=now,
            status__in=[BookingStatus.CONFIRMED, BookingStatus.PENDING],
        ).exists()

        if has_active:
            messages.error(
                request, "No puedes eliminar este vehículo porque tiene reservas activas o futuras."
            )
            return self.get(request, *args, **kwargs)  # recarga la página de confirmación

        messages.success(request, "Vehículo eliminado.")
        return super().post(request, *args, **kwargs)
