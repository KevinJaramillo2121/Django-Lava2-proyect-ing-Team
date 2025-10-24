from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from config.models import TimeStampedModel
from services.models import Service
from users.models import User
from vehicles.models import Vehicle


class BookingStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    CONFIRMED = "CONFIRMED", "Confirmada"
    CANCELLED = "CANCELLED", "Cancelada"
    COMPLETED = "COMPLETED", "Completada"


class Booking(TimeStampedModel):
    """
    Reserva de servicio para un vehículo en una fecha/hora.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")
    scheduled_at = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=12, choices=BookingStatus.choices, default=BookingStatus.PENDING
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-scheduled_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle", "scheduled_at"], name="unique_vehicle_timeslot"
            )
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user", "scheduled_at"]),
        ]

    def __str__(self):
        return f"Reserva #{self.id} - {self.vehicle.plate} - {self.scheduled_at:%Y-%m-%d %H:%M}"

    def clean(self):
        """
        Validaciones de negocio:
        - No reservar en el pasado.
        - Evitar solapamientos básicos para el mismo vehículo considerando la duración del servicio.
        """
        if self.scheduled_at < timezone.now():
            raise ValidationError("No puedes reservar en el pasado.")

        # Verificación simple de solapamiento por vehículo (mismo timeslot exacto
        # lo cubre la UniqueConstraint; aquí miramos rango por duración).
        duration = timezone.timedelta(minutes=self.service.duration_minutes or 0)
        start = self.scheduled_at
        end = start + duration

        overlapping = Booking.objects.filter(
            vehicle=self.vehicle,
            scheduled_at__lt=end,
            # Suponiendo que el otro booking dura su propio `service.duration_minutes`:
        ).exclude(pk=self.pk)

        # Esta comprobación es básica; en Paso 6 haremos chequeo atómico.
        if overlapping.exists():
            raise ValidationError("El vehículo ya tiene una reserva que se solapa con ese horario.")

    def can_modify(self) -> bool:
        """Regla: se puede modificar con >= 24h de antelación."""
        return (self.scheduled_at - timezone.now()) >= timezone.timedelta(hours=24)

    def can_cancel(self) -> bool:
        """Regla: se puede cancelar con >= 12h de antelación."""
        return (self.scheduled_at - timezone.now()) >= timezone.timedelta(hours=12)
