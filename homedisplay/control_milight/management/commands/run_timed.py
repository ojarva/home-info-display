from control_display.utils import set_destination_brightness
from control_milight.models import LightAutomation, LightGroup, update_lightstate
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from ledcontroller import LedController
import datetime
import logging
import redis

class Command(BaseCommand):
    args = ''
    help = 'Run timed transitions'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        redis_instance = redis.StrictRedis()
        led = LedController(settings.MILIGHT_IP)
        now = timezone.now()

        allowed_groups = set()
        for group in range(1, 5):
            if redis_instance.get("lightcontrol-no-automatic-%s" % group) is None:
                allowed_groups.add(group)

        for item in LightAutomation.objects.filter(running=True):
            if not item.is_running(now):
                continue
            percent_done = item.percent_done(now)
            logger.debug("Running %s, done %s%%", item.action, percent_done)

            brightness = None # Set brightness

            if item.action == "evening" or item.action == "evening-weekend":
                brightness = int((1-percent_done)*100)
            elif item.action == "morning" or item.action == "morning-weekend":
                brightness = int(percent_done * 100)

            if not item.action_if_off:
                # Don't turn on lights
                for group in list(allowed_groups): # cast to list to avoid "Set changed size during iteration"
                    item, _ = LightGroup.objects.get_or_create(group_id=group)
                    if item.on == False:
                        allowed_groups.remove(group)
            logger.debug("Only run on %s", allowed_groups)

            if item.set_white:
                for group in allowed_groups:
                    led.white(group)
                    logger.debug("Set %s to white", group)
                    update_lightstate(group, None, "white", important=False)
            if brightness:
                logger.debug("Setting brightness to %s%%", brightness)
                for group in allowed_groups:
                    group_brightness = brightness
                    if item.no_brighten:
                        item, _ = LightGroup.objects.get_or_create(group_id=group)
                        logger.debug("Current brightness: %s%%", item.current_brightness)
                        if item.current_brightness is not None:
                            group_brightness = min(item.current_brightness, group_brightness)
                    if item.no_dimming:
                        item, _ = LightGroup.objects.get_or_create(group_id=group)
                        logger.debug("Current brightness: %s%%", item.current_brightness)
                        if item.current_brightness is not None:
                            group_brightness = max(item.current_brightness, group_brightness)
                    logger.debug("Setting %s to %s", (group, group_brightness))
                    led.set_brightness(group_brightness, group)
                    update_lightstate(group, group_brightness, important=False)
                set_destination_brightness()
