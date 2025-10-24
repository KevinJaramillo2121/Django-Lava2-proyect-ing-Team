from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from vehicles.models import Vehicle

from .forms import BookingCreateForm, BookingUpdateForm
from .models import Booking, BookingStatus
from .utils import overlaps, slot_range


class OwnerBookingMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class BookingListView(OwnerBookingMixin, ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related("vehicle", "service").order_by("-scheduled_at")


class BookingDetailView(OwnerBookingMixin, DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"


class BookingCreateView(LoginRequiredMixin, View):
    template_name = "bookings/booking_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": BookingCreateForm(user=request.user)})

    def post(self, request):
        form = BookingCreateForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        vehicle = form.cleaned_data["vehicle"]
        service = form.cleaned_data["service"]
        scheduled_at = form.cleaned_data["scheduled_at"]
        notes = form.cleaned_data.get("notes", "")

        if vehicle.owner_id != request.user.id:
            messages.error(request, "No puedes reservar con un vehículo que no te pertenece.")
            return render(request, self.template_name, {"form": form})

        with transaction.atomic():
            vehicle = Vehicle.objects.select_for_update().get(pk=vehicle.pk, owner=request.user)
            start, end = slot_range(scheduled_at, service.duration_minutes)
            window_start, window_end = start - timedelta(hours=4), end + timedelta(hours=4)

            candidates = (
                Booking.objects.select_for_update()
                .filter(
                    vehicle=vehicle,
                    status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                    scheduled_at__gte=window_start,
                    scheduled_at__lt=window_end,
                )
                .select_related("service")
            )

            for b in candidates:
                b_start, b_end = slot_range(b.scheduled_at, b.service.duration_minutes)
                if overlaps(start, end, b_start, b_end):
                    messages.error(
                        request, "El vehículo ya tiene una reserva que se solapa en ese horario."
                    )
                    return render(request, self.template_name, {"form": form})

            booking = Booking.objects.create(
                user=request.user,
                vehicle=vehicle,
                service=service,
                scheduled_at=scheduled_at,
                notes=notes,
                status=BookingStatus.PENDING,
            )

        messages.success(request, "Reserva creada correctamente.")
        return redirect("bookings:detail", pk=booking.pk)


class BookingUpdateView(LoginRequiredMixin, View):
    template_name = "bookings/booking_form.html"

    def get_object(self, request, pk):
        return get_object_or_404(Booking, pk=pk, user=request.user)

    def get(self, request, pk):
        booking = self.get_object(request, pk)
        form = BookingUpdateForm(instance=booking, user=request.user)
        return render(request, self.template_name, {"form": form, "booking": booking})

    def post(self, request, pk):
        booking = self.get_object(request, pk)
        form = BookingUpdateForm(request.POST, instance=booking, user=request.user)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "booking": booking})

        if not booking.can_modify():
            messages.error(
                request, "Solo puedes modificar reservas con al menos 24 horas de antelación."
            )
            return render(request, self.template_name, {"form": form, "booking": booking})

        new_vehicle = form.cleaned_data["vehicle"]
        new_service = form.cleaned_data["service"]
        new_scheduled_at = form.cleaned_data["scheduled_at"]

        if new_vehicle.owner_id != request.user.id:
            messages.error(request, "No puedes usar un vehículo que no te pertenece.")
            return render(request, self.template_name, {"form": form, "booking": booking})

        with transaction.atomic():
            new_vehicle = Vehicle.objects.select_for_update().get(
                pk=new_vehicle.pk, owner=request.user
            )
            start, end = slot_range(new_scheduled_at, new_service.duration_minutes)
            window_start, window_end = start - timedelta(hours=4), end + timedelta(hours=4)

            candidates = (
                Booking.objects.select_for_update()
                .filter(
                    vehicle=new_vehicle,
                    status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
                    scheduled_at__gte=window_start,
                    scheduled_at__lt=window_end,
                )
                .exclude(pk=booking.pk)
                .select_related("service")
            )

            for b in candidates:
                b_start, b_end = slot_range(b.scheduled_at, b.service.duration_minutes)
                if overlaps(start, end, b_start, b_end):
                    messages.error(request, "Ese horario ya está ocupado para ese vehículo.")
                    return render(request, self.template_name, {"form": form, "booking": booking})

            booking.vehicle = new_vehicle
            booking.service = new_service
            booking.scheduled_at = new_scheduled_at
            booking.notes = form.cleaned_data.get("notes", booking.notes)
            booking.save(
                update_fields=["vehicle", "service", "scheduled_at", "notes", "updated_at"]
            )

        messages.success(request, "Reserva actualizada correctamente.")
        return redirect("bookings:detail", pk=booking.pk)


class BookingCancelView(LoginRequiredMixin, View):
    template_name = "bookings/booking_confirm_cancel.html"

    def get_object(self, request, pk):
        return get_object_or_404(Booking, pk=pk, user=request.user)

    def get(self, request, pk):
        return render(request, self.template_name, {"booking": self.get_object(request, pk)})

    def post(self, request, pk):
        booking = self.get_object(request, pk)

        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            messages.error(request, "Solo se pueden cancelar reservas pendientes o confirmadas.")
            return redirect("bookings:detail", pk=booking.pk)

        if not booking.can_cancel():
            messages.error(request, "Solo puedes cancelar con al menos 12 horas de antelación.")
            return redirect("bookings:detail", pk=booking.pk)

        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, "Reserva cancelada.")
        return redirect("bookings:list")
