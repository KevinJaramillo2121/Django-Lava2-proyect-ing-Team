from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from config.models import TimeStampedModel
from users.models import User

plate_validator = RegexValidator(
    regex=r"^[A-Z0-9\-]{5,10}$",
    message="Placa inválida: usa mayúsculas, números y guión (5-10 chars).",
)

CURRENT_YEAR = timezone.now().year


class Vehicle(TimeStampedModel):
    """
    Vehículo del usuario.
    - Placa única (a nivel global; si prefieres por usuario, cambia unique→UniqueConstraint).
    - Validaciones básicas para año/placa.
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    plate = models.CharField(
        max_length=10, unique=True, validators=[plate_validator], db_index=True
    )
    make = models.CharField("Marca", max_length=50)
    model = models.CharField("Modelo", max_length=50)
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1980), MaxValueValidator(CURRENT_YEAR + 1)]
    )
    color = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Normalizamos placas a MAYÚSCULAS
        if self.plate:
            self.plate = self.plate.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plate} - {self.make} {self.model}"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["plate"]
        indexes = [
            models.Index(fields=["plate"]),
            models.Index(fields=["owner"]),
        ]
