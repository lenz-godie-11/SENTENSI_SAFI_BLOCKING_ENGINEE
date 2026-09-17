# ruff: noqa: N999, I001

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from the project root.
load_dotenv(BASE_DIR / ".env")


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "unsafe-development-key",
)

DEBUG = os.getenv(
    "DJANGO_DEBUG",
    "False",
).lower() == "true"


ALLOWED_HOSTS = [
    Host.strip()
    for Host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if Host.strip()
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "graphene_django",

    "BlockingEngine.Blocking.Apps.BlockingConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "BlockingEngine.Config.Urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "BlockingEngine.Config.Wsgi.application"

ASGI_APPLICATION = "BlockingEngine.Config.Asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Dar_es_Salaam"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Defines the GraphQL schema exposed through Graphene-Django.
GRAPHENE = {
    "SCHEMA": "BlockingEngine.GraphQL.Schema.Schema",
}


# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------

# Prevent browsers from embedding application pages in frames.
X_FRAME_OPTIONS = "DENY"

# Prevent browsers from MIME-sniffing responses.
SECURE_CONTENT_TYPE_NOSNIFF = True

# Restrict the amount of referrer information sent by the browser.
SECURE_REFERRER_POLICY = "same-origin"


# ---------------------------------------------------------------------------
# Application logging
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "BlockingEngine": {
            "format": (
                "{asctime} | {levelname} | "
                "{name} | {message}"
            ),
            "style": "{",
        },
    },

    "handlers": {
        "Console": {
            "class": "logging.StreamHandler",
            "formatter": "BlockingEngine",
        },
    },

    "loggers": {
        "BlockingEngine": {
            "handlers": ["Console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}