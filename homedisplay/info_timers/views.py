from .models import *
from .tasks import alarm_ending_task
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

def convert_to_timestamp(dt):
    return time.mktime(dt.timetuple())


class GetLabels(View):
    def get(self, request, *args, **kwargs):
        items = get_labels()
        return HttpResponse(json.dumps(items), content_type="application/json")


class CurrentTime(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(int(convert_to_timestamp(timezone.now())*1000))


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
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = False
        item.stopped_at = timezone.now()
        item.save()
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Delete(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.delete()
        return HttpResponse(json.dumps({"deleted": True, "id": kwargs["id"]}), content_type="application/json")


class Restart(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.start_time = timezone.now()
        item.save()
        if item.duration:
            alarm_ending_task.apply_async((item.pk,), eta=item.end_time+datetime.timedelta(seconds=1), expires=item.end_time+datetime.timedelta(seconds=300))

        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Start(View):
    #TODO: this does not handle pausing properly.
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = True
        item.save()
        if item.duration:
            alarm_ending_task.apply_async((item.pk,), eta=item.end_time+datetime.timedelta(seconds=1), expires=item.end_time+datetime.timedelta(seconds=300))

        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Create(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        p = request.POST
        duration = p.get("duration")
        if duration:
            duration = int(duration)
        item = Timer(name=p.get("name"), start_time=timezone.now(), duration=duration)
        item.save()
        serialized = json.loads(serializers.serialize("json", [item]))
        if item.duration:
            alarm_ending_task.apply_async((item.pk,), eta=item.end_time+datetime.timedelta(seconds=1), expires=item.end_time+datetime.timedelta(seconds=300))
        return HttpResponse(serialized, content_type="application/json")
