from __future__ import absolute_import
from info_timers.models import Timer
from celery import shared_task


@shared_task
def alarm_ending_task(timer_id):
    try:
        timer = Timer.objects.get(timer_id)
    except:
        return
    print timer
