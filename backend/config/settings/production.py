from .base import *
import os
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set for production.")
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "your-domain.com").split(",") if host.strip()]

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "project_manager"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "120")),
        "OPTIONS": {
            "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
        },
    }
}

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update(
    {
        "anon": os.getenv("THROTTLE_ANON", "30/minute"),
        "user": os.getenv("THROTTLE_USER", "120/minute"),
    }
)

LOGGING["loggers"]["django"]["level"] = "WARNING"
LOGGING["loggers"]["django.request"]["level"] = "WARNING"
LOGGING["loggers"]["django.db.backends"]["level"] = "ERROR"
LOGGING["loggers"]["app.request"]["level"] = "INFO"

LOGGING["formatters"]["json"] = {
    "()": "core.logging.JsonFormatter",
}
LOGGING["handlers"]["console"]["formatter"] = "json"
LOGGING["handlers"]["app_file"]["formatter"] = "json"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
