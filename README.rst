Info display
============

Info display for showing relevant information and controlling things lying around.

For you, this code is useless without plenty of customizations. It's offered here only for reference and inspiration.


Installation
------------

- Install redis and sql database (don't use sqlite, you'll hit problems with locking)

::
  virtualenv prod
  source prod/bin/activate
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver

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
