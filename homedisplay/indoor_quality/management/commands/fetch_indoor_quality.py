from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from indoor_quality.models import IndoorQuality
import redis
r = redis.StrictRedis()

class Command(BaseCommand):
    args = ''
    help = 'Fetches indoor air quality information'

    def handle(self, *args, **options):
        co2 = open(settings.CO2_FILE).read()
        temperature = open(settings.TEMPERATURE_FILE).read()
        a = IndoorQuality(co2=co2, temperature=temperature)
        a.save()
        r.publish("home:broadcast:indoor", "updated")
