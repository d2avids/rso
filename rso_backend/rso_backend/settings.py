import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

load_dotenv()

MIN_FOUNDING_DATE = 1000
MAX_FOUNDING_DATE = 9999
MASTER_METHODIST_POSITION_NAME = 'Мастер (методист)'
COMMISSIONER_POSITION_NAME = 'Комиссар'
DEFAULT_POSITION_NAME = 'Боец'
DATE_JUNIOR_SQUAD = (2023, 1, 25)

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv('SECRET_KEY', default='key')

DEBUG = os.getenv('DEBUG', default=False) == 'True'

ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost,0.0.0.0'
).split(',')

DEFAULT_SITE_URL = os.getenv('DEFAULT_SITE_URL', default='127.0.0.1:8000')

DATABASE = os.getenv('DATABASE', default='sqlite')

# RUN TYPES:

# DOCKER - для запуска проекта через docker compose.
# Коннект к Redis происходит по имени сервиса - redis.

# LOCAL - для локального запуска проекта.
# Коннект к Redis происходит по локальной сети.
RUN_TYPE = os.getenv('RUN_TYPE', default='LOCAL')

AUTH_USER_MODEL = 'users.RSOUser'

# EMAIL BACKEND
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465
EMAIL_USE_SSL = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

EMAIL_SERVER = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'djoser',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
    'import_export',
]

INSTALLED_APPS += [
    'api.apps.ApiConfig',
    'users.apps.UsersConfig',
    'headquarters.apps.HeadquartersConfig',
    'events.apps.EventsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rso_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['../templates'],
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

WSGI_APPLICATION = 'rso_backend.wsgi.application'

if DATABASE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / '_db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'django'),
            'USER': os.getenv('POSTGRES_USER', 'django'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'django'),
            'HOST': os.getenv('DB_HOST', 'db'),
            'PORT': os.getenv('DB_PORT', 5432)
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'main_formatter': {
            'format': '{asctime} - {name} - {levelname} - {module} - {pathname} - {message}',
            'style': '{',
        },
        'json_formatter': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'json_ensure_ascii': False
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'tasks': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/tasks_logs.log',
            'maxBytes': 1024 * 1024 * 1024,
            'backupCount': 15,
            'formatter': 'json_formatter',
        },
        'request': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': 'logs/requests_logs.log',
            'encoding': 'UTF-8',
        },
        'server_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/server_commands_logs.log',
            'maxBytes': 1024 * 1024 * 1024,
            'backupCount': 15,
            'formatter': 'json_formatter',
        },
        'db': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': 'logs/db_queries_logs.log',
            'encoding': 'UTF-8',
        },
        'security': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': 'logs/security_logs.log',
            'encoding': 'UTF-8',
        },
        'security_csrf': {
            'class': 'logging.FileHandler',
            'formatter': 'json_formatter',
            'filename': 'logs/security_csrf_logs.log',
            'encoding': 'UTF-8',
        }
    },

    'loggers': {
        'tasks': {
            'handlers': ['console', 'tasks'],
            'level': 'DEBUG',
        },
        'django.request': {
            'level': 'INFO',
            'handlers': ['console', 'request']
        },
        'django.server': {
            'level': 'INFO',
            'handlers': ['console', 'server_handler']
        },
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console', 'db']
        },
        'django.security.*': {
            'level': 'INFO',
            'handlers': ['console', 'security']
        },
        'django.security.csrf': {
            'level': 'INFO',
            'handlers': ['console', 'security_csrf']
        }
    }
}


# REDIS CACHE
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
        'OPTIONS': {
            'db': '1',
            'parser_class': 'redis.connection.PythonParser',
            'pool_class': 'redis.BlockingConnectionPool',
        }
    },
}

# CELERY-REDIS CONFIG
REDIS_HOST = '127.0.0.1' if RUN_TYPE != 'DOCKER' else 'redis'
REDIS_PORT = '6379'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_BROKEN_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'reset_membership_fee_task': {
        'task': 'users.tasks.reset_membership_fee',
        'schedule': crontab(
            hour=0,
            minute=0,
            day_of_month=1,
            month_of_year=10,
        )
    },
}

if DEBUG:
    CELERY_BEAT_SCHEDULE['debug_periodic_task'] = {
        'task': 'users.tasks.debug_periodic_task',
        'schedule': timedelta(seconds=90),
    }

# FOR LINUX:
# celery -A rso_backend worker --loglevel=info
# celery -A rso_backend beat -l info

# FOR WINDOWS:
# celery -A rso_backend worker --loglevel=info -P eventlet
# celery -A rso_backend beat -l info -P eventlet

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:80',
    'http://localhost',
    'https://d2avids.sytes.net',
    'https://rso.sprint.1t.ru',
    'https://лк.трудкрут.рф',
    'http://213.139.208.147',
    'https://213.139.208.147',
    'http://xn--j1ab.xn--d1amqcgedd.xn--p1ai',
    'https://xn--j1ab.xn--d1amqcgedd.xn--p1ai',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8080',
    'http://localhost:80',
    'http://127.0.0.1:8080',
    'http://localhost'
    'https://127.0.0.1',
    'https://rso.sprint.1t.ru',
    'https://лк.трудкрут.рф',
    'http://xn--j1ab.xn--d1amqcgedd.xn--p1ai',
    'https://xn--j1ab.xn--d1amqcgedd.xn--p1ai',
    'http://213.139.208.147',
    'https://213.139.208.147',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

DJOSER = {
    'LOGIN_FIELD': 'username',
    'USERNAME_FIELD': 'username',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SEND_ACTIVATION_EMAIL': False,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': False,
    'PASSWORD_RESET_CONFIRM_RETYPE': False,
    'HIDE_USERS': False,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'SERIALIZERS': {
        'user': 'api.serializers.DjoserUserSerializer',
        'user_create_password_retype': 'api.serializers.UserCreateSerializer',
    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.IsAuthenticated'],
        'user': ['rest_framework.permissions.IsAuthenticated'],
    }
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
