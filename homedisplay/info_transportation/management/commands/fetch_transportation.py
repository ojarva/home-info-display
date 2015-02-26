from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from info_transportation.hsl_api import HSLApi
from info_transportation.models import Stop, Line, Data, get_departures
from django.utils import timezone
import datetime
import json
import redis
import requests

class Command(BaseCommand):
    args = ''
    help = 'Fetches transportation information'

    def handle(self, *args, **options):
        hsl = HSLApi(settings.HSL_USERNAME, settings.HSL_PASSWORD)
        redis_instance = redis.StrictRedis()
        now = timezone.now()
        Data.objects.filter(time__lte=now).delete()
        data = []
        for stop in Stop.objects.all():
            lines = Line.objects.filter(show_line=True, stop=stop)
            if len(lines) > 0:
                departures = hsl.get_timetable(stop.stop_number)
                # O(n*m), this could be optimized.
                for line in lines:
                    for departure in departures:
                        if departure["line_number"] == line.line_number_raw:
                            timezone_aware = timezone.make_aware(departure["timestamp"], timezone.get_current_timezone())
                            a, created = Data.objects.get_or_create(line=line, time=timezone_aware)
                            if created:
                                a.save()

        redis_instance.publish("home:broadcast:generic", json.dumps({"key": "public-transportation", "content": get_departures()}))
