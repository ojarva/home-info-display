# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import serializers
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from homedisplay.celery import app as celery_app
from homedisplay.utils import publish_ws
from ledcontroller import LedController
import datetime
import json
import logging
import redis

__all__ = ["LightGroup", "LightAutomation", "update_lightstate",
           "is_any_timed_running", "get_serialized_timed_action", "get_serialized_lightgroup"]

led = LedController(settings.MILIGHT_IP)
redis_instance = redis.StrictRedis()
logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))


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
    """
    kwargs:
     - no_override: don't execute overrides for lightprograms
     - automatic: this update was triggered by PIR/...
     - important: this was triggered by user action.
    """

    if group == 0:
        for group_num in range(1, 5):
            update_lightstate(group_num, brightness, color, on, **kwargs)
        return

    logger.debug("Updating lightstate: group=%s, brightness=%s, color=%s, on=%s, kwargs=%s",
                 group, brightness, color, on, kwargs)
    if kwargs.get("important", True) is True and kwargs.get("automatic", False) is False and kwargs.get("no_override", False) is False:
        timed_ends_at = is_any_timed_running()
        logger.debug("Lightstate: important is True")
        if timed_ends_at != False:
            time_until_ends = (timed_ends_at - timezone.now()
                               ).total_seconds() + 65
            logger.debug("Next timed task ends at %s (%s seconds)",
                         timed_ends_at, time_until_ends)
            logger.info(
                "Setting timed lightcontrol override for %s until %s", group, time_until_ends)
            redis_instance.setex("lightcontrol-no-automatic-%s" %
                                 group, int(time_until_ends), True)
            publish_ws("lightcontrol-timed-override", {"action": "pause"})

    state, _ = LightGroup.objects.get_or_create(group_id=group)

    state_set = False
    if kwargs.get("automatic"):
        # This is update is triggered automatically (by PIR/magnetic
        # switch/...)
        logger.debug(
            "Requested automatic triggering. on_automatically=%s", state.on_automatically)
        if state.on_automatically:
            # Keep on_automatically true
            logger.debug("Keep on_automatically=True")
            state_set = True
            state.on_automatically = True

        if not state.on:
            # Lightgroup is off.
            logger.debug("Lightgroup is off")
            if on:
                logger.debug("Lightgroup was switched on")
                # Lightgroup was switched on.
                state_set = True
                state.on_automatically = True

    on_until = kwargs.get("on_until")
    if on_until:
        # Set ending time for automatic lights.
        state.on_until = on_until

    if state_set is False and kwargs.get("timed", False) is False:
        # Default state for on_automatically
        state.on_automatically = False

    logger.debug("on_automatically=%s, on_until=%s",
                 state.on_automatically, state.on_until)

    if color is not None:
        logger.debug("Setting color for group %s, from %s to %s",
                     group, state.color, color)
        state.color = color

    if brightness is not None:
        if state.color == "white":
            logger.debug("Setting white brightness for group %s, from %s to %s",
                         group, state.white_brightness, brightness)
            state.white_brightness = brightness
        else:
            logger.debug("Setting rgb brightness for group %s, from %s to %s",
                         group, state.rgbw_brightness, brightness)
            state.rgbw_brightness = brightness
    logger.debug("Setting state on=%s for group %s (was %s)",
                 on, group, state.on)
    state.on = on
    state.save()
    return state


def is_any_timed_running():
    timestamp = timezone.now()
    for timed in LightAutomation.objects.all():
        if timed.is_running(timestamp):
            return timed.get_end_datetime()
    return False


def is_group_on(group):
    groups = LightGroup.objects.all()
    if group != 0 and group is not None:
        groups = groups.filter(group_id=group)
    for g in groups:
        if g.on == True:
            return True
    return False


