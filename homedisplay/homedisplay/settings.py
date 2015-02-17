import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '4bqp(_+0m5___@j!@kc-(4feec=wf=!d#9p@el5q)4$#g9qir4'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'control_milight',
    'display',
    'django_extensions',
    'django_statsd',
    'indoor_quality',
    'info_birthdays',
    'info_electricity',
    'info_internet_connection',
    'info_timers',
    'info_weather',
    'repeating_tasks',
    'server_power',
    'ws4redis',
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.StatsdMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_statsd.middleware.StatsdMiddlewareTimer',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'ws4redis.context_processors.default',
)
WSGI_APPLICATION = 'ws4redis.django_runserver.application'
#WSGI_APPLICATION = 'homedisplay.wsgi.application'


ROOT_URLCONF = 'homedisplay.urls'

WEBSOCKET_URL = '/ws/'
WS4REDIS_EXPIRE = 0
WS4REDIS_HEARTBEAT = '--heartbeat--'
WS4REDIS_PREFIX = 'home'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'fi-FI'

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/homecontroller/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

from local_settings import *
