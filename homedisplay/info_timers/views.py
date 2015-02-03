from .models import Timer
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
import json


def convert_to_timestamp(dt):
    return time.mktime(dt.timetuple())


class current_time(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(convert_to_timestamp(now()))

class list(View):
    def get(self, request, *args, **kwargs):
        items = Timer.objects.all()
        items = sorted(items, key=lambda x: x.end_time)
        return HttpResponse(serializers.serialize("json", items), content_type="application/json")

class get(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")

class stop(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = False
        item.stopped_at = now()
        item.save()
        message = RedisMessage('stop')
        RedisPublisher(facility='timer-%s' % item.pk, broadcast=True).publish_message(message)
        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")

class delete(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        message = RedisMessage('delete')
        RedisPublisher(facility='timer-%s' % item.pk, broadcast=True).publish_message(message)
        item.delete()

        return HttpResponse(json.dumps({"deleted": True, "id": kwargs["id"]}), content_type="application/json")

class restart(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.start_time = now()
        item.save()
        message = RedisMessage('restart')
        RedisPublisher(facility='timer-%s' % item.pk, broadcast=True).publish_message(message)

        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")

class start(View):
    #TODO: this does not handle pausing properly.
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = True
        item.save()
        message = RedisMessage('start')
        RedisPublisher(facility='timer-%s' % item.pk, broadcast=True).publish_message(message)

        return HttpResponse(serializers.serialize("json", [item]), content_type="application/json")

class create(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        p = request.POST
        item = Timer(name=p.get("name"), start_time=now(), duration=p.get("duration"))
        item.save()
        serialized = serializers.serialize("json", [item])
        message = RedisMessage('create-'+serialized)
        RedisPublisher(facility='timers', broadcast=True).publish_message(message)

        return HttpResponse(serialized, content_type="application/json")
