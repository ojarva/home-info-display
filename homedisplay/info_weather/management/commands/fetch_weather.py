from django.core.management.base import BaseCommand, CommandError
from homedisplay.utils import publish_ws
from info_weather.models import Weather
from info_weather.views import get_weather_data
import datetime
import json
import requests
import xmltodict

class Command(BaseCommand):
    args = ''
    help = 'Fetches weather information'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        current_time = now - datetime.timedelta(minutes=int(now.strftime("%M")), seconds=int(now.strftime("%S")), microseconds=int(now.strftime("%f")))
        r = requests.get("http://desktopfw.weather.com/weather/local/FIXX0001?hbhf=48&ut=C&cc=*")
        data = r.text
        data = xmltodict.parse(data)
        data = json.loads(json.dumps(data))
        # TODO: process other fields from cc
        uv = int(data["weather"]["cc"]["uv"]["i"])
        for hour in data["weather"]["hbhf"]["hour"]:
            current_hour = int(hour["@h"])
            delta_to_processing_time = datetime.timedelta(hours=current_hour)
            timestamp = current_time + delta_to_processing_time
            wind_speed = int(hour["wind"]["s"])
            wind_speed *= 0.44704 # Convert to meters per second
            wind_gust = hour["wind"]["gust"]
            if wind_gust == "N/A":
                wind_gust = None
            else:
                wind_gust = int(wind_gust) * 0.44704 # Convert to meters per second
            Weather.objects.filter(date=timestamp, hour=int(timestamp.strftime("%H"))).delete()
            a = Weather(date=timestamp,
                        hour=timestamp.hour,
                        icon=hour["icon"],
                        ppcp=int(hour["ppcp"]),
                        dewpoint=int(hour["dewp"]),
                        feels_like=int(hour["flik"]),
                        humidity=int(hour["hmid"]),
                        temperature=int(hour["tmp"]),
                        description=hour["t"],
                        wind_direction=hour["wind"]["t"],
                        wind_gust=wind_gust,
                        wind_speed=wind_speed,
                        uv=uv)
            a.save()
            uv = None # UV is only available for current timestamp
        publish_ws("weather", get_weather_data())
