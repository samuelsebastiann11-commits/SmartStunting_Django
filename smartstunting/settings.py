
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SECURITY CONFIGURATION
# ==========================================

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY in the Vercel project environment.")
    SECRET_KEY = "django-local-development-key-change-before-production"

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

def _environment_list(name):
    return [value.strip() for value in os.environ.get(name, "").split(",") if value.strip()]


vercel_hosts = [
    os.environ[name]
    for name in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL")
    if os.environ.get(name)
]

ALLOWED_HOSTS = [
    "smart-stunting-django-9uxj.vercel.app",
    "smart-stunting-django-xnup.vercel.app",
    "localhost",
    "127.0.0.1",
] + vercel_hosts + _environment_list("DJANGO_ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = [
    "https://smart-stunting-django-9uxj.vercel.app",
    "https://smart-stunting-django-xnup.vercel.app",
] + [f"https://{host}" for host in vercel_hosts]
CSRF_TRUSTED_ORIGINS += _environment_list("DJANGO_CSRF_TRUSTED_ORIGINS")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Quiz state is small and non-sensitive; signed cookies avoid relying on
# writable local SQLite storage in serverless deployments.
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ==========================================
# URL CONFIGURATION
# ==========================================

ROOT_URLCONF = "smartstunting.urls"

WSGI_APPLICATION = "smartstunting.wsgi.application"
ASGI_APPLICATION = "smartstunting.asgi.application"

# ==========================================
# TEMPLATES
# ==========================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# ==========================================
# DATABASE
# ==========================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ==========================================
# PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = []

# ==========================================
# LANGUAGE AND TIMEZONE
# ==========================================

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"

USE_I18N = True
USE_TZ = True

# ==========================================
# STATIC FILES
# ==========================================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ==========================================
# DEFAULT PRIMARY KEY
# ==========================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
