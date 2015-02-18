from django.core.management.base import BaseCommand, CommandError
from info_weather.models import Weather
from info_weather.views import get_weather_data
import datetime
import json
import redis
import requests
import xmltodict


class Command(BaseCommand):
    args = ''
    help = 'Fetches weather information'

    def handle(self, *args, **options):
        redis_instance = redis.StrictRedis()
        now = datetime.datetime.now()
        current_time = now - datetime.timedelta(minutes=int(now.strftime("%M")), seconds=int(now.strftime("%S")), microseconds=int(now.strftime("%f")))
        r = requests.get("http://desktopfw.weather.com/weather/local/FIXX0001?hbhf=48&ut=C")
        data = r.text
        data = xmltodict.parse(data)
        data = json.loads(json.dumps(data))
        for hour in data["weather"]["hbhf"]["hour"]:
            current_hour = int(hour["@h"])
            delta_to_processing_time = datetime.timedelta(hours=current_hour)
            timestamp = current_time + delta_to_processing_time
            Weather.objects.filter(date=timestamp, hour=int(timestamp.strftime("%H"))).delete()
            a = Weather(date=timestamp, hour=int(timestamp.strftime("%H")), icon=hour["icon"], ppcp=int(hour["ppcp"]), dewpoint=int(hour["dewp"]), feels_like=int(hour["flik"]), humidity=int(hour["hmid"]), temperature=int(hour["tmp"]), description=hour["t"], wind_direction=hour["wind"]["t"], wind_gust=hour["wind"]["gust"], wind_speed=hour["wind"]["s"])
            a.save()
#            self.stdout.write("Saved %s" % timestamp)
        redis_instance.publish("home:broadcast:generic", json.dumps({"key": "weather", "content": get_weather_data()}))
