"""
Base settings for Quiz App project.
Contains all shared configuration across environments.
"""
import importlib
import os
import logging

# Bypass local Windows proxy hangs for Google API
os.environ['NO_PROXY'] = '*'
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

from pathlib import Path
from datetime import timedelta
import environ

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps
    'apps.users',
    'apps.quizzes',
    'apps.attempts',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Django REST Framework ────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# ─── SimpleJWT ────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
}

# ─── CORS ─────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ─── Redis URL ────────────────────────────────────────────────────────
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# ─── Celery ───────────────────────────────────────────────────────────
# Try to use Redis, fallback to run tasks synchronously if unavailable
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 120  # 2 minutes max per task

# ─── Cache Configuration ─────────────────────────────────────────────
# Attempt Redis first, gracefully fallback to LocMemCache if unavailable
def _test_redis_connection(redis_url):
    """Test if Redis is reachable."""
    try:
        import redis as redis_lib
        client = redis_lib.from_url(redis_url, socket_connect_timeout=3, socket_timeout=3)
        client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis connection failed ({redis_url}): {e}. Falling back to local memory cache.")
        return False


REDIS_AVAILABLE = _test_redis_connection(REDIS_URL)

if REDIS_AVAILABLE:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'RETRY_ON_TIMEOUT': True,
            },
            'KEY_PREFIX': 'quiz_app',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }
    logger.info("✓ Using Redis cache backend.")
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'quiz-app-local',
        }
    }
    # If Redis is unavailable, run Celery tasks synchronously
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = False
    logger.info("⚠ Using local memory cache (Redis unavailable). Celery tasks run synchronously without propagating exceptions.")

# ─── drf-spectacular (OpenAPI / Swagger) ──────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'AI-Powered Quiz API',
    'DESCRIPTION': 'A production-grade AI-powered quiz application API with Gemini integration.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'Authentication endpoints'},
        {'name': 'Quizzes', 'description': 'Quiz CRUD and AI generation'},
        {'name': 'Attempts', 'description': 'Quiz attempt tracking and scoring'},
        {'name': 'Analytics', 'description': 'Performance analytics and leaderboard'},
        {'name': 'Admin', 'description': 'Admin management endpoints'},
    ],
}

# ─── Groq AI (Labeled internally/externally as Grok) ──────────────────
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_MODEL = 'llama-3.3-70b-versatile'
AI_GENERATION_RATE_LIMIT = 30  # max generations per user per day
