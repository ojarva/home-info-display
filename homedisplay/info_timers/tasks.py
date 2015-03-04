from __future__ import absolute_import
from info_timers.models import Timer
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))


@shared_task
def add_sauna_timer_task():
    timer = Timer(name="Sauna", start_time="", duration=3600)
    pass

@shared_task
def alarm_ending_task(timer_id):
    try:
        timer = Timer.objects.get(timer_id)
    except:
        logger.info("No timer object for ID %s available", timer_id)
        return "No timer object available"
    if timer.end_time > timezone.now():
        # Item has been restarted. Do not play alarms yet.
        logger.info("Timer %s did not expire yet. Time is %s, but timer end time is %s", timer_id, timer.end_time, timezone.now())
        return "Timer %s did not expire yet."
    print timer
