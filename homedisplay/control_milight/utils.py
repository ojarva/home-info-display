# -*- coding: utf-8 -*-

from control_display.display_utils import run_display_command
from control_display.utils import set_destination_brightness
from django.conf import settings
from django.utils import timezone
from homedisplay.utils import publish_ws
from ledcontroller import LedController
import datetime
import info_timers.utils as timer_utils
import logging
import models as light_models
import redis

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))

redis_instance = redis.StrictRedis()

def get_current_settings_for_light(group_id):
    """ Returns current brightness for group, based on the following system:
        1) Brightness and color of lights that are on (and set on manually)
        2) Note color of lights that were set on automatically
        3) Light programs (if running)
            - If light program is running, use it. No need to care about overrides - overrides are active only if light group is manually set on.
            - Use color from step 2. If not set in step 2, use white.
        4) Time of day:
            - Dim red between programs during nights and bright white during days.
    """
    now = timezone.now()
    nowd = datetime.datetime.now()
    weekday = nowd.weekday()

    today_morning_program = None
    today_evening_program = None

    color = "red"
    color_set = False

    # 1) Brightness of manually set lights that are on

    brightness_set = False
    brightness = None
    for lightgroup in light_models.LightGroup.objects.all():
        if lightgroup.on is True:
            # Lightgroup is on.
            if lightgroup.on_automatically is False:
                # Set on manually
                group_brightness = lightgroup.current_brightness
                if group_brightness is not None:
                    logger.debug("Brightness for group %s is %s", lightgroup.group_id, group_brightness)
                    brightness_set = True
                    brightness = max(brightness, group_brightness)
            if lightgroup.color == "white":
                color = "white"
                color_set = True


    if brightness_set:
        logger.info("Brightness for group %s: set by another group. Brightness: %s, color: %s", group_id, brightness, color)
        return (brightness, color)

    # 2) Light programs (if running)
    for program in light_models.LightAutomation.objects.all():
        percent_done = program.percent_done(now)
        if percent_done is not None and program.is_running(now):
            #Program is running.
            brightness = get_program_brightness(program.action, percent_done)
            logger.info("Brightness for group %s set by program %s, %s%%. Color: %s", group_id, program.action, percent_done, color)
            return (brightness, color)
        if program.is_running_on_day(weekday):
            if program.action.startswith("morning"):
                today_morning_program = program
            elif program.action.startswith("evening"):
                today_evening_program = program
            else:
                raise NotImplementedError("Unknown program action: %s" % program.action)

    # 3) Time of day (bright between programs during day)
    if today_morning_program:
        logger.debug("Morning program is defined for this day with start_time: %s", today_morning_program.start_time)
        # Morning program is defined.
        if nowd.time() < today_morning_program.start_time:
            # Time is before the beginning of morning program.
            logger.info("Brightness for group %s set by morning program. Brightness: %s, color: %s", group_id, 0, "red")
            return (0, "red")

    if today_evening_program:
        logger.debug("Evening program is defined for this day with end_time: %s", today_evening_program.end_time)
        if nowd.time() > today_evening_program.end_time:
            # Time is after the end of evening program.
            logger.info("Brightness for group %s set by evening program. Brightness: %s, color: %s", group_id, 0, "red")
            return (0, "red")

    # Default
    logger.info("Default brightness for group %s", group_id)
    return (100, "white")

def convert_group_to_automatic(group, on_until):
    if group == 0:
        for group in range(1, 5):
            convert_group_to_automatic(group, on_until)
        return

    state, _ = light_models.LightGroup.objects.get_or_create(group_id=group)
    if not state.on:
        # Group is off - pass.
        logger.info("Tried to convert %s to automatically triggered, but group is not on", group)
        # Ensure group is really off
        led = LedController(settings.MILIGHT_IP)
        led.off(group)
        return

    state.on_automatically = True
    state.on_until = on_until
    state.save()
    timer_utils.update_group_automatic_timer(group, on_until)

def set_automatic_trigger_light(group, take_action=True, **kwargs):
    """ Returns True if needs to take action, False otherwise """
    quick = kwargs.get("quick", False)

    state, _ = light_models.LightGroup.objects.get_or_create(group_id=group)
    # If already on, don't do anything
    if state.on and not state.on_automatically:
        logger.debug("Group %s is already on. Skip automatic triggering", group)
        return False

    led = LedController(settings.MILIGHT_IP)
    now = timezone.now()
    nowd = datetime.datetime.now()

    brightness, color = get_current_settings_for_light(group)

    hour = nowd.hour

    if hour > 22 or hour < 8:
        on_until = now + datetime.timedelta(minutes=2)
    else:
        on_until = now + datetime.timedelta(minutes=10)

    if take_action is False:
        if state.on and state.color == color:
            if color == "white":
                if state.white_brightness == brightness:
                    return False
            elif state.rgbw_brightness == brightness:
                return False

    if quick:
        original_repeat_commands = led.repeat_commands
        led.repeat_commands = 1
    led.on(group)

    if not (quick and state.color == color):
        # Only send color commands if no quick mode is specified.
        led.set_color(color, group)

    set_brightness = True
    if color == "white":
        if state.white_brightness == brightness:
            set_brightness = False
    elif state.rgbw_brightness == brightness:
        set_brightness = False

    if set_brightness:
        #Only set brightness if it's changing. This prevents data corruption bugs where brightness changes change bulb color.
        led.set_brightness(brightness, group)

    light_models.update_lightstate(group, brightness, color, True, automatic=True, on_until=on_until)
    timer_utils.update_group_automatic_timer(group, on_until)

    if kwargs.get("quick", False):
        led.repeat_commands = original_repeat_commands

    return True


def process_automatic_trigger(trigger, take_action=True, **kwargs):
    """ Returns
        - True if action was/should be taken
        - False if no action needs to be taken
    """
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

    ret = False
    for group in triggers:
        if set_automatic_trigger_light(group, take_action, **kwargs):
            ret = True
    return ret

def get_program_brightness(action, percent_done):
    brightness = 0
    if action == "evening" or action == "evening-weekend":
        brightness = (1-percent_done)*100
    elif action == "morning" or action == "morning-weekend":
        brightness = percent_done * 100
    else:
        raise NotImplementedError("Action %s is not implented." % action)

    if brightness > 95:
        brightness = 100
    elif brightness < 5:
        brightness = 0
    return int(brightness)

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

        brightness = get_program_brightness(item.action, percent_done)


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
                light_models.update_lightstate(group, None, "white", important=False, timed=True)

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
            light_models.update_lightstate(group, group_brightness, important=False, timed=True)
        set_destination_brightness()
