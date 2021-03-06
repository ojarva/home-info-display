from .display_utils import cancel_delayed_shutdown
from .tasks import run_display_command_task
from django.utils import timezone
from homedisplay.utils import publish_ws
from info_weather.utils import get_sun_info
import json
import logging
import redis

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))

redis_instance = redis.StrictRedis()

__all__ = ["initiate_delayed_shutdown",
           "get_desired_brightness", "set_destination_brightness"]


def initiate_delayed_shutdown():
    """ Initiate delayed shutdown

    Automatically cancel possible other delayed shutdowns.
    """
    cancel_delayed_shutdown()
    redis_instance.setex("display-control-command", 120, "off")
    display_task = run_display_command_task.apply_async(
        countdown=30, expires=120)
    redis_instance.set("display-control-task", display_task.task_id)
    publish_ws("shutdown", "delayed-shutdown")


def get_desired_brightness():
    """ Calculate optimal screen brightness based on sun and lighting """
    logger.debug("Getting optimal brightness")
    min_brightness = 0.3
    now = timezone.now()

    # Fetch sun information
    sun_info = get_sun_info()
    if sun_info["sunrise"] < now and sun_info["sunset"] > now:
        if now.hour < 22:
            # Sun is up and it is not too late. Full brightness
            logger.debug("Sun is up and it's not too late. Set brightness to full")
            return 1
        min_brightness = 0.6

    light_brightness_set = False
    light_brightness = 0

    return 1  # TODO

    if light_brightness_set:
        return_brightness = max(min_brightness, float(light_brightness) / 100)
        logger.debug("Setting brightness to %s", return_brightness)
        return return_brightness
    logger.debug("Setting brightness to minimum allowed: %s", min_brightness)
    return min_brightness


def set_destination_brightness(brightness=None):
    """ Set display brightness

    If brightness is None, current brightness will be calculated automatically."""
    if brightness is None:
        brightness = get_desired_brightness()
        logger.debug(
            "Setting destination brightness to automatically calculated %s", brightness)
    else:
        logger.debug("Setting destination brightness to %s", brightness)
    redis_instance.publish("display-control-set-brightness", brightness)
