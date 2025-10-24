"""
Settings base para LAVA2.

Reglas clave:
- MVT estricto y modularidad por entorno
- Seguridad: Argon2, CSRF/XSS, etc.
- PostgreSQL con variables de entorno (python-decouple)
"""

import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Seguridad básica (SECRET_KEY se inyecta por .env)
SECRET_KEY = config("SECRET_KEY", default="insecure-key-change-me")

DEBUG = False  # Se activa en development.py

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=lambda v: [s.strip() for s in v.split(",")]
)

# Apps de Django
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Terceros (alineado con tus reglas)
THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    # "allauth", "allauth.account",  # (lo integraremos cuando armemos el registro/verificación)
]

# Apps locales (iremos agregando)
LOCAL_APPS = [
    "users.apps.UsersConfig",
    "vehicles",
    "services",
    "bookings",
    "payments",
    "notifications",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # carpeta global opcional
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Base de datos PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="lava2_dev"),
        "USER": config("DB_USER", default="lava2_user"),
        "PASSWORD": config("DB_PASSWORD", default="lava2_password"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        # DB_NAME=lava2_dev
        # DB_USER=lava2_user
        # DB_PASSWORD=lava2_password
        # DB_HOST=localhost
        # DB_PORT=5432
    }
}

# Hash de contraseñas: Argon2id (según tus reglas)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    # Backups por compatibilidad si hiciera falta:
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Internacionalización y TZ
LANGUAGE_CODE = config("LANGUAGE_CODE", default="es")
TIME_ZONE = config("TIME_ZONE", default="America/Bogota")
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# Media (si subimos fotos de perfil, etc.)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# DRF (de momento básico; afinaremos al crear APIs)
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# CORS (abrimos en dev; en prod, dominios específicos)
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default="true").lower() == "true"

# Sesiones y seguridad adicional (cabeceras se endurecen en producción)
CSRF_COOKIE_HTTPONLY = True  # dificulta CSRF via JS
SESSION_COOKIE_HTTPONLY = True


AUTH_USER_MODEL = "users.User"


# Redirecciones de autenticación
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "users:profile"  # a dónde ir tras login
LOGOUT_REDIRECT_URL = "users:login"  # a dónde ir tras logout

# Mensajes (framework de mensajes, ya activado por defecto)
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}
