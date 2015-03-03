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
    'control_display',
    'control_milight',
    'control_music',
    'control_printer',
    'display',
    'django_extensions',
    'django_statsd',
    'djcelery',
    'indoor_quality',
    'info_birthdays',
    'info_electricity',
    'info_internet_connection',
    'info_timers',
    'info_torrents',
    'info_transportation',
    'info_weather',
    'pipeline',
    'repeating_tasks',
    'server_power',
    'ws4redis',
)

PIPELINE_BASE_CSS = [
    "sass/_bootstrap.scss",
    "jquery-ui/jquery-ui.css",
    "css/font-awesome.css",
    "css/nv.d3.css",
    "sass/shared.scss",
    "css/server_power.css",
    "css/electricity.css",
    "css/lightcontrol.css",
    "css/internet_connection.css",
    "css/repeating_tasks.css",
    "css/indoor_quality.css",
    "css/timer.css",
    "css/weather.css",
    "css/printer.css",
    "css/torrents.css",
    "css/transportation.css",
]

PIPELINE_CSS = {
    'display': {
        'source_filenames': [
            "css/custom_display.css",
        ] + PIPELINE_BASE_CSS,
        'output_filename': 'css/generated/display.css',
    },
    'door': {
        'source_filenames': (
            "css/bootstrap.css",
            "css/custom_door.css",
            "css/font-awesome.css",
            "jquery-ui/jquery-ui.css",
        ),
        'output_filename': 'css/generated/door.css',
    },
    'computer': {
        'source_filenames': [
            "css/custom_computer.css",
        ] + PIPELINE_BASE_CSS,
        'output_filename': 'css/generated/computer.css',
    },
    'kitchen': {
        'source_filenames': (
            "css/bootstrap.css",
            "jquery-ui/jquery-ui.css",
            "css/font-awesome.css",
            "css/shared.css",
            "css/custom_kitchen.css",
            "css/timer.css",
        ),
        'output_filename': 'css/generated/kitchen.css',
    }
}

PIPELINE_BASE_JS = [
    "js/jquery-1.11.2.js",
    "js/jquery-noconflict.js",
    "js/bootstrap.js",
    "jquery-ui/jquery-ui.js",
    "js/moment-with-locales.js",
    "js/ws4redis_v2.js",
    "js/ws_generic.js",
    "js/generic_refresh.js",
    "js/main.js",
    "js/lightcontrol.js",
    "js/clock.js",
    "js/reload.js",

]

PIPELINE_COMPUTER_DISPLAY_COMMON = [
    "js/d3.js",
    "js/nv.d3.js",
    "js/filesize.js",
    "js/display.js",
    "js/timer.js",
    "js/custom_timers.js",
    "js/electricity.js",
    "js/internet_connection.js",
    "js/repeating_tasks.js",
    "js/indoor_quality.js",
    "js/server_power.js",
    "js/birthdays.js",
    "js/moment_auto_update.js",
    "js/lightcontrol_timed.js",
    "js/printer.js",
    "js/torrents.js",
    "js/transportation.js",
]

PIPELINE_JS = {
    'door': {
        'source_filenames':
            PIPELINE_BASE_JS + [
            "js/weather_door.js",
        ],
        'output_filename': 'js/generated/door.js',
    },
    'kitchen': {
        'source_filenames':
            PIPELINE_BASE_JS + [
            "js/timer.js",
            "js/custom_timers.js",
        ],
        'output_filename': 'js/generated/kitchen.js',
    },
    'display': {
        'source_filenames':
            PIPELINE_BASE_JS +
            PIPELINE_COMPUTER_DISPLAY_COMMON +
            ["js/custom_display.js",
            "js/weather.js",
            "js/namedays.js",
        ],
        'output_filename': 'js/generated/display.js',
    },
    'computer': {
        'source_filenames':
            PIPELINE_BASE_JS +
            PIPELINE_COMPUTER_DISPLAY_COMMON +
            [
            "js/custom_computer.js",
        ],
        'output_filename': 'js/generated/computer.js',
    }
}


STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
PIPELINE_ENABLED=True
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.closure.ClosureCompressor'
PIPELINE_CLOSURE_BINARY = "/usr/bin/env closure-compiler"
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'

PIPELINE_COMPILERS = (
  'pipeline.compilers.sass.SASSCompiler',
)

PIPELINE_SASS_BINARY = "/usr/bin/env sassc"

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

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
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
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%Y-%m-%d %H:%M:%S"
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
        'statsd_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/statsd.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_file'],
            'propagate': True,
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
        }
    }
}
import djcelery
djcelery.setup_loader()

from local_settings import *
