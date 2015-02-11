from control_milight.models import LightAutomation
from control_milight.views import update_lightstate
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from ledcontroller import LedController
import datetime

class Command(BaseCommand):
    args = ''
    help = 'Run timed transitions'

    def handle(self, *args, **options):
        led = LedController(settings.MILIGHT_IP)
        time = datetime.datetime.now()
        hour = datetime.time(time.hour, time.minute)
        for item in LightAutomation.objects.filter(running=True):
            if not item.is_running(time):
                continue
            percent_done = item.percent_done(time)
            if item.action == "evening":
                print "Setting evening brightness to", ((1-percent_done)*100)
                led.set_brightness(int((1-percent_done)*100))
            elif item.action == "morning":
                print "Setting morning brightness to", ((percent_done)*100)
                led.set_brightness(int((percent_done)*100))
#            update_lightstate(transition.group.group_id, transition.to_brightness, transition.to_color)
