# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import serializers
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from homedisplay.utils import publish_ws
from ledcontroller import LedController
import control_milight.models as light_models
import datetime
import json

__all__ = ["get_labels", "get_serialized_timer", "Timer", "CustomLabel", "TimedCustomLabel"]

led = LedController(settings.MILIGHT_IP)

def get_labels():
    items = {"labels": [], "timed_labels": []}
    for item in CustomLabel.objects.all():
        items["labels"].append(item.name)
    for item in TimedCustomLabel.objects.all():
        items["timed_labels"].append({"label": item.name, "duration": item.duration})
    return items

def get_serialized_timer(item):
    return json.loads(serializers.serialize("json", [item]))

class Timer(models.Model):
    name = models.CharField(max_length=30)
    start_time = models.DateTimeField()
    duration = models.IntegerField(null=True)
    running = models.NullBooleanField(default=True)
    stopped_at = models.DateTimeField(null=True)
    action = models.CharField(max_length=50, null=True)

    # Time after which timer is automatically deleted
    auto_remove = models.IntegerField(null=True)

    # Disable refresh/restart button from the UI
    no_refresh = models.BooleanField(default=False, blank=True)

    @property
    def end_time(self):
        if self.duration:
            return self.start_time + datetime.timedelta(seconds=self.duration)
        return timezone.now()

    def delete(self, *args, **kwargs):
        # TODO: handle actions here
        print "Called delete with %s, %s" % (args, kwargs)
        if self.action and self.action.startswith("auto-lightgroup-") and kwargs.get("no_actions", False) != True:
            # Automatically triggered lightgroup
            group = int(self.action.replace("auto-lightgroup-", ""))
            state = light_models.LightGroup.objects.get(group_id=group)
            if state.on_automatically:
                # Group is on automatically (vs. overridden by manual updates)
                # TODO: this should be method from control_milight.utils instead of hardcoded logic.
                led.off(group)
                light_models.update_lightstate(group, None, None, False)

        try:
            del kwargs["no_actions"]
        except KeyError:
            pass
        super(Timer, self).delete(*args, **kwargs)


    def __unicode__(self):
        return u"%s - %s (%s)" % (self.name, self.start_time, self.duration)

    class Meta:
        ordering = ("name", "start_time")
        verbose_name = "Ajastin"
        verbose_name_plural = "Ajastimet"


class CustomLabel(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = "Ajastimen teksti"
        verbose_name_plural = "Ajastimien tekstit"


class TimedCustomLabel(models.Model):
    name = models.CharField(max_length=30)
    duration = models.IntegerField()

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.duration)

    class Meta:
        ordering = ("name",)
        verbose_name = "Ajastin valmiilla ajalla"
        verbose_name_plural = "Ajastimet valmiilla ajoilla"

def publish_changes():
    publish_ws("timer-labels", get_labels())


@receiver(post_delete, sender=Timer, dispatch_uid="timer_delete_signal")
def publish_timer_deleted(sender, instance, using, **kwargs):
    publish_ws("timer-%s" % instance.pk, "delete")

@receiver(post_save, sender=Timer, dispatch_uid="timer_saved_signal")
def publish_timer_saved(sender, instance, created, *args, **kwargs):
    if created:
        publish_ws("timers", get_serialized_timer(instance))
    else:
        publish_ws("timer-%s" % instance.pk, get_serialized_timer(instance))

@receiver(post_delete, sender=CustomLabel, dispatch_uid="customlabel_delete_signal")
def publish_customlabel_deleted(sender, instance, using, **kwargs):
    publish_changes();

@receiver(post_save, sender=CustomLabel, dispatch_uid="customlabel_saved_signal")
def publish_customlabel_saved(sender, instance, *args, **kwargs):
    publish_changes()

@receiver(post_delete, sender=TimedCustomLabel, dispatch_uid="timedcustomlabel_delete_signal")
def publish_timedcustomlabel_deleted(sender, instance, using, **kwargs):
    publish_changes();

@receiver(post_save, sender=TimedCustomLabel, dispatch_uid="timedcustomlabel_saved_signal")
def publish_timedcustomlabel_saved(sender, instance, *args, **kwargs):
    publish_changes()
