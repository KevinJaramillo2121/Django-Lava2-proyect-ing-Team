# config/models.py
from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo abstracto con campos de auditoría estándar.
    - created_at: fecha de creación (auto)
    - updated_at: fecha de última actualización (auto)
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True
