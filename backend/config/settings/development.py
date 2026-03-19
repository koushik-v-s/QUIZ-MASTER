"""
Development settings — local dev with SQLite and DEBUG=True.
"""
from .base import *  # noqa: F401,F403

SECRET_KEY = 'django-insecure-dev-key-change-in-production-!@#$%^&*()'

DEBUG = True
ALLOWED_HOSTS = ['*']

# ─── Database (SQLite for local, override with DATABASE_URL for Supabase) ─
import os

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import environ
    env = environ.Env()
    DATABASES = {
        'default': env.db_url('DATABASE_URL', default=DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── CORS — allow all in dev ─────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ─── Add browsable API renderer in dev ────────────────────────────────
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# ─── Email — console backend for dev ─────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ─── Logging ──────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ─── Disable Redis for local dev if it times out ───────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'quiz-dev',
    }
}
CELERY_TASK_ALWAYS_EAGER = True
