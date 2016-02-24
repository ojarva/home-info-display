from .models import get_labels, Timer, TIMER_ALARMS
from .tasks import alarm_ending_task, alarm_notification_task, alarm_play_until_dismissed
from celery.task.control import revoke
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import datetime
import json
import time


class GetLabels(View):
    def get(self, request, *args, **kwargs):
        items = get_labels()
        return HttpResponse(json.dumps(items), content_type="application/json")


class CurrentTime(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(int(time.time()) * 1000)


class List(View):
    def get(self, request, *args, **kwargs):
        items = Timer.objects.all()
        items = sorted(items, key=lambda x: x.end_time)
        return HttpResponse(serializers.serialize("json", items), content_type="application/json")


class Get(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Stop(View):
    def patch(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = False
        item.stopped_at = timezone.now()
        revoke_tasks(item)
        item.save()
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Delete(View):
    def delete(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        revoke_tasks(item)
        item.delete()
        return HttpResponse(json.dumps({"deleted": True, "id": kwargs["id"]}), content_type="application/json")


def revoke_tasks(timer):
    if timer.alarm_ending_task:
        revoke(timer.alarm_ending_task)
        timer.alarm_ending_task = None
    for alarm in TIMER_ALARMS:
        task_field = "alarm_%ss_task" % alarm
        if getattr(timer, task_field):
            revoke(getattr(timer, task_field))
            setattr(timer, task_field, None)
    if timer.alarm_until_dismissed_task:
        revoke(timer.alarm_until_dismissed_task)
        timer.alarm_until_dismissed_task = None

def set_timer_notifications(timer):
    revoke_tasks(timer)
    if timer.duration:
        timer.alarm_ending_task = alarm_ending_task.apply_async((timer.pk,), eta=timer.end_time+datetime.timedelta(seconds=1), expires=timer.end_time+datetime.timedelta(seconds=300)).id
    for alarm in TIMER_ALARMS:
        alarm_name = "alarm_%ss" % alarm
        if getattr(timer, alarm_name):
            setattr(timer, alarm_name + "_task", alarm_notification_task.apply_async((timer.pk,), eta=timer.end_time+datetime.timedelta(seconds=1+alarm), expires=timer.end_time+datetime.timedelta(seconds=300)+datetime.timedelta(seconds=alarm)).id)

    set_alarm_until_dismissed(timer)
    timer.save()

def set_alarm_until_dismissed(timer):
    if timer.alarm_until_dismissed_task:
        revoke(timer.alarm_until_dismissed_task)
        timer.alarm_until_dismissed_task = None

    if timer.alarm_until_dismissed:
        timer.alarm_until_dismissed_task = alarm_play_until_dismissed.apply_async((timer.pk,), eta=timer.end_time+datetime.timedelta(seconds=1), expires=timer.end_time+datetime.timedelta(seconds=300)).id


class SetBell(View):
    def patch(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.alarm_until_dismissed = not item.alarm_until_dismissed
        set_alarm_until_dismissed(item)
        item.save()
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Restart(View):
    def patch(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.start_time = timezone.now()
        item.running = True
        item.save()
        set_timer_notifications(item)
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Start(View):
    #TODO: this does not handle pausing properly.
    def patch(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = True
        item.save()
        set_timer_notifications(item)

        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Create(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        p = request.POST
        duration = p.get("duration")
        if duration:
            duration = int(duration)

        timer_data = {
            "name": p.get("name"),
            "start_time": timezone.now(),
            "duration": duration,
        }
        for alarm in TIMER_ALARMS:
            alarm_name="alarm_%ss" % alarm
            if alarm_name in p:
                if p[alarm_name] in ("true", "True", "1", "on"):
                    timer_data[alarm_name] = True

        item = Timer(**timer_data)
        item.save()
        serialized = json.loads(serializers.serialize("json", [item]))
        set_timer_notifications(item)
        return HttpResponse(serialized, content_type="application/json")
