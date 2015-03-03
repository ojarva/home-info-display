from control_display.utils import set_destination_brightness
from .models import LightAutomation, LightGroup, update_lightstate
from django.conf import settings
from django.utils import timezone
from homedisplay.utils import publish_ws
from ledcontroller import LedController
import logging
import redis

logger = logging.getLogger(__name__)
redis_instance = redis.StrictRedis()


def run_timed_actions():
    """ Runs light programs """
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
                group_item, _ = LightGroup.objects.get_or_create(group_id=group)
                if group_item.on == False:
                    allowed_groups.remove(group)
        logger.debug("Only run on %s", allowed_groups)

        if item.set_white:
            for group in allowed_groups:
                led.white(group)
                logger.debug("Set %s to white", group)
                update_lightstate(group, None, "white", important=False)
        if brightness:
            logger.debug("Setting brightness to %s%%", brightness)
            publish_ws("lightcontrol-timed-brightness-%s" % item.action, brightness)
            for group in allowed_groups:
                group_brightness = brightness
                group_item, _ = LightGroup.objects.get_or_create(group_id=group)
                if item.no_brighten:
                    logger.debug("Current brightness: %s%%", group_item.current_brightness)
                    if group_item.current_brightness is not None:
                        group_brightness = min(group_item.current_brightness, group_brightness)
                if item.no_dimming:
                    logger.debug("Current brightness: %s%%", group_item.current_brightness)
                    if group_item.current_brightness is not None:
                        group_brightness = max(group_item.current_brightness, group_brightness)
                if group_item.current_brightness:
                    if led.get_brightness_level(group_brightness) == led.get_brightness_level(group_item.current_brightness):
                        logger.debug("Not sending brightness update to %s: no difference in brightness level", group)
                        continue
                logger.debug("Setting %s to %s", (group, group_brightness))
                led.set_brightness(group_brightness, group)
                update_lightstate(group, group_brightness, important=False)
            set_destination_brightness()
