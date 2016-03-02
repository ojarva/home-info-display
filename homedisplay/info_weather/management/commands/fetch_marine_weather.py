# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from homedisplay.utils import publish_ws
from info_weather.models import MarineDataPoint
import aaltopoiju
import datetime
import json
import requests


class Command(BaseCommand):
    args = ''
    help = 'Fetches marine weather information'

    def handle(self, *args, **options):
        ap = aaltopoiju.Aaltopoiju()
        data = ap.fetch()

        for location in data:
            for observation in data[location]["observations"]:
                timestamp = timezone.make_aware(
                    observation["timestamp"], timezone.get_current_timezone())

                values = observation
                del values["timestamp"]
                values["forecast"] = False
                datapoint, created = MarineDataPoint.objects.get_or_create(
                    location=location, timestamp=timestamp, defaults=values)

                if not created:
                    for attr, value in values.iteritems():
                        setattr(datapoint, attr, value)
                    datapoint.save()

            for forecast in data[location]["forecasts"]:
                timestamp = timezone.make_aware(
                    forecast["timestamp"], timezone.get_current_timezone())

                values = forecast
                del values["timestamp"]
                values["forecast"] = True
                datapoint, created = MarineDataPoint.objects.get_or_create(
                    location=location, timestamp=timestamp, defaults=values)

                if not created:
                    for attr, value in values.iteritems():
                        setattr(datapoint, attr, value)
                    datapoint.save()
