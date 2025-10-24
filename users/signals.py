# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance: User, created: bool, **kwargs):
    # Crea el perfil cuando se crea el usuario; si ya existe, lo asegura.
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
