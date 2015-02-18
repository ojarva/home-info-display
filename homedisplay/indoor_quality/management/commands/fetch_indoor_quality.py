from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
import redis
import json

class Command(BaseCommand):
    args = ''
    help = 'Fetches indoor air quality information'

    def handle(self, *args, **options):
        r = redis.StrictRedis()
        co2 = float(open(settings.CO2_FILE).read())
        temperature = float(open(settings.TEMPERATURE_FILE).read())
        r.rpush("air-quality-co2", co2)
        r.rpush("air-quality-temperature", temperature)
        r.publish("home:broadcast:generic", json.dumps({"key": "indoor_temperature", "content": {"value": temperature}}))
        r.publish("home:broadcast:generic", json.dumps({"key": "indoor_co2", "content": {"value": co2}}))
