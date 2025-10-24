# users/models.py
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.models import TimeStampedModel

from .managers import UserManager


class User(AbstractUser, TimeStampedModel):
    """
    Usuario personalizado que usa EMAIL como identificador.
    - Se elimina 'username' y se usa `email` como USERNAME_FIELD.
    - Alineado con seguridad y buenas prácticas (Django + Argon2).
    """

    username = None  # deshabilitamos el username de AbstractUser
    email = models.EmailField(_("email address"), unique=True, db_index=True)

    # Flags estándar de Django ya existen en AbstractUser:
    # is_active, is_staff, is_superuser, last_login, etc.

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no pedimos nada extra para createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-created_at"]


phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-]{7,20}$", message="Número telefónico inválido."
)


class Profile(TimeStampedModel):
    """
    Perfil extendido para datos no críticos de autenticación:
    - nombre completo, teléfono, zona horaria, avatar y preferencias.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, validators=[phone_validator], blank=True)
    timezone = models.CharField(max_length=50, default="America/Bogota")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Preferencias de notificación
    wants_email = models.BooleanField(default=True)
    wants_sms = models.BooleanField(default=False)
    wants_push = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.email}"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
