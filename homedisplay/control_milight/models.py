# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import serializers
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from homedisplay.utils import publish_ws
from ledcontroller import LedController
import datetime
import json
import logging
import redis

__all__ = ["LightGroup", "LightAutomation", "update_lightstate", "is_any_timed_running", "get_serialized_timed_action", "get_serialized_lightgroup", "get_morning_light_level", "set_morning_light"]

led = LedController(settings.MILIGHT_IP)
redis_instance = redis.StrictRedis()
logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))


def get_morning_light_level(group_id=None):
    # TODO: this is called relatively often, and this fetches all LightGroup objects on every iteration.
    max_brightness = 0
    items = LightGroup.objects.filter(on=True)
    if group_id is None or group_id == 0:
        # Process all groups
        c = items.filter(color='white').count()
        if c > 0:
            # If any light is on and white, brightness should be 10
            max_brightness = 10

    else:
        # Process only a single group
        for g in items:
            if g.group_id == group_id:
                # Current group
                if g.color != "white":
                    # Color is not white -> change to white & 0
                    logger.debug("Group %s is not white. Morning light brightness should be 0", g.group_id)
                    return 0
                # Color is white
                brightness = g.current_brightness
                if brightness is None:
                    logger.debug("Group %s brightness is not available. Morning light brightness should be 0", g.group_id)
                    return 0
                # Current group is on and white. Brightness is always 10.
                logger.debug("Group %s is on and white. Morning light brightness should be 10.", g.group_id)
                return 10
            # Take maximum brightness
            max_brightness = max(g.current_brightness or 0, max_brightness)
    # Maximum brightness is 10, do not go over it.
    current_brightness = min(10, max_brightness)
    logger.debug("Group %s morning light brightness should be %s.", group_id, current_brightness)
    return current_brightness


def set_morning_light(group):
    brightness = get_morning_light_level(group)
    logger.debug("set_morning_light: morning light level for group %s is %s", group, brightness)
    led.white(group)
    led.set_brightness(brightness, group)
    update_lightstate(group, brightness, "white")
    logger.info("Set morning light for group %s. Brightness is %s", group, brightness)


def get_main_buttons():
    all_off = True
    all_on = True
    all_on_white_bright = True
    all_on_white_dim = True
    all_on_red_dim = True
    for group in LightGroup.objects.all():
        if group.on:
            all_off = False
            if group.color != "white":
                all_on_white_bright = False
                all_on_white_dim = False
            elif group.current_brightness != 100:
                all_on_white_bright = False
            if group.current_brightness > 10:
                all_on_white_dim = False
            if group.color != "red":
                all_on_red_dim = False
        else:
            all_on = False
            all_on_white_bright = False
            all_on_white_dim = False
            all_on_red_dim = False
    return {"on": all_on_white_bright, "off": all_off, "night": all_on_red_dim, "lights-morning-auto": all_on_white_dim}

def get_serialized_lightgroups():
    return [get_serialized_lightgroup(item) for item in LightGroup.objects.all()]

def get_serialized_lightgroup(item):
    ret = json.loads(serializers.serialize("json", [item]))[0]
    ret["fields"]["current_brightness"] = item.current_brightness
    ret["fields"]["morning_light_level"] = get_morning_light_level(item.group_id)
    return ret

def get_serialized_timed_action(item):
    ret = json.loads(serializers.serialize("json", [item]))
    ret[0]["fields"]["start_datetime"] = item.get_start_datetime().isoformat()
    ret[0]["fields"]["end_datetime"] = item.get_end_datetime().isoformat()
    for group in range(1, 5):
        if redis_instance.get("lightcontrol-no-automatic-%s" % group) is not None:
            ret[0]["fields"]["is_overridden"] = True
            break
    return ret

def update_lightstate(group, brightness, color=None, on=True, **kwargs):
    if group == 0:
        for group_num in range(1, 5):
            update_lightstate(group_num, brightness, color, on, **kwargs)
        return

    logger.debug("Updating lightstate: group=%s, brightness=%s, color=%s, on=%s, kwargs=%s", group, brightness, color, on, kwargs)
    if kwargs.get("important", True) != False:
        timed_ends_at = is_any_timed_running()
        logger.debug("Lightstate: important is True")
        if timed_ends_at != False:
            time_until_ends = (timed_ends_at - timezone.now()).total_seconds() + 65
            logger.debug("Next timed task ends at %s (%s seconds)", timed_ends_at, time_until_ends)
            logger.info("Setting timed lightcontrol override for %s until %s", group, time_until_ends)
            redis_instance.setex("lightcontrol-no-automatic-%s" % group, int(time_until_ends), True)
            publish_ws("lightcontrol_timed_override", {"action": "pause"})

    (state, _) = LightGroup.objects.get_or_create(group_id=group)
    if color is not None:
        logger.debug("Setting color for group %s, from %s to %s", group, state.color, color)
        state.color = color

    if brightness is not None:
        if state.color == "white":
            logger.debug("Setting white brightness for group %s, from %s to %s", group, state.white_brightness, brightness)
            state.white_brightness = brightness
        else:
            logger.debug("Setting rgb brightness for group %s, from %s to %s", group, state.rgbw_brightness, brightness)
            state.rgbw_brightness = brightness
    logger.debug("Setting state on=%s for group %s (was %s)", on, group, state.on)
    state.on = on
    state.save()
    return state

