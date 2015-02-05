from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from indoor_quality.models import IndoorQuality
import redis
r = redis.StrictRedis()

class Command(BaseCommand):
    args = ''
    help = 'Fetches indoor air quality information'

    def handle(self, *args, **options):
        co2 = open("/mnt/owfs/20.F1580D000000/CO2/ppm").read()
        temperature = open("/mnt/owfs/22.53B222000000/temperature").read()
        a = IndoorQuality(co2=co2, temperature=temperature)
        a.save()
        r.publish("home:broadcast:indoor", "updated")
