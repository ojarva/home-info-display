"""
This command will create new air quality timepoint and
average all per-sensor information from redis.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from indoor_quality.models import AirDataPoint, AirTimePoint
import redis
r = redis.StrictRedis()

class Command(BaseCommand):
    args = ''
    help = 'Adds new indoor air quality timepoint'

    def handle(self, *args, **options):
        timepoint = AirTimePoint()
        timepoint.save()
        for sensor in settings.SENSOR_MAP:
            k = "air-quality-%s" % sensor
            s = 0
            c = 0
            while True:
                val = r.lpop(k)
                if val is None:
                    break
                val = float(val)
                s += val
                c += 1
            if c == 0:
                avg = None
            else:
                avg = float(s) / c
            datapoint = AirDataPoint(name=sensor, value=avg, timepoint=timepoint)
            datapoint.save()
        r.publish("home:broadcast:indoor", "updated")
