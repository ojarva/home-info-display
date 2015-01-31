from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.views.generic import View
from models import Timer
import json

def convert_to_timestamp(dt):
    return time.mktime(dt.timetuple())


class current_time(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(convert_to_timestamp(datetime.datetime.now()))

class list(View):
    def get(self, request, *args, **kwargs):
        items = Timer.objects.all()
        items = sorted(items, key=lambda x: x.end_time)
        for item in items:
            item.start_time = convert_to_timestamp(item.start_time)
        return HttpResponse(json.dumps(items))

class get(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.start_time = convert_to_timestamp(item.start_time)
        return HttpResponse(json.dumps(item))

class stop(View):
    #TODO: stop instead of deleting
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = False
        item.save()
        item.start_time = convert_to_timestamp(item.start_time)
        return HttpResponse(json.dumps(item))

class delete(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.delete()
        return HttpResponse(json.dumps({"deleted": True, "id": kwargs["id"]}))

class restart(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.start_time = datetime.datetime.now()
        item.save()

        item.start_time = convert_to_timestamp(item.start_time)
        return HttpResponse(json.dumps(item))

class start(View):
    #TODO: this does not handle pausing properly.
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Timer, pk=kwargs["id"])
        item.running = True
        item.save()
        item.start_time = convert_to_timestamp(item.start_time)
        return HttpResponse(json.dumps(item))


class create(View):
    def post(self, request, *args, **kwargs):
        p = request.POST
        item = Timer(name=p.get("name"), start_time=datetime.datetime.now(), duration=p.get("duration"))
        item.save()
        item.start_time = convert_to_timestamp(item.start_time)
        return HttpResponse(json.dumps(item))
