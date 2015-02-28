from django.core import serializers
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
import datetime
import json
import redis

redis_instance = redis.StrictRedis()

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

    auto_remove = models.IntegerField(null=True)
    no_refresh = models.BooleanField(default=False, blank=True)

    @property
    def end_time(self):
        if self.duration:
            return self.start_time + datetime.timedelta(seconds=self.duration)
        return now()

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
    redis_instance.publish("home:broadcast:generic", json.dumps({"key": "timer-labels", "content": get_labels()}))

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
