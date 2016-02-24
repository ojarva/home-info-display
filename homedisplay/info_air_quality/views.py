from .models import OutsideAirQuality
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.views.generic import View
import datetime
import json
import numpy
import redis
import time

redis_instance = redis.StrictRedis()


class GetModalContent(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("air_quality_graphs.html", {}, context_instance=RequestContext(request))


class GetLatestSensorReadings(View):
    def get(self, request, *args, **kwargs):
        item = redis_instance.get("air-latest-%s" % kwargs["sensor_id"])
        try:
            return HttpResponse(json.dumps({"value": float(item)}), content_type="application/json")
        except (ValueError, TypeError):
            raise Http404


class GetHistoryForSensor(View):
    def get(self, request, *args, **kwargs):
        items = redis_instance.lrange("air-storage-%s" % kwargs["sensor_id"], 0, -1)
        items.reverse()
        ret = ",".join(items)
        return HttpResponse("[%s]" % ret, content_type="application/json")


class GetLatestOutdoor(View):
    def get(self, request, *args, **kwargs):
        data = {}
        now = timezone.now()
        maximum_age = datetime.timedelta(hours=6)
        types = OutsideAirQuality.objects.values_list("type", flat=True).order_by("type").distinct()
        for type in types:
            obj = OutsideAirQuality.objects.filter(type=type).latest()
            if obj:
                if now - obj.timestamp < maximum_age:
                    data[type] = {"value": float(obj.value), "timestamp": obj.timestamp.isoformat()}
        return HttpResponse(json.dumps(data), content_type="application/json")
