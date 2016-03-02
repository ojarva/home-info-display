from __future__ import absolute_import
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from ledcontroller import LedController
import datetime
import logging
import redis


logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))
redis_instance = redis.StrictRedis()
led = LedController(settings.MILIGHT_IP)

@shared_task
def lightgroup_on_until(group_id):
    from control_milight.models import LightGroup, update_lightstate

    group = LightGroup.objects.get(group_id=group_id)
    if not group.on_until:
        logger.info("No on_until specified for {group_id}. Cancelling task.".format(group_id=group_id))
        return

    now = timezone.now()
    if group.on_until > now:
        logger.error("Called incorrectly - on_until is in the future. Group id {group_id}".format(group_id=group_id))
        return

    logger.info("Switching off group {group_id}. Current time is {now} and on_until is {on_until}".format(group_id=group_id, now=now, on_until=group.on_until))

    if group.on:
        led.off(group_id)
        group.on_until = None
        group.on = False
        group.save()
