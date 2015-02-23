from control_milight.models import LightGroup
from django.utils import timezone
from info_weather.views import get_sun_info
import datetime
import subprocess
import redis

redis_instance = redis.StrictRedis()

def run_display_command(cmd):
    env = {"DISPLAY": ":0"}
    p = subprocess.Popen(["xset", "dpms", "force", cmd], env=env)
    p.wait()

def get_desired_brightness():
    brightness = 1 # Sensible default
    min_brightness = 0.3
    now = timezone.now()

    # Fetch sun information
    sun_info = get_sun_info()
    if sun_info["sunrise"] < now and sun_info["sunset"] > now:
        if now.hour < 20:
            # Sun is up and it is not too late. Full brightness, please.
            return 1
        min_brightness = 0.6
    else:
        sun_is_up = False

    light_brightness_set = False
    light_brightness = 0
    for lightgroup in LightGroup.objects.all():
        if lightgroup.group_id == 4:
            continue
        light_brightness_set = True
        if lightgroup.on == True:
            group_brightness = lightgroup.current_brightness
            if group_brightness is not None:
                light_brightness = max(light_brightness, group_brightness)

    if light_brightness_set:
        return max(min_brightness, float(light_brightness) / 100)
    return min_brightness

def set_destination_brightness(brightness=None):
    if brightness is None:
        brightness = get_desired_brightness()
    redis_instance.setex("display-control-destination-brightness", 60, brightness)
