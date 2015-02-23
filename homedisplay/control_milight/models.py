from django.db import models
from ledcontroller import LedController
from django.conf import settings
from django.utils import timezone
import datetime
import json
import math
import redis

__all__ = ["LightGroup", "LightAutomation", "update_lightstate", "is_any_timed_running"]

led = LedController(settings.MILIGHT_IP)
redis_instance = redis.StrictRedis()

def update_lightstate(group, brightness, color=None, on=True, **kwargs):
    if group == 0:
        for a in range(1, 5):
            update_lightstate(a, brightness, color, on, **kwargs)

    timed_ends_at = is_any_timed_running()
    if kwargs.get("important", True) != False:
        if timed_ends_at != False:
            time_until_ends = (timed_ends_at - timezone.now()).total_seconds() + 65
            print time_until_ends
            redis_instance.setex("lightcontrol-no-automatic-%s" % group, int(time_until_ends), True)
            redis_instance.publish("home:broadcast:generic", json.dumps({"key": "lightcontrol_timed_override", "content": {"action": "pause"}}))

    (state, _) = LightGroup.objects.get_or_create(group_id=group)
    if brightness is not None:
        if color == "white":
            state.white_brightness = brightness
        else:
            state.rgbw_brightness = brightness
    if color is not None:
        state.color = color
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
    group_id = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    rgbw_brightness = models.PositiveSmallIntegerField(null=True)
    white_brightness = models.PositiveSmallIntegerField(null=True)
    color = models.TextField(null=True, blank=True)
    on = models.NullBooleanField(null=True)

    def __unicode__(self):
        return "%s (%s), color: %s, on: %s, rgbw: %s, white: %s" % (self.description, self.group_id, self.color, self.on, self.rgbw_brightness, self.white_brightness)

    def set_state(self, brightness, color=None, on=True):
        if brightness is not None:
            if color == "white":
                self.white_brightness = brightness
            else:
                self.rgbw_brightness = brightness
        if color is not None:
            self.color = color
        self.on = on
        self.save()
        return self

    @property
    def current_brightness(self):
        if self.color == "white":
            return self.white_brightness
        return self.rgbw_brightness

class LightAutomation(models.Model):
    action = models.CharField(max_length=30)
    running = models.NullBooleanField(default=True)
    start_time = models.TimeField()
    duration = models.IntegerField() # in seconds
    active_days = models.CharField(max_length=7, default="0000000")

    def __unicode__(self):
        return "%s (%s) %s -- %s" % (self.action, self.running, self.start_time, self.duration)

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

    @classmethod
    def plus_time(cls, time1, seconds):
        hours = math.floor(seconds / 3600)
        seconds = hours * 3600
        minutes = math.floor(seconds / 60)
        datetime.time(time1.hour + hours)

    def is_running(self, timestamp):
        """ Returns true if timer is currently running """
        if timestamp < self.get_end_datetime() and timestamp > self.get_start_datetime():
            return True
        return False

    def percent_done(self, timestamp):
        if not self.is_running(timestamp):
            return
        return float((timestamp - self.get_start_datetime()).total_seconds()) / self.duration