class LightGroup(models.Model):
    group_id = models.PositiveSmallIntegerField(
        unique=True, verbose_name="Numero")
    description = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Kuvaus")
    rgbw_brightness = models.PositiveSmallIntegerField(
        null=True, verbose_name="Värillisen kirkkaus")
    white_brightness = models.PositiveSmallIntegerField(
        null=True, verbose_name="Valkoisen kirkkaus")
    color = models.TextField(null=True, blank=True, verbose_name="Väri")
    on = models.NullBooleanField(null=True, verbose_name="Päällä")

    on_automatically = models.BooleanField(blank=True, default=False, verbose_name="Päällä automaattisesti",
                                           help_text="Onko ryhmä päällä automaattisesti vai manuaalisesti")
    on_until = models.DateTimeField(
        blank=True, null=True, verbose_name="Automaattinen sammutusaika", help_text="Aika, johon asti valo pidetään päällä")
    on_until_task = models.TextField(null=True, blank=True)

    def revoke_task(self):
        """ This is called from save(). To avoid cycles, *do not* call self.save here. """
        if self.on_until_task:
            celery_app.control.revoke(self.on_until_task)
            self.on_until_task = None

    def save(self, *args, **kwargs):
        import tasks as milight_tasks
        if not self.on_until:
            self.revoke_task()
        else:
            old_on_until = redis_instance.get("on-until-timestamp-group-%s" % self.group_id)
            if not old_on_until:
                old_on_until = timezone.now() - datetime.timedelta(days=365)
            else:
                old_on_until = timezone.make_aware(datetime.datetime.fromtimestamp(float(old_on_until)), timezone.utc)

            if abs((self.on_until - old_on_until).total_seconds()) > 15 or timezone.now() > self.on_until or self.on_until - timezone.now() < datetime.timedelta(seconds=45):
                redis_instance.set("on-until-timestamp-group-%s" % self.group_id, self.on_until.strftime("%s"))
                self.revoke_task()
                now = timezone.now()
                if self.on_until > now:
                    # on_until is in the future. Add new task.
                    self.on_until_task = str(milight_tasks.lightgroup_on_until.apply_async((self.group_id,), eta=self.on_until + datetime.timedelta(seconds=16), expires=self.on_until + datetime.timedelta(seconds=60)))

        super(LightGroup, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.on_until_task:
            celery_app.control.revoke(self.on_until_task)

        logger.info("Deleted lightgroup")
        super(LightGroup, self).delete(*args, **kwargs)

    def __unicode__(self):
        return u"%s (%s), color: %s, on: %s, rgbw: %s, white: %s" % (self.description, self.group_id, self.color, self.on, self.rgbw_brightness, self.white_brightness)

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
    action = models.CharField(
        max_length=30, verbose_name="Sisäinen nimi toiminnolle", unique=True)
    running = models.NullBooleanField(default=True, verbose_name="Päällä")
    start_time = models.TimeField(verbose_name="Aloitusaika")
    duration = models.IntegerField(
        verbose_name="Kestoaika sekunteina")  # in seconds
    active_days = models.CharField(
        max_length=7, default="0000000", verbose_name="Päivät", help_text="ma-su, 0=pois, 1=päällä")

    turn_display_on = models.BooleanField(
        default=False, blank=True, verbose_name="Käynnistä näyttö", help_text="Käynnistä näyttö ohjelman alussa")
    turn_display_off = models.BooleanField(
        default=False, blank=True, verbose_name="Sammuta näyttö", help_text="Sammuta näyttö ohjelman lopussa")
    action_if_off = models.BooleanField(
        default=True, blank=True, verbose_name="Suorita sammutetuille", help_text="Suorita ohjelma myös sammutetuille valoille")
    set_white = models.BooleanField(
        default=False, blank=True, verbose_name="Vaihda väri valkoiseksi", help_text="Vaihda ohjelman aikana väri valkoiseksi")
    no_brighten = models.BooleanField(default=False, blank=True, verbose_name="Älä lisää valojen kirkkautta",
                                      help_text="Jos raksitettu, valojen kirkkautta ei koskaan lisätä")
    no_dimming = models.BooleanField(default=False, blank=True, verbose_name="Älä vähennä valojen kirkkautta",
                                     help_text="Jos raksitettu, valojen kirkkautta ei koskaan vähennetä")

    def __unicode__(self):
        return u"%s (%s) %s -- %s" % (self.action, self.running, self.start_time, self.duration)

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
        timestamp = (timezone.now() -
                     datetime.timedelta(seconds=duration)).time()
        return self.get_start_datetime(timestamp) + datetime.timedelta(seconds=duration)

    @property
    def end_time(self):
        return (datetime.datetime.combine(datetime.date.today(), self.start_time) + datetime.timedelta(seconds=max(self.duration, 300))).time()

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
    publish_ws("lightcontrol-timed-%s" % instance.action,
               get_serialized_timed_action(instance))


@receiver(post_save, sender=LightGroup, dispatch_uid="lightgroup_post_save")
def publish_lightgroup_saved(sender, instance, *args, **kwargs):
    publish_ws("lightcontrol", {
               "groups": get_serialized_lightgroups(), "main_buttons": get_main_buttons()})
