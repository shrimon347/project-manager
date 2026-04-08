from .base import *
import os

DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-local-development-key")

ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]

DATABASES["default"]["CONN_MAX_AGE"] = int(os.getenv("DB_CONN_MAX_AGE", "0"))

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update(
    {
        "anon": os.getenv("THROTTLE_ANON", "300/minute"),
        "user": os.getenv("THROTTLE_USER", "1000/minute"),
    }
)

LOGGING["loggers"]["django"]["level"] = "INFO"
LOGGING["loggers"]["django.db.backends"]["level"] = "INFO"
LOGGING["loggers"]["django.utils.autoreload"] = {
    "handlers": ["console", "app_file"],
    "level": "WARNING",
    "propagate": False,
}

LOGGING["formatters"]["json"] = {
    "()": "core.logging.JsonFormatter",
}
LOGGING["handlers"]["console"]["formatter"] = "json"
LOGGING["handlers"]["app_file"]["formatter"] = "json"
