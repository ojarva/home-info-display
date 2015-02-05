from django.core.management.base import BaseCommand, CommandError
import xmltodict
import requests
import json
import datetime
import redis
redis_instance = redis.StrictRedis()

from info_weather.models import Weather

"""
    date = models.DateField()
    hour = models.PositiveSmallIntegerField()

    icon = models.TextField()
    ppcp = models.PositiveSmallIntegerField()
    dewpoint = models.IntegerField()
    feels_like = models.IntegerField()
    humidity = models.PositiveSmallIntegerField()
    temperature = models.IntegerField()

    description = models.TextField()

    wind_direction = models.TextField()
    wind_gust = models.TextField()
    wind_speed = models.TextField()

{u'@c': u'23',
 u'@h': u'3',
 u'bt': u'P Cloudy',
 u'dewp': u'-9',
 u'flik': u'-14',
 u'hmid': u'94',
 u'icon': u'29',
 u'ppcp': u'0',
 u't': u'Partly Cloudy',
 u'tmp': u'-8',
 u'wind': {u'd': u'18', u'gust': u'N/A', u's': u'8', u't': u'NNE'}}

"""

class Command(BaseCommand):
    args = ''
    help = 'Fetches weather information'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        current_time = now - datetime.timedelta(minutes=int(now.strftime("%M")), seconds=int(now.strftime("%S")), microseconds=int(now.strftime("%f")))
        r = requests.get("http://desktopfw.weather.com/weather/local/FIXX0001?hbhf=48&ut=C")
        data = r.text
#        wget --no-cookies --header "Cookie: RMID=`echo $RANDOM | md5sum | awk {'print $1'}`" --user-agent "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 3.5.23022)"  "desktopfw.weather.com/weather/local/FIXX0001?hbhf=48&ut=C" -O-
#        data = open("info_weather/management/commands/test.xml").read()
        data = xmltodict.parse(data)
        data = json.loads(json.dumps(data))
        for hour in data["weather"]["hbhf"]["hour"]:
            current_hour = int(hour["@h"])
            delta_to_processing_time = datetime.timedelta(hours=current_hour)
            timestamp = current_time + delta_to_processing_time
            Weather.objects.filter(date=timestamp, hour=int(timestamp.strftime("%H"))).delete()
            a = Weather(date=timestamp, hour=int(timestamp.strftime("%H")), icon=hour["icon"], ppcp=int(hour["ppcp"]), dewpoint=int(hour["dewp"]), feels_like=int(hour["flik"]), humidity=int(hour["hmid"]), temperature=int(hour["tmp"]), description=hour["t"], wind_direction=hour["wind"]["t"], wind_gust=hour["wind"]["gust"], wind_speed=hour["wind"]["s"])
            a.save()
            self.stdout.write("Saved %s" % timestamp)
        redis_instance.publish("home:broadcast:weather", "updated")
