from .models import *
from .tasks import alarm_ending_task
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
import redis
import json
import time

r = redis.StrictRedis()

def convert_to_timestamp(dt):
    return time.mktime(dt.timetuple())


class GetLabels(View):
    def get(self, request, *args, **kwargs):
        items = get_labels()
        return HttpResponse(json.dumps(items), content_type="application/json")


class CurrentTime(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(int(convert_to_timestamp(now())*1000))


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
        item.stopped_at = now()
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
        item.start_time = now()
        item.save()
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Start(View):
    #TODO: this does not handle pausing properly.
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = True
        item.save()
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")


class Create(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        p = request.POST
        item = Timer(name=p.get("name"), start_time=now(), duration=int(p.get("duration")))
        item.save()
        serialized = json.loads(serializers.serialize("json", [item]))
        r.publish("home:broadcast:generic", json.dumps({"key": "timers", "content": serialized}))
        if item.duration:
            alarm_ending_task.apply_async((item.pk,), eta=item.end_time)
        return HttpResponse(serialized, content_type="application/json")
