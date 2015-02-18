Info display
============

Info display for showing relevant information and controlling things lying around.

For you, this code is useless without plenty of customizations. It's offered here only for reference and inspiration.


Installation
------------

Install redis and sql database (don't use sqlite, you'll hit problems with locking).

Create virtualenv:

::

  virtualenv prod
  source prod/bin/activate
  pip install -r requirements.txt

Test everything with Django server:

::

  python manage.py migrate
  python manage.py runserver

For production, configure uwsgi:

::

  uwsgi --virtualenv /path/to/virtualenv --socket /path/to/django.socket --buffer-size=32768 --workers=5 --master --module wsgi_django
  uwsgi --virtualenv /path/to/virtualenv --http-socket /path/to/web.socket --gevent 100 --http-websockets --workers=2 --master --module wsgi_websocket

And nginx (or any other web server that supports websockets):

::

  location /static {
    root /path/to/static/files;
  }
  location / {
    include /etc/nginx/uwsgi_params;
    uwsgi_pass unix:/path/to/django.socket;
  }
  location /ws/ {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://unix:/path/to/web.socket:;
  }


Crontab entries
---------------

::

  # Fetch weather information from weather.com
  04 *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_weather
  # Fetch internet connection information from Huawei modem
  *  *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_internet_information
  # Update CO2 and temperature readings from 1-wire devices
  *  *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_indoor_quality
  # Periodically average and store all air quality information from redis
  *  *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py add_air_timepoint
  # Run morning and evening transitions
  *  *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py run_timed
