from control_milight.models import LightAutomation
from control_milight.views import update_lightstate
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from ledcontroller import LedController
import datetime
import redis


class Command(BaseCommand):
    args = ''
    help = 'Run timed transitions'

    def handle(self, *args, **options):
        redis_instance = redis.StrictRedis()
        led = LedController(settings.MILIGHT_IP)
        time = datetime.datetime.now()
        hour = datetime.time(time.hour, time.minute)
        for item in LightAutomation.objects.filter(running=True):
            if not item.is_running(time):
                continue
            percent_done = item.percent_done(time)
            if item.action == "evening" or item.action == "evening-weekend":
                brightness = int((1-percent_done)*100)
                print "Setting morning brightness to %s%%" % brightness
                led.set_brightness(brightness)
                update_lightstate(0, brightness)
            elif item.action == "morning" or item.action == "morning-weekend":
                brightness = int(percent_done * 100)
                print "Setting morning brightness to %s%%" % brightness
                led.set_brightness(brightness)
                led.white()
                update_lightstate(0, brightness, "white")
