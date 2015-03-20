# -*- coding: utf-8 -*-

from control_display.utils import set_destination_brightness
from control_display.display_utils import run_display_command
import models as light_models
import info_timers.utils as timer_utils
from django.conf import settings
from django.utils import timezone
from homedisplay.utils import publish_ws
from ledcontroller import LedController
import datetime
import logging
import redis

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))

redis_instance = redis.StrictRedis()

def set_automatic_trigger_light(group):
    state, _ = light_models.LightGroup.objects.get_or_create(group_id=group)
    # If already on, don't do anything
    if state.on and not state.on_automatically:
        logger.debug("Group %s is already on. Skip automatic triggering", group)
        return

    led = LedController(settings.MILIGHT_IP)
    now = timezone.now()
    nowd = datetime.datetime.now()

    # Determine proper brightness:
    # - If other lights are on, use that.
    # - If not, based on time
    brightness = 0
    color = "white"
    brightness_set = False
    color_set = False
    for lightgroup in light_models.LightGroup.objects.all():
        if lightgroup.on == True:
            group_brightness = lightgroup.current_brightness
            if group_brightness is not None:
                logger.debug("Brightness for group %s is %s", lightgroup.group_id, group_brightness)
                brightness_set = True

                if lightgroup.color == "white":
                    color = "white"
                    color_set = True
                elif not color_set and lightgroup.color:
                    # Color is not set and lightgroup color is known (!None)
                    color = lightgroup.color

                brightness = max(brightness, group_brightness)


    hour = nowd.hour

    if not brightness_set:
        # No lights are on. Decide color and brightness by time of day.
        # TODO: use LightAutomation programs here
        if hour > 22 or hour < 6:
            # 23:00-05:59
            color = "red"
            brightness = 0
        else:
            color = "white"
            brightness = 100

    if hour > 22 or hour < 6:
        on_until = now + datetime.timedelta(minutes=2)
    else:
        on_until = now + datetime.timedelta(minutes=10)

    led.on(group)
    led.set_color(color, group)
    led.set_brightness(brightness, group)
    light_models.update_lightstate(group, brightness, color, True, automatic=True, on_until=on_until)
    timer_utils.update_group_automatic_timer(group, on_until)


def process_automatic_trigger(trigger):
    BED = 1
    TABLE = 2
    KITCHEN = 3
    DOOR = 4

    triggers = set()
    if trigger == "front-door":
        triggers.add(DOOR)
        #TODO: bathroom
    if trigger == "kitchen":
        triggers.update([KITCHEN, TABLE])
    if trigger == "hall":
        triggers.update([DOOR, KITCHEN])
    if trigger == "table":
        triggers.add(TABLE)

    for group in triggers:
        set_automatic_trigger_light(group)

def run_timed_actions():
    """ Runs light programs """
    led = LedController(settings.MILIGHT_IP)
    now = timezone.now()

    allowed_groups = set()
    for group in range(1, 5):
        if redis_instance.get("lightcontrol-no-automatic-%s" % group) is None:
            allowed_groups.add(group)

    for item in light_models.LightAutomation.objects.filter(running=True):
        if not item.is_running(now):
            continue
        percent_done = item.percent_done(now)
        logger.debug("Running %s, done %s%%", item.action, percent_done * 100)

        if item.turn_display_on:
            run_display_command("on")

        brightness = None # Set brightness

        if item.action == "evening" or item.action == "evening-weekend":
            brightness = int((1-percent_done)*100)
        elif item.action == "morning" or item.action == "morning-weekend":
            brightness = int(percent_done * 100)

        if not item.action_if_off:
            # Don't turn on lights
            for group in list(allowed_groups): # cast to list to avoid "Set changed size during iteration"
                group_item, _ = light_models.LightGroup.objects.get_or_create(group_id=group)
                if group_item.on == False:
                    allowed_groups.remove(group)
        logger.debug("Only run on %s", allowed_groups)

        if item.set_white:
            for group in allowed_groups:
                led.white(group)
                logger.debug("Set %s to white", group)
                light_models.update_lightstate(group, None, "white", important=False)

        if brightness > 95:
            brightness = 100
        elif brightness < 5:
            brightness = 0
        logger.debug("Setting brightness to %s%%", brightness)
        publish_ws("lightcontrol-timed-brightness-%s" % item.action, brightness)
        for group in allowed_groups:
            group_brightness = brightness
            group_item, _ = light_models.LightGroup.objects.get_or_create(group_id=group)
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
            logger.debug("Setting %s to %s", group, group_brightness)
            led.set_brightness(group_brightness, group)
            light_models.update_lightstate(group, group_brightness, important=False)
        set_destination_brightness()
