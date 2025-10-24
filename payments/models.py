from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from bookings.models import Booking
from config.models import TimeStampedModel


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    PAID = "PAID", "Pagado"
    FAILED = "FAILED", "Fallido"
    REFUNDED = "REFUNDED", "Reembolsado"


class Payment(TimeStampedModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    currency = models.CharField(max_length=10, default="USD")
    provider = models.CharField(max_length=30, default="stripe")
    status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    transaction_id = models.CharField(max_length=120, blank=True, db_index=True)
    error_message = models.TextField(blank=True)

    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["transaction_id"]),
        ]

    def __str__(self):
        return f"Pago #{self.id} - Booking #{self.booking_id} - {self.status}"
