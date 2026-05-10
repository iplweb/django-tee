"""Django settings for the django-tee test suite.

Spins up a Postgres testcontainer at import time (so JSONField is
exercised against a real backend, matching the production target),
and registers django_tee under its actual import path.
"""

from __future__ import annotations

import atexit

from testcontainers.postgres import PostgresContainer

_postgres = PostgresContainer("postgres:16-alpine")
_postgres.start()
atexit.register(_postgres.stop)

SECRET_KEY = "django-tee-test-key-not-secret"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "django_tee",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _postgres.dbname,
        "USER": _postgres.username,
        "PASSWORD": _postgres.password,
        "HOST": _postgres.get_container_host_ip(),
        "PORT": _postgres.get_exposed_port(5432),
    }
}

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    }
]

STATIC_URL = "/static/"
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
