from django.db import models
from django.db.models.signals import post_save, post_delete
from homedisplay.utils import publish_ws
from django.dispatch import receiver
from django.core import serializers
import json

class Notification(models.Model):
    class Meta:
        get_latest_by = "timestamp"
        ordering = ("-timestamp",)

    timestamp = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=20)
    description = models.TextField()
    can_dismiss = models.NullBooleanField(null=True, blank=True)

    def __unicode__(self):
        return u'%s @ %s: %s (%s)' % (self.item_type, self.timestamp, self.description, self.can_dismiss)

def publish_notifications():
    publish_ws("notifications", json.loads(serializers.serialize("json", Notification.objects.all())))

@receiver(post_save, sender=Notification, dispatch_uid="notification_post_save")
def publish_notification_saved(sender, instance, *args, **kwargs):
    publish_notifications()

@receiver(post_delete, sender=Notification, dispatch_uid="notification_post_delete")
def publish_notification_deleted(sender, instance, *args, **kwargs):
    publish_notifications()
