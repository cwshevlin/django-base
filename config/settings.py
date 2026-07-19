"""
Django settings for this project.

Environment variables:
    DEBUG                "1" enables debug mode (default "0").
    SECRET_KEY           or SECRET_KEY_FILE (docker secret path).
    POSTGRES_DB / POSTGRES_USER / POSTGRES_HOST / POSTGRES_PORT
    POSTGRES_PASSWORD    or POSTGRES_PASSWORD_FILE.
    RESEND_API_KEY       or RESEND_API_KEY_FILE; used when DEBUG is off.
    DJANGO_LOG_LEVEL     log level for the console handler (default "INFO").

In DEBUG mode the secrets fall back to insecure development defaults; with
DEBUG off, missing secrets raise ImproperlyConfigured at startup.
"""

import os
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_secret(name, default=None):
    """Read a secret from ``<NAME>_FILE`` (docker secret) if present,
    otherwise fall back to the plain ``<NAME>`` environment variable."""
    file_path = os.environ.get(f"{name}_FILE")
    if file_path:
        with open(file_path, encoding="utf-8") as handle:
            return handle.read().strip()
    value = os.environ.get(name, default)
    if value is None:
        raise ImproperlyConfigured(
            f"Set the {name} or {name}_FILE environment variable."
        )
    return value


DEBUG = os.environ.get("DEBUG", "0") == "1"

SECRET_KEY = _read_secret(
    "SECRET_KEY", default="django-insecure-dev-only" if DEBUG else None
)

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]  # TODO: add your production hostname

# HTTPS is terminated at the Cloudflare edge; only trust our public origin.
CSRF_TRUSTED_ORIGINS = []  # e.g. ["https://example.com"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "auditlog",
    "rest_framework",
    "drf_spectacular",
    "anymail",
    "authn",
    "config",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "config.urls"

# Security. The app serves HTTPS terminated upstream (Cloudflare tunnel), so
# trust the forwarded protocol header and lock everything down outside DEBUG.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "config/templates",
            "authn/templates",
        ],
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


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "pg"),
        "USER": os.environ.get("POSTGRES_USER", "user"),
        "PASSWORD": _read_secret(
            "POSTGRES_PASSWORD", default="postgres" if DEBUG else None
        ),
        "HOST": os.environ.get("POSTGRES_HOST", "database"),
        "PORT": int(os.environ.get("POSTGRES_PORT", "5432")),
    }
}

AUTH_USER_MODEL = "authn.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Serve collected static files directly from Django via WhiteNoise, since the
# app runs behind the Cloudflare tunnel with no separate static file server.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

LOGIN_REDIRECT_URL = "/"

# Email: Resend (via Anymail) in production, console output in development.
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
ANYMAIL = {
    "RESEND_API_KEY": _read_secret("RESEND_API_KEY", default="" if DEBUG else None),
}
DEFAULT_FROM_EMAIL = (
    "noreply@example.com"  # TODO: a sender on your verified Resend domain
)

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.v1.pagination.StandardPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Django Base API",
    "DESCRIPTION": "API for this project's clients.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
