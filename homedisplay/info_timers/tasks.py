from __future__ import absolute_import
from celery import shared_task
from django.utils import timezone
from info_timers.models import Timer, TIMER_ALARMS
import datetime
import json
import logging
import redis
import time

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))


def play_sound(sound):
    r = redis.StrictRedis()
    r.publish("sound-notification", json.dumps({"type": sound}))

@shared_task
def alarm_ending_task(timer_id):
    try:
        timer = Timer.objects.get(id=timer_id)
    except Timer.DoesNotExist:
        logger.info("No timer object for ID %s available", timer_id)
        return "No timer object available"
    if timer.end_time > timezone.now():
        # Item has been restarted. Do not play alarms yet.
        logger.info("Timer %s did not expire yet. Time is %s, but timer end time is %s", timer_id, timer.end_time, timezone.now())
        return "Timer %s did not expire yet." % timer
    print "Processing %s" % timer

    if timer.auto_remove:
        print "Removing automatically"
        timer.delete()


@shared_task
def alarm_play_until_dismissed(timer_id):
    try:
        timer = Timer.objects.get(id=timer_id)
    except Timer.DoesNotExist:
        logger.info("No timer object for ID %s available", timer_id)
        return "No timer object available"
    if timer.end_time > timezone.now():
        # Item has been restarted. Do not play alarms yet.
        logger.info("Timer %s did not expire yet. Time is %s, but timer end time is %s", timer_id, timer.end_time, timezone.now())
        return "Timer %s did not expire yet." % timer
    if not timer.alarm_until_dismissed:
        print "Timer does not have alarm enabled - abort"
        return "Timer %s does not have alarms enabled" % timer
    print "Processing alarm for %s" % timer
    while True:
        try:
            timer = Timer.objects.get(id=timer_id)
        except Timer.DoesNotExist:
            logger.info("Timer %s has been removed" % timer_id)
            return "End-of-timer alarm finished (timer removed)"
        if timer.alarm_until_dismissed:
            play_sound("finished-important")
            time.sleep(5)
        else:
            logger.info("Timer %s does not have alarm_until_dismissed set anymore." % timer_id)
            return "End-of-timer alarm finished (exists, but alarm_until_dismissed not set)"


@shared_task
def alarm_notification_task(timer_id):
    try:
        timer = Timer.objects.get(id=timer_id)
    except Timer.DoesNotExist:
        logger.info("No timer object for ID %s available", timer_id)
        return "No timer object available"
    if timer.end_time > timezone.now():
        # Item has been restarted. Do not play alarms yet.
        logger.info("Timer %s did not expire yet. Time is %s, but timer end time is %s", timer_id, timer.end_time, timezone.now())
        return "Timer %s did not expire yet." % timer
    print "Processing alarms for %s" % timer
    for alarm in TIMER_ALARMS:
        alarm_name = "alarm_%ss" % alarm
        if getattr(timer, alarm_name):
            print "Alarm %s enabled, diff: %s" % (alarm, timezone.now() - timer.end_time)
            if timezone.now() - timer.end_time >= datetime.timedelta(seconds=alarm):
                print "Playing alarm for %s" % alarm
                play_sound("finished-important-quiet")
                setattr(timer, alarm_name, False)
                timer.save()
