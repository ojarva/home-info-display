# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from homedisplay.utils import publish_ws
from info_weather.models import MarineWeather
import datetime
import json
import requests


class Command(BaseCommand):
    args = ''
    help = 'Fetches marine weather information'

    def handle(self, *args, **options):
        response = requests.get("http://ilmatieteenlaitos.fi/saa/helsinki/harmaja")

        def get_second(value):
            value = value.split(u"\xa0", 1)
            return value[1]


        def parse_float(value):
            value = value.replace(",", ".").split(u"\xa0")
            return float(value[0])

        soup = BeautifulSoup(response.text)

        item = soup.find("table", {"class": "observation-text"})
        timestamp = item.find("span", {"class": "time-stamp"})
        timestamp_text = timestamp.text.split(u"\xa0")[0].split(".", 2)
        if len(timestamp_text[1]) == 1:
            timestamp_text[1] = "0" + timestamp_text[1]
        if len(timestamp_text[0]) == 1:
            timestamp_text[0] = "0" + timestamp_text[0]

        timestamp_text = "%s-%s-%s" % (timestamp_text[0], timestamp_text[1], timestamp_text[2])
        parsed_timestamp = timezone.make_aware(datetime.datetime.strptime(timestamp_text, "%d-%m-%Y %H:%M"), timezone.get_current_timezone())

        values = {}

        DIRECTIONS = {
            u"Koillis": "NE",
            u"Kaakkois": "SE",
            u"Lounais": "SW",
            u"Luoteis": "NW",
            u"Pohjois": "N",
            u"Etelä": "S",
            u"Länsi": "W",
            u"Itä": "E",
        }

        item = item.find("tbody")
        for data in item.find_all("span", {"class": "parameter-name-value"}):
            k = data.find("span", {"class": "parameter-name"}).text
            v = data.find("span", {"class": "parameter-value"}).text

            if k == u"Lämpötila":
                values["temperature"] = parse_float(v)
            elif k == u"Kosteus":
                values["humidity"] = int(parse_float(v))
            elif k == u"Kastepiste":
                values["dewpoint"] = parse_float(v)
            elif k == u"Puuska":
                values["wind_gust"] = parse_float(v)
            elif k == "Paine":
                values["pressure"] = parse_float(v)
            elif k.startswith(u"Näkyvyys"):
                values["visibility"] = int(parse_float(get_second(v)))
            elif v.endswith("m/s"):
                values["wind_speed"] = parse_float(v)
                for text, direction in DIRECTIONS.items():
                    if k.startswith(text):
                        values["wind_direction"] = direction
            elif v.startswith("(") and v.endswith(")") and "/" in v:
                values["cloudiness"] = int(v.split("/")[0].replace("(", ""))
            else:
                print k, "--", v

        datapoint, _ = MarineWeather.objects.get_or_create(location="harmaja", timestamp=parsed_timestamp, defaults=values)
        datapoint.save()
