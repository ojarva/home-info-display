# -*- coding: utf-8 -*-

from django.utils import timezone
import datetime
import logging

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))

# TODO: move to local_settings
GROUP_TIMER_NAME_MAP = {
    1: "Tatamin valot",
    2: "Pöydän valot",
    3: "Keittiön valot",
    4: "Eteisen valot",
}


def update_group_automatic_timer(group, on_until):
    import models as timer_models

    duration = (on_until - timezone.now()).total_seconds()
    start_time = timezone.now() - datetime.timedelta(seconds=5)
    duration += 5

    timer, created = timer_models.Timer.objects.get_or_create(action="auto-lightgroup-%s" % group, defaults={
                                                              "name": GROUP_TIMER_NAME_MAP[group], "start_time": start_time, "duration": duration, "auto_remove": 0, "no_bell": True})
    if not created:
        if on_until > timer.end_time:
            timer.start_time = start_time
            timer.duration = duration
        else:
            logger.info("Did not update timer for group %s: on_until (%s) is earlier than current end time (%s)",
                        group, on_until, timer.end_time)
    logger.info("Updated timer for group %s: start_time=%s, duration=%s",
                group, start_time, duration)
    timer.save()


def delete_group_automatic_timer(group, no_actions=False):
    import models as timer_models
    try:
        timer = timer_models.Timer.objects.get(
            action="auto-lightgroup-%s" % group)
    except timer_models.Timer.DoesNotExist:
        return
    timer.delete(no_actions=no_actions)
