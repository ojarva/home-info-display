# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils import timezone
from ledcontroller import LedController
import datetime
import json
import logging
import redis

__all__ = ["LightGroup", "LightAutomation", "update_lightstate", "is_any_timed_running"]

led = LedController(settings.MILIGHT_IP)
redis_instance = redis.StrictRedis()
logger = logging.getLogger(__name__)

def update_lightstate(group, brightness, color=None, on=True, **kwargs):
    if group == 0:
        for group_num in range(1, 5):
            update_lightstate(group_num, brightness, color, on, **kwargs)
        return

    logger.debug("Updating lightstate: group=%s, brightness=%s, color=%s, on=%s, kwargs=%s", group, brightness, color, on, kwargs)
    timed_ends_at = is_any_timed_running()
    if kwargs.get("important", True) != False:
        if timed_ends_at != False:
            time_until_ends = (timed_ends_at - timezone.now()).total_seconds() + 65
            logger.info("Setting timed lightcontrol override for %s until %s", group, time_until_ends)
            redis_instance.setex("lightcontrol-no-automatic-%s" % group, int(time_until_ends), True)
            redis_instance.publish("home:broadcast:generic", json.dumps({"key": "lightcontrol_timed_override", "content": {"action": "pause"}}))

    (state, _) = LightGroup.objects.get_or_create(group_id=group)
    if color is not None:
        state.color = color

    if brightness is not None:
        if state.color == "white":
            state.white_brightness = brightness
        else:
            state.rgbw_brightness = brightness
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
        timestamp = (timezone.now() - datetime.timedelta(seconds=self.duration)).time()
        return self.get_start_datetime(timestamp) + datetime.timedelta(seconds=self.duration)

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
        if not self.is_running(timestamp):
            return
        return float((timestamp - self.get_start_datetime()).total_seconds()) / self.duration
