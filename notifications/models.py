from django.db import models
from django.utils import timezone

from config.models import TimeStampedModel
from users.models import User


class NotificationChannel(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"
    PUSH = "PUSH", "Push"


class NotificationStatus(models.TextChoices):
    QUEUED = "QUEUED", "En cola"
    SENT = "SENT", "Enviada"
    FAILED = "FAILED", "Fallida"


class Notification(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    subject = models.CharField(max_length=120)
    message = models.TextField()
    status = models.CharField(
        max_length=10, choices=NotificationStatus.choices, default=NotificationStatus.QUEUED
    )
    sent_at = models.DateTimeField(blank=True, null=True)
    meta = models.JSONField(blank=True, null=True)  # ids de proveedor, payload, etc.

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["channel"]),
        ]

    def mark_sent(self):
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])

    def __str__(self):
        return f"Notification #{self.id} to {self.user.email} [{self.channel}] - {self.status}"
