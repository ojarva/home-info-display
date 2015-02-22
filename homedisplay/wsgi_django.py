# entry point for the Django loop
import os
from raven import Client
from raven.middleware import Sentry

from raven_settings import DSN

client = Client(DSN)

os.environ.update(DJANGO_SETTINGS_MODULE='homedisplay.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
application = Sentry(application, client=client)
