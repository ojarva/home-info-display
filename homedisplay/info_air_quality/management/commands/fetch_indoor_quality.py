from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from homedisplay.utils import publish_ws
import json

class Command(BaseCommand):
    args = ''
    help = 'Fetches indoor air quality information'

    def handle(self, *args, **options):
        co2 = float(open(settings.CO2_FILE).read())
        temperature = float(open(settings.TEMPERATURE_FILE).read())
        r.rpush("air-quality-co2", co2)
        r.rpush("air-quality-temperature", temperature)
        publish_ws("indoor_temperature", {"value": temperature})
        publish_ws("indoor_co2", {"value": co2})
