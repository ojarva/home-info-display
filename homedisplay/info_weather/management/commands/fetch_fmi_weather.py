# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from homedisplay.utils import publish_ws
import json
import redis
import requests
import time

class Command(BaseCommand):
    args = ''
    help = 'Fetches weather information'

    def handle(self, *args, **options):
        redis_instance = redis.StrictRedis()

        headers = {
            "Accept-Encoding": None,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36",
        }

        # Fetch warnings - Sörnäinen
        response = requests.get("http://m.fmi.fi/mobile/interfaces/warnings.php?l=fi&version=1.1.10&preventcache=%s654" % time.time(), headers=headers)
        redis_instance.setex("weather-main-warnings", 7200, response.text)
        main_warnings = response.json()

        # Fetch forecasts
        response = requests.get("http://m.fmi.fi/mobile/interfaces/weatherdata.php?locations=636242&l=fi&version=1.1.10&preventcache=%s070" % time.time(), headers=headers)
        redis_instance.setex("weather-main-forecasts", 7200, response.text)
        main_forecasts = response.json()

        # Harmaja forecasts
        response = requests.get("http://m.fmi.fi/mobile/interfaces/weatherdata.php?locations=658802&l=en&version=1.1.10&preventcache=%s842" % time.time(), headers=headers)
        redis_instance.setex("weather-marine-forecasts", 7200, response.text)
        marine_forecasts = response.json()

        all_info = {"main_forecasts": main_forecasts, "main_warnings": main_warnings, "marine_forecasts": marine_forecasts}
        redis_instance.setex("weather-all", 7200, json.dumps(all_info))

        publish_ws("weather", all_info)
