import os
import platform
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '4bqp(_+0m5___@j!@kc-(4feec=wf=!d#9p@el5q)4$#g9qir4'

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'control_display',
    'control_milight',
    'control_music',
    'control_printer',
    'display',
    'django_extensions',
    'django_statsd',
    'djcelery',
    'info_air_quality',
    'info_birthdays',
    'info_electricity',
    'info_ext_pages',
    'info_internet_connection',
    'info_timers',
    'info_torrents',
    'info_transportation',
    'info_weather',
    'info_notifications',
    'repeating_tasks',
    'server_power',
    'ws4redis',
    'node_data_receiver',
    'control_kettle',
)

COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', '~/node_modules/.bin/coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-sass', 'sassc {infile} {outfile}'),
    ('text/x-scss', 'sassc {infile} {outfile}'),
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.StatsdMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'display.middleware.authentication.SpecialAuthenticationMiddleware',
    'django_statsd.middleware.StatsdMiddlewareTimer',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
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

# Celery settings
BROKER_URL = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/homecontroller/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'django_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose'
        },
        'homedisplay_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/homecontroller.log',
            'formatter': 'verbose'
        },
        'jeenode_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/jeenode.log',
            'formatter': 'verbose'
        },
        'statsd_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/statsd.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'homecontroller.control_milight.management.commands.listen_jeenode': {
            'handlers': ['jeenode_file'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['django_file'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'homedisplay': {
            'handlers': ['homedisplay_file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'statsd': {
            'handlers': ['statsd_file'],
            'propagate': False,
            'level': 'DEBUG',
        },
        '': {
            'handlers': ['homedisplay_file'],
            'propagate': True,
            'level': 'DEBUG',
        }
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                'ws4redis.context_processors.default',
            ],
        },
    },
]

import djcelery
djcelery.setup_loader()


SESSION_COOKIE_AGE = 360 * 24 * 60 * 60

if platform.system() == "Darwin":
    # Development environment
    print "Warning: using development environment settings"
    RUN_XSET = False
else:
    RUN_XSET = True

from local_settings import *
