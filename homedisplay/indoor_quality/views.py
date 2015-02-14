from .models import AirDataPoint, AirTimePoint
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import numpy
import redis
import time

redis_instance = redis.StrictRedis()

class get_keys(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(settings.SENSOR_MAP.keys()), content_type="application/json")

class get_modal(View):
    def get(self, request, *args, **kwargs):
        ret = {"graphs": settings.SENSOR_MAP}
        return render_to_response("air_quality_graphs.html", ret, context_instance=RequestContext(request))

class get_latest(View):
    def get(self, request, *args, **kwargs):
        item = redis_instance.get("air-latest-%s" % kwargs["sensor_id"])
        try:
            return HttpResponse(json.dumps({"value": float(item)}), content_type="application/json")
        except ValueError:
            raise Http404

class get_json(View):
    def get(self, request, *args, **kwargs):
        items = redis_instance.lrange("air-storage-%s" % kwargs["sensor_id"], 0, -1)
        items.reverse()
        ret = ",".join(items)
        return HttpResponse("[%s]" % ret, content_type="application/json")

class get_json_trend(View):
    #TODO: implement this on top of redis
    def get(self, request, *args, **kwargs):
        data = AirDataPoint.objects.filter(name=kwargs["sensor_id"]).select_related("timepoint")[0:30]
        if len(data) < 30:
            return HttpResponse(json.dumps({"status": "no_data"}), content_type="application/json")
        items = []
        timestamps = []
        for item in data:
            if item.value is None:
                continue
            items.append(float(item.value))
            timestamps.append(time.mktime(item.timepoint.timestamp.timetuple()))
        items.reverse()
        timestamps.reverse()
        timestamps = map(lambda x: x - timestamps[0], timestamps)
        items = numpy.array(items)
        timestamps = numpy.array(timestamps)
        z = numpy.polyfit(timestamps, items, 1)
        return HttpResponse(json.dumps({"delta": z[0], "base": z[1]}), content_type="application/json")
