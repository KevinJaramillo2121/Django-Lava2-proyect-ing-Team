from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Emails a consola en dev (luego configuramos SMTP para notificaciones)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