def is_any_timed_running():
    timestamp = timezone.now()
    for timed in LightAutomation.objects.all():
        if timed.is_running(timestamp):
            return timed.get_end_datetime()
    return False

class LightGroup(models.Model):
    group_id = models.PositiveSmallIntegerField(unique=True, verbose_name="Numero")
    description = models.CharField(max_length=20, null=True, blank=True, verbose_name="Kuvaus")
    rgbw_brightness = models.PositiveSmallIntegerField(null=True, verbose_name="Värillisen kirkkaus")
    white_brightness = models.PositiveSmallIntegerField(null=True, verbose_name="Valkoisen kirkkaus")
    color = models.TextField(null=True, blank=True, verbose_name="Väri")
    on = models.NullBooleanField(null=True, verbose_name="Päällä")

    def __unicode__(self):
        return "%s (%s), color: %s, on: %s, rgbw: %s, white: %s" % (self.description, self.group_id, self.color, self.on, self.rgbw_brightness, self.white_brightness)

    @property
    def current_brightness(self):
        if self.color == "white":
            return self.white_brightness
        return self.rgbw_brightness

    class Meta:
        verbose_name = "Valoryhmä"
        verbose_name_plural = "Valoryhmät"
        ordering = ("group_id", )

class LightAutomation(models.Model):
    action = models.CharField(max_length=30, verbose_name="Sisäinen nimi toiminnolle", unique=True)
    running = models.NullBooleanField(default=True, verbose_name="Päällä")
    start_time = models.TimeField(verbose_name="Aloitusaika")
    duration = models.IntegerField(verbose_name="Kestoaika sekunteina") # in seconds
    active_days = models.CharField(max_length=7, default="0000000", verbose_name="Päivät", help_text="ma-su, 0=pois, 1=päällä")

    turn_display_on = models.BooleanField(default=False, blank=True, verbose_name="Käynnistä näyttö", help_text="Käynnistä näyttö ohjelman alussa")
    action_if_off = models.BooleanField(default=True, blank=True, verbose_name="Suorita sammutetuille", help_text="Suorita ohjelma myös sammutetuille valoille")
    set_white = models.BooleanField(default=False, blank=True, verbose_name="Vaihda väri valkoiseksi", help_text="Vaihda ohjelman aikana väri valkoiseksi")
    no_brighten = models.BooleanField(default=False, blank=True, verbose_name="Älä lisää valojen kirkkautta", help_text="Jos raksitettu, valojen kirkkautta ei koskaan lisätä")
    no_dimming = models.BooleanField(default=False, blank=True, verbose_name="Älä vähennä valojen kirkkautta", help_text="Jos raksitettu, valojen kirkkautta ei koskaan vähennetä")

    def __unicode__(self):
        return "%s (%s) %s -- %s" % (self.action, self.running, self.start_time, self.duration)

    class Meta:
        verbose_name = "Valo-ohjelma"
        verbose_name_plural = "Valo-ohjelmat"
        ordering = ("action", )

    def is_running_on_day(self, weekday):
        if self.active_days[weekday] == "0":
            return False
        return True

    def get_end_datetime(self):
        """ Returns datetime.datetime for next ending time. """
        duration = max(self.duration, 300)
        timestamp = (timezone.now() - datetime.timedelta(seconds=duration)).time()
        return self.get_start_datetime(timestamp) + datetime.timedelta(seconds=duration)

    def get_start_datetime(self, current_time=None):
        """ Returns datetime.datetime for next starting time. """
        if current_time is None:
            current_time = timezone.now().time()
        weekday = timezone.now().weekday()
        original_weekday = weekday
        plus_days = datetime.timedelta(seconds=0)
        for a in range(0, 7):
            if self.is_running_on_day(weekday):
                if weekday == original_weekday and self.start_time < current_time:
                    # Already gone for this day.
                    pass
                else:
                    return timezone.make_aware(datetime.datetime.combine(datetime.date.today(), self.start_time) + plus_days, timezone.get_current_timezone())

            plus_days += datetime.timedelta(days=1)
            weekday += 1
            if weekday > 6:
                weekday = 0
        # Not active on any day.
        return None

    def is_running(self, timestamp):
        """ Returns true if timer is currently running """
        if timestamp < self.get_end_datetime() and timestamp > self.get_start_datetime():
            return True
        return False

    def percent_done(self, timestamp):
        if self.duration == 0:
            return 1.0
        if not self.is_running(timestamp):
            return
        return float((timestamp - self.get_start_datetime()).total_seconds()) / self.duration

@receiver(post_save, sender=LightAutomation, dispatch_uid="lightautomation_post_save")
def publish_lightautomation_saved(sender, instance, *args, **kwargs):
    publish_ws("lightcontrol_timed_%s" % instance.action, get_serialized_timed_action(instance))

@receiver(post_save, sender=LightGroup, dispatch_uid="lightgroup_post_save")
def publish_lightgroup_saved(sender, instance, *args, **kwargs):
    publish_ws("lightcontrol", {"groups": get_serialized_lightgroups(), "main_buttons": get_main_buttons()})
