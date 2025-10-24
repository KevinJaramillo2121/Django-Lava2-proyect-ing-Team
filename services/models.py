from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from config.models import TimeStampedModel


class Service(TimeStampedModel):
    """
    Catálogo de servicios de lavado.
    """

    name = models.CharField(max_length=80, unique=True, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(5)])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price})"

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["name"]
        indexes = [models.Index(fields=["is_active"])]
