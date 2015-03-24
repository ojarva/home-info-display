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

Load fixtures for transitions:

::

  python manage.py loaddata control_milight/fixtures/LightAutomation.json

Test everything with Django server:

::

  python manage.py migrate
  python manage.py runserver

For production, configure uwsgi:

::

  uwsgi --virtualenv /path/to/virtualenv --socket /path/to/django.socket --buffer-size=32768 --workers=5 --master --module wsgi_django
  uwsgi --virtualenv /path/to/virtualenv --http-socket /path/to/web.socket --gevent 100 --http-websockets --workers=2 --master --module wsgi_websocket

For production, remember to run "manage.py collectstatic". Also, running "manage.py compress --force" caches compressed css and javascript files.

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


Light operation
---------------

There is three ways to control lights:

- Using buttons and sliders on the UI. These either use per-source controls (when off button is pressed on the computer UI, there can be different action compared to door UI)
- With scheduled programs
- With automatic triggers (magnet switches and PIRs)

For manual controls, brightness is decided with following logic:

- Morning/evening white lights: 0% if no other group is on with brightness >0%. Otherwise min(brightest group, 10)
- Automatic brightness buttons: same logic as with automatic triggers
- Other buttons: manually configured

Scheduled programs:

- Either morning (brightness up) or evening (brightness down) programs. Brightness down programs do not turn lights on, or adjust brightness up.
- Any manual operation will pause scheduled programs for that group

Automatic triggers brightness, color and timing:

- Timer is 10 minutes during days and two minutes during nights.
- Color is white during days and red during nights (except if any group is on with white).
- Brightness: if any other group is on, use brightness from brightest group. If not, use brightness from scheduled programs. If none is running, 0% for nights and 100% for days.

Background workers
------------------

Crontab:

::

  # Fetch weather information from weather.com
  04 *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_weather > /dev/null
  # Fetch more accurate weather information from fmi.fi
  04 *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_fmi_weather > /dev/null
  # Fetch internet connection information from Huawei modem
  *  *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_internet_information > /dev/null
  # Periodically average and store all air quality information from redis
  *  *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py add_air_timepoint > /dev/null
  # Run morning and evening transitions
  *  *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py run_timed > /dev/null
  # Fetch electricity information
  15 2    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_electricity > /dev/null
  # Update public transportation schedules
  */5 *   *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_transportation
  # Get outdoor air quality measurements from HSY website
  30 *    *   *  *     cd home-info-display/homedisplay; ~/homedisplay-env/bin/python manage.py fetch_outside_air_quality

Supervisord example configuration files can be found from supervisor-conf.d folder.
